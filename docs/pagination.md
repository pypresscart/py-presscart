# Pagination

Presscart's list endpoints use a uniform envelope. `pypresscart` models it as `Paginated[T]`.

## The envelope

```python
from pypresscart import Paginated, OutletListing

page: Paginated[OutletListing] = client.outlets.list(limit=25, page=1)

page.records         # list[OutletListing]
page.total_records   # int  — total across all pages
page.total_pages     # int
page.current_page    # int  — 1-indexed
page.next_page       # int | None — None on the last page
page.previous_page   # int | None — None on the first page
```

## Common query parameters

Every paginated endpoint in `pypresscart` accepts at least:

| Param | Default | Notes |
|---|---|---|
| `limit` | `25` | Items per page |
| `page` | `1` | 1-indexed page number |
| `sort_by` | varies | Field name (see endpoint docs) |
| `order_by` | `"desc"` | `"asc"` or `"desc"` |

Many endpoints also accept a `filters=` dict — see [Resource: Outlets](resource-outlets.md) for a filter-rich example.

## Iterating all pages

There's no built-in paginator today. Page manually:

```python
def all_records(endpoint_callable, **kwargs):
    page = 1
    while True:
        result = endpoint_callable(page=page, **kwargs)
        yield from result.records
        if result.next_page is None:
            return
        page = result.next_page

for outlet in all_records(client.outlets.list, limit=100, filters={"country": "United States"}):
    print(outlet.outlet_name)
```

## Paginated vs bare-array endpoints

A few endpoints return a naked JSON array instead of the paginated envelope. `pypresscart` returns `list[Model]` for those, not `Paginated[Model]`:

| Endpoint | Return type |
|---|---|
| `GET /profiles/{id}/order-items` | `list[ProfileOrderItem]` |
| `GET /products/categories` | `list[ProductCategoryCount]` |
| `GET /outlets/locations/countries` | `CountriesResponse` (wrapped `{"countries": [...]}`) |
| `GET /outlets/locations/states` | `StatesResponse` |
| `GET /outlets/locations/cities` | `CitiesResponse` |

Check each resource page for the exact return type.

## JSON mode

With `as_json=True` (or `response_mode="json"`), `Paginated[T]` collapses to the raw envelope dict:

```python
raw = client.outlets.list(as_json=True)
raw["records"]        # list of dicts
raw["next_page"]      # int | None
```

See [Dual-Mode I/O](dual-mode.md).

## Tips

- **Start with `limit=100`** rather than the default of 25 if you're reading a lot.
- **Use `total_pages`** to plan work before iterating (e.g., for a progress bar).
- **Server may cap `limit`** — check the returned `records` length rather than trusting your requested limit.
- **Stable ordering matters.** If you're crawling pages over time, sort by a monotonic field (e.g. `created_at`) to avoid skips or duplicates when rows change under you.
