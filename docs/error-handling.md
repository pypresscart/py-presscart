# Error Handling

`pypresscart` maps every HTTP error to a typed exception. You can catch the broad base class or the specific subclass.

## Hierarchy

```
PresscartError                       # base class for anything this library raises
├── PresscartAPIError                # the API returned a non-2xx response
│   ├── BadRequestError       (400)
│   │   └── ValidationError   (400 with field-level `issues`)
│   ├── AuthenticationError   (401)
│   ├── PermissionError       (403)
│   ├── NotFoundError         (404)
│   ├── RateLimitError        (429)
│   └── ServerError           (5xx)
└── PresscartTransportError          # network failures (DNS, timeout, connection reset)
```

Import from the top level:

```python
from pypresscart import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionError,
    PresscartAPIError,
    PresscartError,
    PresscartTransportError,
    RateLimitError,
    ServerError,
    ValidationError,
)
```

## What's on every `PresscartAPIError`

| Attribute | Type | Description |
|---|---|---|
| `status_code` | `int` | HTTP status (400, 401, …) |
| `name` | `str \| None` | `name` field from the API body (e.g. `"ForbiddenError"`) |
| `message` | `str` | Human-readable description |
| `payload` | `dict` | Full parsed JSON body (empty dict if the body wasn't JSON) |

Extras on specific subclasses:

- `ValidationError.issues: list[dict]` — each item has `path` and `message` for the offending field.
- `RateLimitError.retry_after: float | None` — parsed from the `Retry-After` response header.

`PresscartTransportError` wraps the underlying `requests.exceptions.RequestException` in `__cause__`.

## Basic pattern

```python
from pypresscart import NotFoundError, PresscartAPIError

try:
    campaign = client.campaigns.get("cmp_missing")
except NotFoundError:
    print("campaign does not exist")
except PresscartAPIError as exc:
    print(f"[{exc.status_code}] {exc.name}: {exc.message}")
    print("full payload:", exc.payload)
```

## Handling validation errors

The API returns `400` with a structured `issues` array when the body fails schema validation:

```python
from pypresscart import ValidationError

try:
    client.orders.create_checkout({"profile_id": "", "line_items": []})
except ValidationError as exc:
    for issue in exc.issues:
        print(f"field {issue['path']}: {issue['message']}")
```

## Rate limiting

`pypresscart` automatically retries `429` responses up to `max_retries` times, honoring `Retry-After`. If you still exhaust retries, you get `RateLimitError`:

```python
from pypresscart import RateLimitError

try:
    client.outlets.list()
except RateLimitError as exc:
    print(f"rate limited; retry after {exc.retry_after}s")
```

See [Retry and Timeouts](retry-and-timeouts.md) for tuning.

## Permission vs authentication

- **`AuthenticationError` (401)** — token missing, malformed, expired, or revoked. Re-mint the token.
- **`PermissionError` (403)** — token is valid but the requested action isn't in its scope (or crosses team boundaries). Grant the missing scope (see [Authentication and Scopes](authentication-and-scopes.md)).

```python
from pypresscart import AuthenticationError, PermissionError

try:
    client.orders.create_checkout(body)
except AuthenticationError:
    refresh_or_alert()
except PermissionError:
    print("token lacks orders.create")
```

## Network failures

```python
from pypresscart import PresscartTransportError

try:
    client.auth.whoami()
except PresscartTransportError as exc:
    # The underlying requests exception is in __cause__
    import requests
    if isinstance(exc.__cause__, requests.Timeout):
        print("timeout — retry later")
    raise
```

`PresscartTransportError` is raised only **after** retries are exhausted.

## Catch-all

If you just want "any pypresscart failure":

```python
from pypresscart import PresscartError

try:
    ...
except PresscartError as exc:
    log.exception("Presscart call failed")
```

## HTTP status → exception cheat sheet

| Status | Exception | Also retried? |
|---|---|---|
| 400 (no `issues`) | `BadRequestError` | no |
| 400 (with `issues`) | `ValidationError` | no |
| 401 | `AuthenticationError` | no |
| 403 | `PermissionError` | no |
| 404 | `NotFoundError` | no |
| 429 | `RateLimitError` | **yes** |
| 500, 502, 503, 504 | `ServerError` | **yes** |
| other 5xx | `ServerError` | no |
| non-HTTP failure | `PresscartTransportError` | **yes** (before raising) |

## Logging tips

Always log `status_code`, `name`, `message`, and `payload` for debuggability:

```python
import logging
log = logging.getLogger(__name__)

try:
    client.campaigns.create(body)
except PresscartAPIError as exc:
    log.error(
        "presscart error %d %s: %s payload=%r",
        exc.status_code, exc.name, exc.message, exc.payload,
    )
    raise
```
