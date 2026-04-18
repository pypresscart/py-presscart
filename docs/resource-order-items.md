# Order Items

Team-wide order-item reporting. For per-profile order items, see [Profiles](resource-profiles.md).

```python
client.order_items  # OrderItemsResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list`](#list) | `GET /order-items` | `orders.lists` |

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
) -> Paginated[OrderItem] | dict
```

**Returns** a {py:class}`~pypresscart.models.Paginated` envelope of {py:class}`~pypresscart.models.OrderItem`. Each item has the purchased product, the associated article and campaign (if any), outlet, commission/accounting fields, and refund status.

**Example**

```python
page = client.order_items.list(limit=50, sort_by="created_at", order_by="desc")
for oi in page.records:
    print(oi.product_name, oi.sale_price, oi.commission_status)
```

### What's visible

`internal_cost` and `reseller_price` will always be `null` on the API. Don't rely on them in your integration.

## Recipes

### Pending publisher payouts

```python
unpaid = [
    oi for oi in client.order_items.list(limit=100).records
    if not oi.is_publisher_paid and oi.commission_status != "NOT_APPLICABLE"
]
```

### Link order items back to orders

Each `OrderItem.order_id` points to the parent order. Pair with `client.orders.get(...)` to get full context:

```python
oi = client.order_items.list(limit=1).records[0]
parent = client.orders.get(oi.order_id)
print(parent.status, parent.total)
```
