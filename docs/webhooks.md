# Webhooks

Presscart can POST real-time events to your server when an article changes
status or when a comment is created, updated, or archived — so you can react
without polling the API.

:::{important}
`pypresscart` is an **API client**, not a web server. It does not receive
webhooks for you. This page shows how to **verify** and **handle** Presscart
deliveries in your own endpoint using only the Python standard library (plus,
optionally, the SDK to enrich a delivery). The verification helper here adds
**no dependencies** — it's `hmac` + `hashlib` + `base64`.
:::

## Available topics

| Topic | When it fires |
|---|---|
| `article.status_changed` | An article transitions to a new content status (e.g. draft submitted, revision requested, pending publishing, published). |
| `comment.created` | An article comment is created in Presscart or via the [Comments API](resource-articles.md#comments). |
| `comment.updated` | An article comment is updated. |
| `comment.archived` | An article comment is archived. |

You can also subscribe to **all events** when creating the webhook; new topics
added later are delivered automatically. Internal comments are never delivered.

Subscribe to these topics from the **Webhooks** section of the Presscart
dashboard, then reveal and copy the **signing secret** on the webhook detail
page — you'll need it to verify deliveries.

## Event payload

Every delivery is a JSON `POST` with the same envelope. Only `data` changes
shape per topic:

```json
{
  "id": "evt_01HF8...",
  "topic": "comment.created",
  "time": "2026-03-20T10:00:00.000Z",
  "metadata": { "source": "presscart.comments" },
  "data": { "...": "topic-specific" }
}
```

**`article.status_changed`** `data`:

```json
{
  "article_id": "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
  "campaign_id": "66666666-6666-6666-6666-666666666666",
  "profile_id": "22222222-2222-2222-2222-222222222222",
  "status": { "id": "4444...", "prefix": "pending-content-brief" },
  "effective_at": "2026-03-20T10:00:00.000Z",
  "changed_at": "2026-03-20T10:00:00.000Z"
}
```

Branch on `status.prefix` (a stable string), not `status.id`.

**`comment.created` / `comment.updated` / `comment.archived`** `data`:

```json
{
  "id": "ReDLZTmGOG2A",
  "content": {
    "type": "doc",
    "content": [
      { "type": "paragraph", "content": [{ "type": "text", "text": "Updated comment text." }] }
    ]
  },
  "author": { "name": "Jane Smith" },
  "created_at": "2026-03-20T10:00:00.000Z",
  "updated_at": "2026-03-20T10:05:00.000Z",
  "parent_comment_id": null
}
```

`id` is the comment reference — the same value the [Comments
API](resource-articles.md#comments) returns. For replies, `parent_comment_id`
is the parent's reference.

:::{warning}
**Webhook comment payloads are *not* the same shape as the Comments API
response.** In a webhook, `data.content` is a **rich-text document object**
(`{"type": "doc", ...}`), and `author` carries the **display name only** (no
email). The Comments API, by contrast, returns `content` as a plain string.

So do **not** parse a webhook payload with `pypresscart.Comment` — its
`content: str` field will reject the document object. Treat webhook `data` as a
plain `dict`, or define your own shape for it.
:::

## Verifying deliveries

Each delivery is signed with your webhook's **signing secret** using
HMAC-SHA256 over the raw request body, base64-encoded. Verify **before** you
parse the JSON, and reject anything that fails.

The signature is in the `x-hookdeck-signature` header. During a signing-secret
rotation a second header, `x-hookdeck-signature-2`, may also be present — the
delivery is valid if **either** header matches. (Sources: [Presscart
webhooks](https://docs.presscart.com/getting-started/webhooks), [Hookdeck
signature verification](https://hookdeck.com/docs/signature-verification).)

```python
import base64
import hashlib
import hmac


def verify_signature(
    secret: str,
    raw_body: bytes,
    signature: str | None,
    signature_2: str | None = None,
) -> bool:
    """Return True if `raw_body` was signed by Presscart with `secret`.

    HMAC-SHA256 over the raw body, base64-encoded, compared timing-safe.
    Valid if either the primary or the rotation header matches.
    """
    if not secret or not signature:
        return False
    expected = base64.b64encode(
        hmac.new(secret.encode(), raw_body, hashlib.sha256).digest()
    ).decode()
    return any(
        candidate is not None and hmac.compare_digest(expected, candidate)
        for candidate in (signature, signature_2)
    )
```

:::{note}
Sign the **raw bytes exactly as received**. If you let a framework parse and
re-serialize the body first, the bytes change and the HMAC won't match. Always
read the raw body, verify, *then* `json.loads` it.
:::

## Responding to deliveries

- **Return `2xx` fast.** Anything else is treated as a failure and retried.
  Respond within a few seconds; do heavy work *after* acknowledging.
- **Deliveries are at-least-once.** The same event can arrive more than once on
  retry — deduplicate on the envelope `id` (or, for comment events, `data.id`).
- **Failures retry automatically** with backoff; you can also replay a delivery
  from the webhook detail page.

## Examples

Each example reuses the `verify_signature` helper above. A complete, Dockerized
FastAPI version lives in
[`examples/fastapi-webhook/`](https://github.com/pypresscart/py-presscart/tree/main/examples/fastapi-webhook).

### Plain Python (`http.server`)

A zero-dependency receiver — good for understanding the flow or for a tiny
internal service.

```python
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# from the snippet above
# def verify_signature(...): ...

SECRET = os.environ["PRESSCART_WEBHOOK_SECRET"]
_seen: set[str] = set()  # swap for Redis / a DB in production


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))

        if not verify_signature(
            SECRET,
            raw,
            self.headers.get("x-hookdeck-signature"),
            self.headers.get("x-hookdeck-signature-2"),
        ):
            self.send_response(401)
            self.end_headers()
            return

        event = json.loads(raw)
        if event["id"] not in _seen:  # at-least-once -> dedupe
            _seen.add(event["id"])
            handle_event(event)  # keep fast; offload heavy work

        self.send_response(200)  # ack
        self.end_headers()
        self.wfile.write(b'{"received": true}')


def handle_event(event: dict) -> None:
    topic, data = event["topic"], event["data"]
    if topic == "article.status_changed":
        print(data["article_id"], "->", data["status"]["prefix"])
    elif topic.startswith("comment."):
        print(topic, data["id"])


if __name__ == "__main__":
    HTTPServer(("", 8000), Handler).serve_forever()
```

### AWS Lambda (Python)

Behind an API Gateway / Lambda Function URL. The one gotcha: the gateway may
**base64-encode the body** (`isBase64Encoded`), and you must HMAC the *decoded*
raw bytes.

```python
import base64
import json
import os

# def verify_signature(...): ...  # from the snippet above

SECRET = os.environ["PRESSCART_WEBHOOK_SECRET"]


def handler(event, context):
    body = event.get("body") or ""
    raw = base64.b64decode(body) if event.get("isBase64Encoded") else body.encode()

    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    if not verify_signature(
        SECRET,
        raw,
        headers.get("x-hookdeck-signature"),
        headers.get("x-hookdeck-signature-2"),
    ):
        return {"statusCode": 401, "body": "invalid signature"}

    delivery = json.loads(raw)
    # Enqueue to SQS / EventBridge for async processing, then ack immediately.
    print(delivery["topic"], delivery["id"])
    return {"statusCode": 200, "body": json.dumps({"received": True})}
```

### GCP Cloud Function (Python)

Using the Functions Framework. `request.get_data()` returns the raw bytes
before any JSON parsing.

```python
import os

import functions_framework

# def verify_signature(...): ...  # from the snippet above

SECRET = os.environ["PRESSCART_WEBHOOK_SECRET"]


@functions_framework.http
def presscart_webhook(request):
    raw = request.get_data()  # raw bytes — verify before get_json()

    if not verify_signature(
        SECRET,
        raw,
        request.headers.get("x-hookdeck-signature"),
        request.headers.get("x-hookdeck-signature-2"),
    ):
        return ("invalid signature", 401)

    event = request.get_json(silent=True) or {}
    # Publish to Pub/Sub for async work, then ack.
    print(event.get("topic"), event.get("id"))
    return ({"received": True}, 200)
```

### FastAPI

The essentials (read raw body, verify, ack fast). The full runnable app —
topic routing, background processing, dedupe, health check, Dockerfile — is in
[`examples/fastapi-webhook/`](https://github.com/pypresscart/py-presscart/tree/main/examples/fastapi-webhook).

```python
import os

from fastapi import BackgroundTasks, FastAPI, Request, Response

# def verify_signature(...): ...  # from the snippet above

SECRET = os.environ["PRESSCART_WEBHOOK_SECRET"]
app = FastAPI()


@app.post("/webhooks/presscart")
async def receive(request: Request, background: BackgroundTasks) -> Response:
    raw = await request.body()  # raw bytes — verify before parsing

    if not verify_signature(
        SECRET,
        raw,
        request.headers.get("x-hookdeck-signature"),
        request.headers.get("x-hookdeck-signature-2"),
    ):
        return Response(status_code=401)

    event = await request.json()
    background.add_task(process, event)  # do the work after acking
    return Response(status_code=200)
```

## Enriching a delivery with the SDK

Webhook payloads are intentionally lean (no emails, no full objects). When you
need more, hydrate via the API after acknowledging — for example, fetch the
full article on a status change:

```python
from pypresscart import PresscartClient

with PresscartClient(api_token="pc_...") as client:
    article = client.articles.get(data["article_id"])  # from a status_changed event
    print(article.name, article.status.prefix)
```

For comment events there is no `article_id` in the payload, so enrich from your
own mapping of comment reference → article if you need the parent article.

## Local development

Webhooks need a publicly reachable URL. For local testing:

1. Create a temporary URL with **Hookdeck Console** and paste it as your
   Presscart webhook endpoint.
2. Trigger an event (create a comment, change an article status).
3. Inspect the body, headers, your response, and retries in the console.

To deliver to a server on your machine, expose it with the **Hookdeck CLI** or
a tunnel and use the generated public URL. Keep separate webhooks for local,
staging, and production.
