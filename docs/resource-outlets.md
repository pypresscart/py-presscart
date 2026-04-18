# Outlets

Browse the marketplace of outlets (publications, newsletters, social channels) and their metadata.

```python
client.outlets  # OutletsResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list`](#list) | `GET /outlets` | `outlets.lists` |
| [`get`](#get) | `GET /outlets/{outlet_id}` | `outlets.read` |
| [`list_products`](#list_products) | `GET /outlets/{outlet_id}/products` | `outlets.read` |
| [`list_countries`](#list_countries) | `GET /outlets/locations/countries` | `outlets.read` |
| [`list_states`](#list_states) | `GET /outlets/locations/states` | `outlets.read` |
| [`list_cities`](#list_cities) | `GET /outlets/locations/cities` | `outlets.read` |
| [`list_tags`](#list_tags) | `GET /tags` | `tags.lists` |
| [`list_disclaimers`](#list_disclaimers) | `GET /outlet-disclaimers` | `outlet_disclaimers.lists` |

---

### `list`

List marketplace outlets.

```python
def list(
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    filters: dict | None = None,
    as_json: bool | None = None,
) -> Paginated[OutletListing] | dict
```

**Returns** a {py:class}`~pypresscart.models.Paginated` envelope of {py:class}`~pypresscart.models.OutletListing`. See [Pagination](pagination.md).

**`sort_by`** options: `name`, `created_at`, `domain_authority`, `domain_ranking`
**`order_by`** options: `asc`, `desc` (default `desc`)

**`filters`** (all optional):

| Key | Type | Values |
|---|---|---|
| `search` | `str` | Free-text on outlet/product name |
| `status` | `str` | `ACTIVE` (default), `INACTIVE`, `DRAFT`, `PENDING_REVIEW`, `PENDING_AGREEMENT`, `REJECTED`, `ARCHIVED`, `SUSPENDED` |
| `channel_type` | `str` | `WEBSITE`, `NEWSLETTER`, `INSTAGRAM`, `LINKEDIN`, `YOUTUBE`, `TIKTOK`, `TWITTER_X`, `PODCAST`, `OTHER` |
| `placement_type` | `str` | `FULL_FEATURE`, `PRESS_RELEASE`, `MENTION`, `QUOTE`, `LISTICLE` |
| `is_do_follow` | `bool` | |
| `is_indexed` | `bool` | |
| `disclaimer` | `str` | Disclaimer name |
| `tags` | `list[str]` | Tag names |
| `country`, `state`, `city` | `str` | |
| `pricing[min]`, `pricing[max]` | `int` | USD cents |
| `domain_authority[min]`, `domain_authority[max]` | `int` | |
| `domain_ranking[min]`, `domain_ranking[max]` | `int` | |
| `turnaround_time[min]`, `turnaround_time[max]` | `int` | Days |

**Example**

```python
page = client.outlets.list(
    limit=50,
    sort_by="domain_authority",
    order_by="desc",
    filters={
        "country": "United States",
        "channel_type": "WEBSITE",
        "is_do_follow": True,
        "pricing[max]": 50000,  # cents
    },
)

for row in page.records:
    print(f"{row.outlet_name:40}  ${row.prices[0].unit_amount/100:>7.2f}")
```

> Note: in the listing response, `id` is a **product id** (what you pass to `orders.create_checkout`). The outlet id is `outlet_id`.

---

### `get`

Fetch a single outlet with its channels.

```python
def get(
    outlet_id: str,
    *,
    as_json: bool | None = None,
) -> Outlet | dict
```

**Returns** {py:class}`~pypresscart.models.Outlet`.

**Example**

```python
outlet = client.outlets.get("out_123")
for ch in outlet.outlet_channels:
    print(ch.channel_type, ch.placement_type, ch.domain_authority)
```

**Errors** — `NotFoundError` if the outlet doesn't exist or is on another team.

---

### `list_products`

Products for a single outlet. Same filter/sort shape as `list`, but scoped to one outlet.

```python
def list_products(
    outlet_id: str,
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    filters: dict | None = None,
    as_json: bool | None = None,
) -> Paginated[OutletListing] | dict
```

**Returns** a {py:class}`~pypresscart.models.Paginated` envelope of {py:class}`~pypresscart.models.OutletListing`.

---

### `list_countries`

```python
def list_countries(
    *,
    country: str | None = None,
    as_json: bool | None = None,
) -> CountriesResponse | dict
```

**Returns** {py:class}`~pypresscart.models.CountriesResponse` — a wrapper around `{"countries": [...]}`.

---

### `list_states`

```python
def list_states(
    *,
    country: str | None = None,
    as_json: bool | None = None,
) -> StatesResponse | dict
```

**Returns** {py:class}`~pypresscart.models.StatesResponse` — a wrapper around `{"states": [...]}`. Pass `country` to scope states to one country.

---

### `list_cities`

```python
def list_cities(
    *,
    country: str | None = None,
    state: str | None = None,
    as_json: bool | None = None,
) -> CitiesResponse | dict
```

**Returns** {py:class}`~pypresscart.models.CitiesResponse` — a wrapper around `{"cities": [...]}`.

---

### `list_tags`

```python
def list_tags(
    *,
    limit: int = 25,
    page: int = 1,
    filters: dict | None = None,
    as_json: bool | None = None,
) -> Paginated[Tag] | dict
```

**Returns** a {py:class}`~pypresscart.models.Paginated` envelope of {py:class}`~pypresscart.models.Tag`.

**`filters`**:

| Key | Type | Values |
|---|---|---|
| `search` | `str` | Partial match on tag name |
| `category` | `str` | `TOPIC`, `AUDIENCE`, `LOCATION`, `ROLE`, `COMPANY_SIZE` |
| `fetch_all` | `str` | `"true"` to bypass pagination |

---

### `list_disclaimers`

```python
def list_disclaimers(
    *,
    limit: int = 25,
    page: int = 1,
    filters: dict | None = None,
    as_json: bool | None = None,
) -> Paginated[DisclaimerRecord] | dict
```

**Returns** a {py:class}`~pypresscart.models.Paginated` envelope of {py:class}`~pypresscart.models.DisclaimerRecord`. Use `filters={"fetch_all": "true"}` to get them all at once.

## Recipes

### Find the top 10 US outlets by DA

```python
top = client.outlets.list(
    limit=10,
    sort_by="domain_authority",
    order_by="desc",
    filters={"country": "United States"},
)
for o in top.records:
    print(o.outlet_name, o.channels[0].domain_authority)
```

### Budget filter

```python
affordable = client.outlets.list(
    filters={"pricing[min]": 5000, "pricing[max]": 25000}  # $50–$250
)
```
