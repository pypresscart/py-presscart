# Auth

Access token introspection.

```python
client.auth  # AuthResource
```

## Methods

### `whoami()`

Verify the current API token and return its metadata.

```python
def whoami(
    *,
    as_json: bool | None = None,
) -> TokenInfo | dict
```

**HTTP** `GET /auth/token`
**Scope** any valid token
**Returns** {py:class}`~pypresscart.models.auth.TokenInfo`. Key fields:

| Field | Type | Description |
|---|---|---|
| `source` | `str` | `"api_token"` for tokens issued from the dashboard |
| `team_id` | `str` | UUID of the owning team |
| `token_type` | `"full_access"` \| `"custom"` \| `"read_only"` | See [Authentication and Scopes](authentication-and-scopes.md) |
| `scopes` | `list[str]` | Explicit scopes (empty for `full_access`) |
| `pro_pricing_enabled` | `bool` | Whether the team is on pro pricing |

**Example**

```python
info = client.auth.whoami()
print(info.team_id, info.token_type)
for scope in info.scopes:
    print("-", scope)
```

**Errors**
- `AuthenticationError` (401) — token missing, malformed, expired, or revoked.

## Recipes

### Fail fast on missing scopes

```python
REQUIRED = {"orders.create", "campaigns.update"}

info = client.auth.whoami()
missing = REQUIRED - set(info.scopes)
if info.token_type != "full_access" and missing:
    raise RuntimeError(f"token missing: {sorted(missing)}")
```

### Log token metadata on startup

```python
import logging
info = client.auth.whoami()
logging.info("presscart team=%s type=%s scopes=%s", info.team_id, info.token_type, len(info.scopes))
```
