# Retry and Timeouts

`pypresscart` retries transient failures with exponential backoff + jitter. This page covers the retry model, what's retryable, and how to tune it.

## What gets retried

| Condition | Retried? | Why |
|---|---|---|
| `429 Too Many Requests` | ✅ | Rate limited — back off and retry |
| `500 Internal Server Error` | ✅ | Possibly transient |
| `502 Bad Gateway` | ✅ | Edge/upstream flap |
| `503 Service Unavailable` | ✅ | Server asking for a break |
| `504 Gateway Timeout` | ✅ | Transient upstream slowness |
| Other 5xx (e.g. 501, 505) | ❌ | Not expected to be transient |
| `400 / 401 / 403 / 404` | ❌ | Your payload/token/resource — won't fix itself |
| Network errors (timeout, connection reset, DNS failures) | ✅ | Often transient |

Everything else raises immediately.

## Backoff formula

```
delay = min(retry_backoff_max, retry_backoff_base * (2 ** attempt))
if jitter > 0:
    delay += delay * jitter * random()
```

Where `attempt` is 0-indexed (0 for the first retry).

With defaults (`base=0.25`, `max=4.0`, `jitter=0.1`), you get approximately:

| Attempt | Target delay | With +10% jitter |
|---|---|---|
| 0 | 0.25s | 0.25–0.275s |
| 1 | 0.50s | 0.50–0.55s |
| 2 | 1.00s | 1.00–1.10s |
| 3 | 2.00s | 2.00–2.20s |
| 4+ | 4.00s (cap) | 4.00–4.40s |

## `Retry-After` handling

If the server returns `Retry-After` on a 429 or 5xx, the library uses that value (capped by `retry_backoff_max`) instead of the computed delay. Both integer-seconds and HTTP-date formats are accepted — the library parses seconds; unparseable values fall back to the computed delay.

## Attempt count

`max_retries` is **additional attempts beyond the first**. The total request count is `max_retries + 1`.

```python
client = PresscartClient(api_token="pc_...", max_retries=3)
# First try + 3 retries = up to 4 requests.
```

## Disabling retry

For deterministic tests or scripts that must fail fast:

```python
client = PresscartClient(api_token="pc_...", max_retries=0)
```

## Aggressive retry for batch jobs

```python
client = PresscartClient(
    api_token="pc_...",
    max_retries=8,
    retry_backoff_base=0.5,
    retry_backoff_max=30.0,
    retry_jitter=0.2,
)
```

Total worst-case wait: ~`min(sum(0.5 * 2**i), cap) for i in range(8)` ≈ 60–90s of backoff for a single call.

## Timeouts

`timeout` applies to each individual attempt (not the total elapsed time across retries). A request that retries 3× with a 30s timeout can take up to ~90s + backoff.

For strict end-to-end deadlines, wrap the call:

```python
import time
from pypresscart import PresscartError

deadline = time.monotonic() + 60
try:
    result = client.orders.list()
except PresscartError:
    if time.monotonic() > deadline:
        raise TimeoutError("exceeded deadline")
    raise
```

Or enforce via an external watchdog (signal alarm, anyio cancel scope, etc.).

## Idempotency

Presscart's API is:

- **Idempotent for GET, DELETE, PUT, PATCH** — safe to retry.
- **Not idempotent for POST** — retrying a `POST /orders/checkout` after a network timeout could double-create an order.

`pypresscart` retries network failures on all methods, including POST. If you need stricter POST semantics, set `max_retries=0` for those calls specifically — build a second "idempotent-only" client:

```python
strict_client = PresscartClient(api_token="pc_...", max_retries=0)
strict_client.orders.create_checkout(body)  # no retries
```

## Observing retries

`pypresscart` doesn't emit retry events. To see them, attach a session hook:

```python
import requests

sess = requests.Session()
sess.hooks["response"].append(
    lambda r, *a, **kw: print(f"{r.status_code} {r.request.method} {r.url}")
)
client = PresscartClient(api_token="pc_...", session=sess)
```

Every retried attempt fires the hook, so you'll see repeated log lines for a 429 storm.

## Related

- [Error Handling](error-handling.md) — what's raised when retries exhaust
- [Client Configuration](client-configuration.md) — full parameter list
