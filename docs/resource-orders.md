# Orders

List, read, and create checkouts.

```python
client.orders  # OrdersResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list`](#list) | `GET /orders` | `orders.lists` |
| [`get`](#get) | `GET /orders/{order_id}` | `orders.read` |
| [`create_checkout`](#create_checkout) | `POST /orders/checkout` | `orders.create` |

---

### `list`

```python
def list(
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    as_json: bool | None = None,
) -> Paginated[Order] | dict
```

**Returns** a {py:class}`~pypresscart.models.Paginated` envelope of {py:class}`~pypresscart.models.Order`.

**Example**

```python
page = client.orders.list(limit=50, sort_by="created_at", order_by="desc")
for order in page.records:
    print(order.reference_number, order.status, order.total)
```

:::{note}
Order money fields (`total`, `subtotal`, `processing_fee`, `discount`, `credits_applied`, `LineItem.price`) are returned as **floats in dollar units** — e.g. `154.5` means $154.50. This is different from product listings, which return prices in **cents**. See [Monetary units](models-reference.md#price) in the Models Reference.
:::

---

### `get`

```python
def get(
    order_id: str,
    *,
    as_json: bool | None = None,
) -> Order | dict
```

**Returns** {py:class}`~pypresscart.models.Order`.

**Example**

```python
order = client.orders.get("ord_1")
for li in order.line_items:
    print(li.name, li.quantity, li.price)
```

**Errors** — `NotFoundError` if the order doesn't exist or belongs to another team.

---

### `create_checkout`

Create a checkout order. If the order isn't already paid, the response includes a shareable `checkout_link` for guest payment.

:::{warning}
**Not yet exercised against the live API** — this creates a real order and initiates billing. See [Testing status](testing-status.md).
:::

```python
def create_checkout(
    body: CheckoutRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Order | dict
```

**Returns** {py:class}`~pypresscart.models.Order` — the created order. If not yet paid, includes a `checkout_link` URL.

**Request body** ([`CheckoutRequest`](models-reference.md#checkoutrequest)):

| Field | Type | Required | Notes |
|---|---|---|---|
| `profile_id` | `str` | ✅ | UUID of the profile placing the order |
| `line_items` | `list[CheckoutLineItem]` | ✅ | Non-empty |
| `discount` | `float` | ❌ | Defaults to 0 |

**Line item** ([`CheckoutLineItem`](models-reference.md#checkoutlineitem)):

| Field | Type | Required |
|---|---|---|
| `product_id` | `str` | ✅ |
| `quantity` | `int` | ❌ (default 1) |
| `is_add_on` | `bool` | ❌ (default `False`) |
| `linked_order_line_item_id` | `str \| None` | ❌ |

**Example (Pydantic)**

```python
from pypresscart import CheckoutLineItem, CheckoutRequest

order = client.orders.create_checkout(
    CheckoutRequest(
        profile_id="prof_abc",
        line_items=[
            CheckoutLineItem(product_id="prod_xyz", quantity=1),
        ],
    )
)
print(order.reference_number)
print(order.checkout_link)  # URL for the buyer if not paid
```

**Example (dict)**

```python
order = client.orders.create_checkout(
    {
        "profile_id": "prof_abc",
        "line_items": [
            {"product_id": "prod_xyz", "quantity": 1, "is_add_on": False}
        ],
        "discount": 0,
    }
)
```

**Errors**
- `ValidationError` (400) — missing/invalid fields. Inspect `exc.issues` for details.
- `PermissionError` (403) — token missing `orders.create`.
- `NotFoundError` (404) — `profile_id` or `product_id` references something not on your team.

## Idempotency

`POST /orders/checkout` is **not** idempotent — retrying after a timeout could double-create. `pypresscart` will retry network failures by default. For strict semantics:

```python
strict = PresscartClient(api_token="pc_...", max_retries=0)
strict.orders.create_checkout(body)
```

See [Retry and Timeouts](retry-and-timeouts.md).

## Recipes

### Place an order with an add-on

```python
order = client.orders.create_checkout(
    CheckoutRequest(
        profile_id="prof_1",
        line_items=[
            CheckoutLineItem(product_id="prod_main", quantity=1),
            CheckoutLineItem(product_id="prod_addon", quantity=1, is_add_on=True),
        ],
    )
)
```

### Poll order status

```python
import time

order_id = order.id
for _ in range(30):
    order = client.orders.get(order_id)
    if order.status in {"PAID", "FULFILLED"}:
        break
    time.sleep(5)
```

### Export paid orders for a date range

```python
from itertools import chain

def all_orders():
    page = 1
    while True:
        result = client.orders.list(page=page, limit=100)
        yield from result.records
        if result.next_page is None:
            return
        page = result.next_page

paid = [o for o in all_orders() if o.status == "PAID"]
```

See [Pagination](pagination.md) for a reusable iterator.
