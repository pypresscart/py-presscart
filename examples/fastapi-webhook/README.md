# Presscart webhook receiver (FastAPI + Docker)

A complete, runnable endpoint for [Presscart
webhooks](https://docs.presscart.com/getting-started/webhooks). It:

- **verifies** the `x-outpost-signature` HMAC-SHA256 (hex) signature over the
  raw body, timing-safe, **before** parsing JSON;
- **acknowledges fast** with `2xx` and processes in a background task;
- **deduplicates** redeliveries on the `x-outpost-event-id` header (deliveries
  are at-least-once);
- **routes** by the `x-outpost-topic` header (`article.status_changed`,
  `comment.*`). The event envelope is in `x-outpost-*` headers; the body is the
  event data.

See the SDK docs page [Webhooks](https://pypresscart.github.io/py-presscart/webhooks.html)
for the concepts and equivalent plain-Python / Lambda / GCP snippets.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/webhooks/presscart` | Receive a Presscart delivery |
| `GET`  | `/healthz` | Liveness probe |

## Configure

```bash
cp .env.example .env
# edit .env and paste your signing secret (Presscart webhook detail page)
```

- `PRESSCART_WEBHOOK_SECRET` (**required**) — the webhook's signing secret.
- `PRESSCART_API_TOKEN` (optional) — a read-scoped token; if set, the receiver
  hydrates the full article on `article.status_changed`. Omit to run without it.

## Run

**Docker Compose** (reads `.env`):

```bash
docker compose up --build
```

**Docker**:

```bash
docker build -t presscart-webhook .
docker run --rm -p 8000:8000 -e PRESSCART_WEBHOOK_SECRET=whsec_... presscart-webhook
```

**Local, no Docker** (via [uv](https://docs.astral.sh/uv/)):

```bash
PRESSCART_WEBHOOK_SECRET=whsec_... \
  uv run --with 'fastapi' --with 'uvicorn[standard]' uvicorn app:app --reload
```

## Test locally (without Presscart)

Sign a sample body with the same secret and POST it, putting the envelope in
headers. Use `--data-binary` so curl sends the **exact bytes** the signature
was computed over.

```bash
export PRESSCART_WEBHOOK_SECRET=whsec_test

# The body is the event data itself (here, an article.status_changed payload).
cat > /tmp/event.json <<'JSON'
{"article_id":"a-1","status":{"prefix":"published"}}
JSON

SIG=$(python - "$PRESSCART_WEBHOOK_SECRET" /tmp/event.json <<'PY'
import hashlib, hmac, sys
secret, path = sys.argv[1], sys.argv[2]
body = open(path, "rb").read()
print("v0=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest())
PY
)

curl -sS -X POST http://localhost:8000/webhooks/presscart \
  -H "content-type: application/json" \
  -H "x-outpost-signature: $SIG" \
  -H "x-outpost-topic: article.status_changed" \
  -H "x-outpost-event-id: evt_local_1" \
  --data-binary @/tmp/event.json
# -> 200 on success; a wrong/absent signature returns 401.
```

## Point Presscart at it

Presscart needs a public URL. For local development, expose port 8000 with a
tunnel (e.g. the Hookdeck CLI) and paste the generated URL — with the
`/webhooks/presscart` path — into the webhook's **Endpoint URL** in the
Presscart dashboard.

## Production notes

- **De-dupe** uses an in-memory `set`, which resets on restart and is per-worker.
  Move it to Redis or a database before running multiple workers/replicas.
- The `Dockerfile` runs **one** uvicorn worker on purpose, to keep that
  in-memory set coherent. Scale out only after externalizing de-dupe.
- Keep the request handler fast; push heavy work to a queue and process it
  asynchronously after the `2xx` ack.
