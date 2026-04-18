# Getting Started

Make your first Presscart API call in under a minute.

## 1. Install

```bash
uv add pypresscart
```

See [Installation](installation.md) for alternatives.

## 2. Get an API token

Create a token in your Presscart dashboard. Tokens look like `pc_xxxx_xxxxxxx_xxxxxxxx_xxxxxxxx`. Store it in an environment variable — **never** hardcode it:

```bash
export PRESSCART_API_TOKEN="pc_..."
```

For the full matrix of token types and scopes, see [Authentication and Scopes](authentication-and-scopes.md).

## 3. Verify the token

```python
import os
from pypresscart import PresscartClient

client = PresscartClient(api_token=os.environ["PRESSCART_API_TOKEN"])

info = client.auth.whoami()
print(info.team_id, info.token_type, info.scopes)
```

If the token is bad, you'll get an `AuthenticationError` (HTTP 401). If it's missing a required scope for a later call, you'll get a `PermissionError` (HTTP 403). See [Error Handling](error-handling.md).

## 4. Browse outlets

```python
page = client.outlets.list(limit=5)
for outlet in page.records:
    print(f"{outlet.outlet_name:30}  DA={outlet.channels[0].domain_authority}")
```

`page.records` is a list of typed [`OutletListing`](resource-outlets.md) models. `page.total_records`, `page.next_page`, etc. describe the full result set. See [Pagination](pagination.md).

## 5. Place an order

```python
from pypresscart import CheckoutLineItem, CheckoutRequest

order = client.orders.create_checkout(
    CheckoutRequest(
        profile_id="YOUR_PROFILE_ID",
        line_items=[
            CheckoutLineItem(product_id="YOUR_PRODUCT_ID", quantity=1)
        ],
    )
)
print(order.reference_number, order.checkout_link)
```

The same call works with a raw `dict` if you prefer:

```python
order = client.orders.create_checkout(
    {
        "profile_id": "YOUR_PROFILE_ID",
        "line_items": [
            {"product_id": "YOUR_PRODUCT_ID", "quantity": 1, "is_add_on": False}
        ],
        "discount": 0,
    },
    as_json=True,  # returns a dict instead of an Order model
)
print(order["reference_number"])
```

Read [Dual-Mode I/O](dual-mode.md) for the full story on request/response modes.

## 6. Clean up

`PresscartClient` manages a `requests.Session`. Close it with `client.close()` or (better) use it as a context manager:

```python
with PresscartClient(api_token="pc_...") as client:
    ...
# session closed automatically
```

## Next steps

- **Configure the client**: timeouts, retries, JSON mode — [Client Configuration](client-configuration.md)
- **Handle errors**: [Error Handling](error-handling.md)
- **Explore resources**: start with [Outlets](resource-outlets.md) or [Campaigns](resource-campaigns.md)
- **See recipes**: [Recipes](recipes.md) has common end-to-end workflows
