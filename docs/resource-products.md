# Resource: Products

Individual products (purchasable placements), cross-outlet listings, and category counts.

```python
client.products  # ProductsResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`get`](#get) | `GET /products/{product_id}` | `products.read` |
| [`list_listings`](#list_listings) | `GET /products/listings` | `products.read` |
| [`list_categories`](#list_categories) | `GET /products/categories` | `products.read` |

---

### `get`

```python
def get(
    product_id: str,
    *,
    as_json: bool | None = None,
) -> Product | dict
```

**Example**

```python
product = client.products.get("prod_abc")
print(product.name, product.prices[0].unit_amount)
```

---

### `list_listings`

Flat listing of products across outlets, useful for a marketplace-style browse.

```python
def list_listings(
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    filters: dict | None = None,
    as_json: bool | None = None,
) -> Paginated[ProductListing] | dict
```

**`sort_by`** options: `domain_authority` (default), `domain_ranking`, `price`, `created_at`, `name`

**`filters`** (all optional):

| Key | Type | Notes |
|---|---|---|
| `search` | `str` | Free-text |
| `channel_types` | `list[str]` | e.g. `["WEBSITE", "NEWSLETTER"]` |
| `placement_types` | `list[str]` | |
| `min_price`, `max_price` | `int` | USD cents |
| `min_da`, `max_da` | `int` | Domain authority |
| `min_dr`, `max_dr` | `int` | Domain ranking |
| `min_tat`, `max_tat` | `int` | Turnaround days |
| `tags` | `list[str]` | |
| `country`, `state`, `city` | `str` | |
| `is_do_follow`, `is_indexed` | `bool` | |
| `most_popular`, `new_last_30_days` | `bool` | |
| `product_ids` | `list[str]` | Exact match |
| `disclaimer_ids` | `list[str]` | |

**Example**

```python
listings = client.products.list_listings(
    limit=50,
    sort_by="price",
    order_by="asc",
    filters={
        "channel_types": ["WEBSITE"],
        "placement_types": ["FULL_FEATURE"],
        "min_da": 40,
    },
)
for p in listings.records:
    print(p.name, p.outlet_name, p.domain_authority)
```

---

### `list_categories`

```python
def list_categories(
    *,
    as_json: bool | None = None,
) -> list[ProductCategoryCount] | list[dict]
```

Returns counts per placement type for your team's accessible catalog:

```python
for row in client.products.list_categories():
    print(row.type, row.count)
# FULL_FEATURE 142
# PRESS_RELEASE 88
# ...
```

Note: this is a **bare array** endpoint — not a `Paginated` envelope. See [Pagination](pagination.md).

## Recipes

### Cheapest high-DA outlets

```python
cheap_authority = client.products.list_listings(
    limit=25,
    sort_by="price",
    order_by="asc",
    filters={"min_da": 60, "max_price": 50000},
)
```

### Resolve product + outlet for a checkout

```python
listing = client.products.list_listings(limit=1).records[0]
product_id = listing.id
outlet_id = listing.outlet_id
```
