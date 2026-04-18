# Authentication and Scopes

All Presscart API traffic uses bearer-token auth. `pypresscart` handles the header automatically — you just pass the token to the client.

```python
client = PresscartClient(api_token="pc_...")
```

The library sets:

```
Authorization: Bearer pc_...
Accept: application/json
User-Agent: pypresscart/<version>
```

You can override the `User-Agent` via `PresscartClient(..., user_agent="my-app/1.0")`. See [Client Configuration](client-configuration.md).

## Token format

- Tokens are prefixed with `pc_`.
- The raw token is only shown at creation/regeneration time — store it securely.
- Tokens are stored hashed server-side.

## Token types

| Type | Behavior |
|---|---|
| `full_access` | Bypasses scope checks. Can call any API-token route. |
| `custom` | Only the explicit scopes on the token. Most common. |
| `read_only` | Can `GET`/`LIST` on its scopes but cannot write. |

`client.auth.whoami()` returns the current token's type in `.token_type`. See [Resource: Auth](resource-auth.md).

## Scopes

Scopes gate endpoint access. If a call returns HTTP 403, the token is valid but missing the scope — `pypresscart` raises `PermissionError`. See [Error Handling](error-handling.md).

| Scope | Routes |
|---|---|
| `outlets.lists` | `GET /outlets` |
| `outlets.read` | `GET /outlets/{outlet_id}`, `GET /outlets/{id}/products`, `GET /outlets/locations/*` |
| `tags.lists` | `GET /tags` |
| `outlet_disclaimers.lists` | `GET /outlet-disclaimers` |
| `products.read` | `GET /products/{product_id}`, `GET /products/listings`, `GET /products/categories` |
| `orders.lists` | `GET /orders`, `GET /order-items`, `GET /profiles/{id}/orders`, `GET /profiles/{id}/order-items` |
| `orders.read` | `GET /orders/{order_id}` |
| `orders.create` | `POST /orders/checkout` |
| `profiles.lists` | `GET /teams/{team_id}/profiles` |
| `campaigns.lists` | `GET /campaigns`, `GET /profiles/{id}/campaigns` |
| `campaigns.read` | `GET /campaigns/{id}`, `GET /campaigns/{id}/articles`, `GET /campaigns/{id}/articles/status-count` |
| `campaigns.create` | `POST /campaigns` |
| `campaigns.update` | `PUT /campaigns/{id}`, `POST /campaigns/{id}/order-items`, `POST /questionnaires/{id}/link` |
| `files.lists` | `GET /files` |
| `files.read` | `GET /files/{id}`, `GET /files/{id}/download` |
| `files.create` | `POST /files/upload` |
| `files.update` | `POST /files/move` |
| `files.delete` | `DELETE /files/{id}` |
| `folders.lists` | `GET /folders` |
| `folders.create` | `POST /folders` |
| `folders.update` | `PATCH /folders/{id}` |
| `folders.delete` | `DELETE /folders/{id}` |

Every resource method in `pypresscart` documents its required scope in the docstring:

```python
help(client.campaigns.create)
# Create a campaign. Required scope: `campaigns.create`.
```

## Defensive checks

Verify scopes before launching a workflow:

```python
REQUIRED = {"outlets.lists", "orders.create", "campaigns.update"}

info = client.auth.whoami()
missing = REQUIRED - set(info.scopes)
if info.token_type != "full_access" and missing:
    raise RuntimeError(f"token is missing scopes: {sorted(missing)}")
```

## Rotation

When you rotate a token, instantiate a new client. Tokens aren't mutable on an existing `PresscartClient`.

```python
client = PresscartClient(api_token=new_token)
```

## Environment loading

A common pattern:

```python
import os
from pypresscart import PresscartClient

token = os.environ.get("PRESSCART_API_TOKEN")
if not token:
    raise SystemExit("PRESSCART_API_TOKEN is not set")

client = PresscartClient(api_token=token)
```

For `.env` files, use `python-dotenv` (not a runtime dep of `pypresscart`).
