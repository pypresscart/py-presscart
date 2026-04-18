# Client Configuration

`PresscartClient` is the single entry point. All behavior is configured at construction time.

```python
from pypresscart import PresscartClient

client = PresscartClient(
    api_token="pc_...",
    base_url="https://api.presscart.com",
    timeout=30.0,
    max_retries=3,
    retry_backoff_base=0.25,
    retry_backoff_max=4.0,
    retry_jitter=0.1,
    response_mode="pydantic",
    user_agent=None,
    session=None,
)
```

## Parameter reference

| Parameter | Type | Default | Description |
|---|---|---|---|
| `api_token` | `str` | *(required)* | Bearer token. Raises `ValueError` if empty. |
| `base_url` | `str` | `"https://api.presscart.com"` | API origin. Override for staging or self-hosted. |
| `timeout` | `float` | `30.0` | Per-request timeout in seconds (connect + read). |
| `max_retries` | `int` | `3` | Additional attempts on 429/5xx/network errors. `0` disables retry. |
| `retry_backoff_base` | `float` | `0.25` | Base seconds for `base * 2**attempt` backoff. |
| `retry_backoff_max` | `float` | `4.0` | Backoff cap (also caps `Retry-After`). |
| `retry_jitter` | `float` | `0.1` | Fractional random jitter added to each backoff. Set to `0.0` to disable. |
| `response_mode` | `"pydantic"` \| `"json"` | `"pydantic"` | Default return type. Overridable per call. |
| `user_agent` | `str \| None` | `"pypresscart/<version>"` | Custom `User-Agent` header. |
| `session` | `requests.Session \| None` | `None` | Inject a pre-configured session (proxies, custom adapters, etc.). |

## Base URL

Point at a different host for staging or self-hosted Presscart deployments:

```python
client = PresscartClient(
    api_token="pc_...",
    base_url="https://staging.api.presscart.com",
)
```

## Timeouts

One number applies to both connect and read. If you need fine-grained control, pass a session with a custom adapter:

```python
import requests
from requests.adapters import HTTPAdapter

sess = requests.Session()
sess.mount("https://", HTTPAdapter(pool_connections=20, pool_maxsize=50))

client = PresscartClient(api_token="pc_...", session=sess, timeout=60.0)
```

## Retries

See [Retry and Timeouts](retry-and-timeouts.md) for the full retry model. Short version:

- 429 and 5xx responses retry up to `max_retries` times.
- `Retry-After` header (if present) overrides the computed backoff.
- Network errors (timeouts, connection reset) also retry.
- 4xx non-429 responses do **not** retry — they raise immediately.

## Response mode

Default is `"pydantic"`. Switch the whole client to raw dicts:

```python
client = PresscartClient(api_token="pc_...", response_mode="json")
client.outlets.list()  # returns dict, not Paginated[OutletListing]
```

Per-call override always wins:

```python
client.outlets.list(as_json=False)  # Pydantic, regardless of client default
client.outlets.list(as_json=True)   # dict, regardless of client default
```

See [Dual-Mode I/O](dual-mode.md).

## Custom User-Agent

For apps with bot-filtering or audit requirements:

```python
client = PresscartClient(
    api_token="pc_...",
    user_agent="acme-pr-bot/2.1 (contact=ops@acme.com)",
)
```

## Injecting a `requests.Session`

Use cases:
- Corporate proxy.
- Custom retry adapter beyond what pypresscart offers.
- Shared connection pool across multiple clients.
- Request/response logging via session hooks.

```python
import requests

sess = requests.Session()
sess.proxies = {"https": "http://corp-proxy:3128"}
sess.hooks["response"].append(lambda r, *a, **kw: print(r.status_code, r.url))

client = PresscartClient(api_token="pc_...", session=sess)
```

> When you supply a session, `pypresscart` does **not** close it on `client.close()` — you own its lifecycle.

## Lifecycle

Three equivalent patterns:

```python
# Context manager (preferred)
with PresscartClient(api_token="pc_...") as client:
    client.auth.whoami()

# Explicit close
client = PresscartClient(api_token="pc_...")
try:
    client.auth.whoami()
finally:
    client.close()

# Long-lived (common in web servers) — create once, reuse
client = PresscartClient(api_token="pc_...")
# ... application lifetime ...
client.close()  # at shutdown
```

## Thread safety

The underlying `requests.Session` is thread-safe for request dispatch. Pydantic models are immutable by default. You can share a single `PresscartClient` across threads in typical usage.

For high-fanout async workflows, consider running blocking `pypresscart` calls inside `anyio.to_thread.run_sync` or `loop.run_in_executor`.

## Logging

`pypresscart` does not emit logs itself. To trace requests, use a session hook (see above) or enable `urllib3`'s logger:

```python
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
```
