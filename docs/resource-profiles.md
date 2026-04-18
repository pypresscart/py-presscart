# Profiles

A **profile** is the brand/entity being promoted. Orders, campaigns, and articles all belong to a profile.

```python
client.profiles  # ProfilesResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list_team_profiles`](#list_team_profiles) | `GET /teams/{team_id}/profiles` | `profiles.lists` |
| [`list_orders`](#list_orders) | `GET /profiles/{profile_id}/orders` | `orders.lists` |
| [`list_order_items`](#list_order_items) | `GET /profiles/{profile_id}/order-items` | `orders.lists` |
| [`list_campaigns`](#list_campaigns) | `GET /profiles/{profile_id}/campaigns` | `campaigns.lists` |

---

### `list_team_profiles`

List every profile on the given team. The `team_id` must match your token's team (you can get it from `client.auth.whoami().team_id`).

```python
def list_team_profiles(
    team_id: str,
    *,
    limit: int = 25,
    page: int = 1,
    as_json: bool | None = None,
) -> Paginated[Profile] | dict
```

**Example**

```python
me = client.auth.whoami()
page = client.profiles.list_team_profiles(me.team_id)
for profile in page.records:
    print(profile.name, profile.website_url)
```

---

### `list_orders`

Orders scoped to one profile, with date filters.

```python
def list_orders(
    profile_id: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    paid_orders_only: bool | None = None,
    limit: int = 25,
    page: int = 1,
    as_json: bool | None = None,
) -> Paginated[Order] | dict
```

**`start_date`** / **`end_date`** — ISO-8601 date strings (e.g. `"2025-01-01"` or full timestamps).

**Example**

```python
page = client.profiles.list_orders(
    "prof_1",
    start_date="2025-01-01",
    end_date="2025-06-30",
    paid_orders_only=True,
)
```

---

### `list_order_items`

Order items for a single profile. **This endpoint returns a bare JSON array** — not the paginated envelope.

```python
def list_order_items(
    profile_id: str,
    *,
    type: str | None = None,
    is_add_on: bool | None = None,
    search: str | None = None,
    aggregate_add_ons: bool | None = None,
    as_json: bool | None = None,
) -> list[ProfileOrderItem] | list[dict]
```

**Example**

```python
items = client.profiles.list_order_items("prof_1", is_add_on=False)
for item in items:
    print(item.name, item.outlet.name)
```

Note: returns `list[ProfileOrderItem]`, not `Paginated[...]`. See [Pagination](pagination.md).

---

### `list_campaigns`

```python
def list_campaigns(
    profile_id: str,
    *,
    limit: int = 25,
    page: int = 1,
    as_json: bool | None = None,
) -> Paginated[Campaign] | dict
```

## Recipes

### Dashboard per profile

```python
me = client.auth.whoami()
profiles = client.profiles.list_team_profiles(me.team_id, limit=100)

for p in profiles.records:
    orders = client.profiles.list_orders(p.id, paid_orders_only=True, limit=100)
    camps = client.profiles.list_campaigns(p.id, limit=100)
    print(f"{p.name}: {orders.total_records} orders, {camps.total_records} campaigns")
```

### Add-ons only

```python
addons = client.profiles.list_order_items("prof_1", is_add_on=True)
```
