# Webhooks

Presscart can POST real-time events to your server when an article changes
status or when a comment is created, updated, or archived — so you can react
without polling the API.

:::{important}
`pypresscart` is an **API client**, not a web server. It does not receive
webhooks for you. This page shows how to **verify** and **handle** Presscart
deliveries in your own endpoint using only the Python standard library (plus,
optionally, the SDK to enrich a delivery). The verification helper here adds
**no dependencies** — it's `hmac` + `hashlib`.
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

## Delivery format

Each delivery is a JSON `POST`. The **event envelope is carried in request
headers**, and the **request body is the event data** for the topic:

| Header | Description |
|---|---|
| `x-outpost-event-id` | Unique delivery id. **Deduplicate on this.** |
| `x-outpost-topic` | Event topic, e.g. `comment.created`. **Route on this.** |
| `x-outpost-timestamp` | Delivery timestamp (use for optional replay protection). |
| `x-outpost-source` | Event source. |
| `x-outpost-signature` | HMAC signature over the raw body — see [Verifying deliveries](#verifying-deliveries). |

A `comment.created` delivery, for example:

```text
POST /webhooks/presscart HTTP/1.1
content-type: application/json
x-outpost-event-id: evt_01HF8...
x-outpost-topic: comment.created
x-outpost-timestamp: 2026-03-20T10:00:00.000Z
x-outpost-source: presscart.comments
x-outpost-signature: v0=2f8a...c1

{
  "id": "ReDLZTmGOG2A",
  "content": { "type": "doc", "content": [ ... ] },
  "author": { "name": "Jane Smith" },
  "created_at": "2026-03-20T10:00:00.000Z",
  "updated_at": "2026-03-20T10:05:00.000Z",
  "parent_comment_id": null
}
```

### Body shapes

**`article.status_changed`**:

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

**`comment.created` / `comment.updated` / `comment.archived`**:

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
**Webhook comment bodies are *not* the same shape as the Comments API
response.** In a webhook, `content` is a **rich-text document object**
(`{"type": "doc", ...}`), and `author` carries the **display name only** (no
email). The Comments API, by contrast, returns `content` as a plain string.

So do **not** parse a webhook body with `pypresscart.Comment` — its
`content: str` field will reject the document object. Treat the body as a plain
`dict`, or define your own shape for it.
:::

## Verifying deliveries

Each delivery is signed with your webhook's **signing secret** using
HMAC-SHA256 over the **raw request body**, hex-encoded. Verify **before** you
parse the JSON, and reject anything that fails.

The signature is in the `x-outpost-signature` header, formatted `v0=<hex>`.
During a signing-secret rotation the header may carry several comma-separated
signatures (`v0=<sig1>,<sig2>`) — the delivery is valid if **any** of them
matches. (Reference: Outpost webhook destination spec, *Signatures → Default
Mode*: <https://hookdeck.com/docs/outpost/destinations/webhook>.)

```python
import hashlib
import hmac


def verify_signature(secret: str, raw_body: bytes, signature_header: str | None) -> bool:
    """Return True if `raw_body` was signed by Presscart with `secret`.

    HMAC-SHA256 over the raw body, hex-encoded, compared timing-safe. The
    `x-outpost-signature` header is `v0=<hex>`; during a secret rotation it may
    carry several comma-separated signatures, and any match is valid.
    """
    if not secret or not signature_header:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    for part in signature_header.split(","):
        candidate = part.strip().removeprefix("v0=")
        if candidate and hmac.compare_digest(expected, candidate):
            return True
    return False
```

:::{note}
Sign the **raw bytes exactly as received**. If you let a framework parse and
re-serialize the body first, the bytes change and the HMAC won't match. Always
read the raw body, verify, *then* `json.loads` it. Optionally, reject
deliveries whose `x-outpost-timestamp` is too old to blunt replay attacks.
:::

## Responding to deliveries

- **Return `2xx` fast.** Anything else is treated as a failure and retried.
  Respond within a few seconds; do heavy work *after* acknowledging.
- **Deliveries are at-least-once.** The same event can arrive more than once on
  retry — deduplicate on the `x-outpost-event-id` header.
- **Failures retry automatically** with backoff; you can also replay a delivery
  from the webhook detail page.

## Examples

Each example reuses the `verify_signature` helper above and reads the topic /
event id from headers. A complete, Dockerized FastAPI version lives in
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

        if not verify_signature(SECRET, raw, self.headers.get("x-outpost-signature")):
            self.send_response(401)
            self.end_headers()
            return

        event_id = self.headers.get("x-outpost-event-id", "")
        topic = self.headers.get("x-outpost-topic", "")
        data = json.loads(raw)  # the body IS the event data

        if event_id not in _seen:  # at-least-once -> dedupe on the event id
            _seen.add(event_id)
            handle_event(topic, data)  # keep fast; offload heavy work

        self.send_response(200)  # ack
        self.end_headers()
        self.wfile.write(b'{"received": true}')


def handle_event(topic: str, data: dict) -> None:
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
    if not verify_signature(SECRET, raw, headers.get("x-outpost-signature")):
        return {"statusCode": 401, "body": "invalid signature"}

    topic = headers.get("x-outpost-topic", "")
    event_id = headers.get("x-outpost-event-id", "")
    data = json.loads(raw)  # body is the event data
    # Enqueue to SQS / EventBridge for async processing, then ack immediately.
    print(topic, event_id)
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
    raw = request.get_data()  # raw bytes -- verify before get_json()

    if not verify_signature(SECRET, raw, request.headers.get("x-outpost-signature")):
        return ("invalid signature", 401)

    topic = request.headers.get("x-outpost-topic", "")
    data = request.get_json(silent=True) or {}  # body is the event data
    # Publish to Pub/Sub for async work, then ack.
    print(topic, request.headers.get("x-outpost-event-id"))
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
    raw = await request.body()  # raw bytes -- verify before parsing

    if not verify_signature(SECRET, raw, request.headers.get("x-outpost-signature")):
        return Response(status_code=401)

    topic = request.headers.get("x-outpost-topic", "")
    data = await request.json()  # body is the event data
    background.add_task(process, topic, data)  # do the work after acking
    return Response(status_code=200)
```

## Enriching a delivery with the SDK

Webhook bodies are intentionally lean (no emails, no full objects). When you
need more, hydrate via the API after acknowledging — for example, fetch the
full article on a status change (its `article_id` is in the body):

```python
from pypresscart import PresscartClient

with PresscartClient(api_token="pc_...") as client:
    article = client.articles.get(data["article_id"])  # from a status_changed body
    print(article.name, article.status.prefix)
```

For comment events there is no `article_id` in the body, so enrich from your
own mapping of comment reference → article if you need the parent article.

## Local development

Webhooks need a publicly reachable URL. For local testing, expose your server
with a tunnel (e.g. the Hookdeck CLI or ngrok) and paste the generated public
URL — including your endpoint path — into the webhook's **Endpoint URL** in the
Presscart dashboard. Trigger an event (create a comment, change an article
status) and inspect the request, your response, and any retries. Keep separate
webhooks for local, staging, and production.
