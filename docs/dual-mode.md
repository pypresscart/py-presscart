# Dual-Mode I/O

`pypresscart` lets you work with **typed Pydantic models** or **plain dicts** — separately on the request and response side. This page covers the rules.

## Why

Two audiences:

- **App developers** want typed objects: autocomplete, validation, `.attribute` access.
- **Pipeline/infra code** often just forwards JSON. Materializing a Pydantic model just to `.model_dump()` it back is wasted work.

`pypresscart` serves both without a second SDK. Every resource method accepts both input shapes and can return both output shapes.

## Request side: accept either

Anywhere a method takes a request body, you can pass:

- a Pydantic model (from `pypresscart.models`)
- a plain `dict` with the equivalent JSON shape

```python
from pypresscart import CheckoutLineItem, CheckoutRequest

# Pydantic
client.orders.create_checkout(
    CheckoutRequest(
        profile_id="prof_1",
        line_items=[CheckoutLineItem(product_id="prod_1", quantity=1)],
    )
)

# Dict
client.orders.create_checkout(
    {
        "profile_id": "prof_1",
        "line_items": [
            {"product_id": "prod_1", "quantity": 1, "is_add_on": False}
        ],
    }
)
```

### Fields set to `None` are omitted, not sent as `null`

When you pass a Pydantic model, any field left as `None` is **dropped** from the JSON body rather than serialized as `null`. That usually matches what the API expects.

If an endpoint actually needs an explicit `null` — e.g. clearing a field that was previously set — pass a dict:

```python
client.campaigns.update("cmp_1", {"writing_samples": None})
```

## Response side: return either

Every read/write method accepts `as_json: bool | None = None`.

| `as_json` value | Behavior |
|---|---|
| `None` (default) | Use the client's default (`response_mode`). |
| `True` | Return a plain `dict` (or `list[dict]` for array endpoints). |
| `False` | Return a Pydantic model (or `Paginated[Model]`, `list[Model]`). |

### Client-level default

```python
client = PresscartClient(api_token="pc_...", response_mode="json")
client.auth.whoami()          # dict
client.auth.whoami(as_json=False)  # TokenInfo (per-call override)
```

### Per-call override

```python
client = PresscartClient(api_token="pc_...")  # response_mode defaults to "pydantic"

info = client.auth.whoami()              # TokenInfo
raw  = client.auth.whoami(as_json=True)  # dict
```

## Union return types

Because a single method can return either shape, the annotated return type is `Model | dict` (or `Paginated[Model] | dict`). Your type checker won't narrow automatically. Two patterns:

**Pin the mode once**, let the checker trust it:

```python
from pypresscart import Outlet

outlet = client.outlets.get("out_1")
assert isinstance(outlet, Outlet)  # narrows for the rest of the block
print(outlet.website_url)
```

**Use `typing.cast`** in library code where you know the mode:

```python
from typing import cast
from pypresscart import TokenInfo

info = cast(TokenInfo, client.auth.whoami(as_json=False))
```

## Endpoint envelope handling

Presscart uses three envelope styles. `pypresscart` hides the differences:

| Envelope | Example endpoints | Pydantic return | Dict return |
|---|---|---|---|
| Object | `GET /auth/token`, `GET /orders/{id}` | a single model | the dict |
| Paginated | `GET /outlets`, `GET /orders` | `Paginated[Model]` | the envelope dict (records + pagination keys) |
| Bare array | `GET /profiles/{id}/order-items`, `GET /products/categories` | `list[Model]` | `list[dict]` |
| Raw non-standard | `POST /campaigns/{id}/order-items`, `GET /campaigns/{id}/articles/status-count` | `dict` (always) | `dict` |

A few Presscart endpoints return shapes that don't fit cleanly into the standard envelopes. For those, `pypresscart` just returns the `dict` in both modes and documents it clearly in the method's docstring.

See [Pagination](pagination.md) for working with `Paginated[Model]`.

## Choosing a mode

Rules of thumb:

- **Prefer Pydantic** in application code. You get free validation, autocomplete, and runtime errors that point at the offending field.
- **Prefer JSON** when the next hop is JSON anyway (a task queue, a webhook, a file). Skip the round-trip through Pydantic.
- **Switch per-call** when you're mostly in one mode but need the other for a specific call (e.g., dumping a response for a logging audit).

## Round-tripping

Pydantic models round-trip losslessly to and from dicts:

```python
from pypresscart import Order

raw = client.orders.get("ord_1", as_json=True)
order = Order.model_validate(raw)          # dict → model
raw_again = order.model_dump(mode="json")  # model → dict
```

This is useful when you store the dict form (cache, queue) and want typed access later.
