"""Presscart webhook receiver -- FastAPI + Docker.

A complete, runnable endpoint for Presscart webhook deliveries that:

* verifies the ``x-hookdeck-signature`` HMAC-SHA256 (base64) signature over the
  raw request body, timing-safe, BEFORE parsing any JSON;
* acknowledges with a fast ``2xx`` and offloads work to a background task;
* deduplicates redeliveries on the envelope ``id`` (deliveries are at-least-once);
* routes by ``topic`` (article.status_changed, comment.created/updated/archived).

Run locally:

    PRESSCART_WEBHOOK_SECRET=whsec_... uv run --with 'fastapi' --with 'uvicorn[standard]' \\
        uvicorn app:app --reload

Or with Docker -- see README.md.

References:
* Presscart webhooks: https://docs.presscart.com/getting-started/webhooks
* Hookdeck signatures: https://hookdeck.com/docs/signature-verification
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os

from fastapi import BackgroundTasks, FastAPI, Request, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("presscart.webhook")

SECRET = os.environ.get("PRESSCART_WEBHOOK_SECRET", "")

app = FastAPI(title="Presscart webhook receiver")

# In-memory de-dupe set. Replace with Redis or a database in production so the
# guarantee survives restarts and is shared across multiple workers.
_processed: set[str] = set()


def verify_signature(
    secret: str,
    raw_body: bytes,
    signature: str | None,
    signature_2: str | None = None,
) -> bool:
    """Return True when ``raw_body`` was signed by Presscart with ``secret``.

    HMAC-SHA256 over the raw body, base64-encoded, compared timing-safe.
    During a signing-secret rotation an ``x-hookdeck-signature-2`` header may
    also be present; the delivery is valid if EITHER signature matches.
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


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness probe."""
    return {"status": "ok"}


@app.post("/webhooks/presscart")
async def receive(request: Request, background: BackgroundTasks) -> Response:
    """Verify, de-dupe, and acknowledge a Presscart delivery."""
    raw = await request.body()  # raw bytes: verify BEFORE parsing JSON

    if not verify_signature(
        SECRET,
        raw,
        request.headers.get("x-hookdeck-signature"),
        request.headers.get("x-hookdeck-signature-2"),
    ):
        logger.warning("rejected delivery: missing or invalid signature")
        return Response(status_code=401)

    event = json.loads(raw)
    event_id = event.get("id", "")

    # At-least-once delivery: the same event may arrive more than once.
    if event_id and event_id in _processed:
        return Response(status_code=200)  # already handled: ack and move on
    if event_id:
        _processed.add(event_id)

    # Acknowledge fast; do the real work after responding.
    background.add_task(handle_event, event)
    return Response(status_code=200)


def handle_event(event: dict) -> None:
    """Process a verified delivery. Runs after the 2xx ack."""
    topic = event.get("topic", "")
    data = event.get("data", {})

    if topic == "article.status_changed":
        logger.info(
            "article %s -> %s",
            data.get("article_id"),
            (data.get("status") or {}).get("prefix"),
        )
        _maybe_enrich_article(data.get("article_id"))
    elif topic.startswith("comment."):
        # NOTE: webhook `data.content` is a rich-text document object, not the
        # plain string the Comments API returns. Do not parse it with
        # pypresscart.Comment.
        logger.info("%s: comment %s", topic, data.get("id"))
    else:
        logger.info("unhandled topic %s (event %s)", topic, event.get("id"))


def _maybe_enrich_article(article_id: str | None) -> None:
    """Optionally hydrate the full article via the SDK.

    Webhook payloads are intentionally lean. If a read-scoped API token is set
    in ``PRESSCART_API_TOKEN`` we fetch the full object; otherwise this no-ops,
    so the example runs out of the box without a token.
    """
    token = os.environ.get("PRESSCART_API_TOKEN")
    if not token or not article_id:
        return
    try:
        from pypresscart import PresscartClient

        with PresscartClient(api_token=token) as client:
            article = client.articles.get(article_id)
            logger.info("enriched article %s: %s", article_id, getattr(article, "name", None))
    except Exception:  # best-effort enrichment; never break the ack path
        logger.exception("failed to enrich article %s", article_id)
