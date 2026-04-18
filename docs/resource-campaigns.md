# Resource: Campaigns

A **campaign** groups related articles and order items under a shared brief and questionnaire.

```python
client.campaigns  # CampaignsResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`list`](#list) | `GET /campaigns` | `campaigns.lists` |
| [`get`](#get) | `GET /campaigns/{id}` | `campaigns.read` |
| [`create`](#create) | `POST /campaigns` | `campaigns.create` |
| [`update`](#update) | `PUT /campaigns/{id}` | `campaigns.update` |
| [`list_articles`](#list_articles) | `GET /campaigns/{id}/articles` | `campaigns.read` |
| [`article_status_counts`](#article_status_counts) | `GET /campaigns/{id}/articles/status-count` | `campaigns.read` |
| [`assign_order_items`](#assign_order_items) | `POST /campaigns/{id}/order-items` | `campaigns.update` |
| [`link_questionnaire`](#link_questionnaire) | `POST /questionnaires/{id}/link` | `campaigns.update` |

---

### `list`

```python
def list(
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    filters: dict | None = None,
    as_json: bool | None = None,
) -> Paginated[Campaign] | dict
```

**`filters`**: `search` (str) — partial match on campaign name.

**Example**

```python
camps = client.campaigns.list(filters={"search": "launch"})
for c in camps.records:
    print(c.name, c.total_articles)
```

---

### `get`

```python
def get(
    campaign_id: str,
    *,
    as_json: bool | None = None,
) -> Campaign | dict
```

Returns a full `Campaign` including nested `profile` and `questionnaire`.

---

### `create`

```python
def create(
    body: CampaignCreateRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Campaign | dict
```

**Request body** ([`CampaignCreateRequest`](models-reference.md#campaigncreaterequest)):

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | Required |
| `description` | `str \| None` | Required — send `None` if N/A |
| `profile_id` | `str` | Required |
| `objectives` | `str` | Required |
| `keywords` | `str \| None` | Required — send `None` if N/A |
| `target_audience` | `str \| None` | Required — send `None` if N/A |
| `tone` | `str \| None` | Required — send `None` if N/A |
| `writing_samples` | `str \| None` | Required — send `None` if N/A |
| `file_id` | `str \| None` | Required — send `None` if N/A |

> Unusual: Presscart's schema expects all nine keys to be *present* in the payload, but most may be `null`. `pypresscart`'s `CampaignCreateRequest` uses `exclude_none=True` by default — **pass a dict to preserve explicit nulls** (`create({"name": ..., "keywords": None, ...})`).

**Example**

```python
from pypresscart import CampaignCreateRequest

campaign = client.campaigns.create(
    CampaignCreateRequest(
        name="Q3 Launch",
        description="Announce v2.0",
        profile_id="prof_1",
        objectives="drive awareness",
        keywords="AI, SaaS, launch",
        target_audience="VPs of Engineering",
        tone="authoritative",
        writing_samples=None,
        file_id=None,
    )
)
```

---

### `update`

```python
def update(
    campaign_id: str,
    body: CampaignUpdateRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Campaign | dict
```

All fields on [`CampaignUpdateRequest`](models-reference.md#campaignupdaterequest) are optional — only send what you're changing.

```python
from pypresscart import CampaignUpdateRequest

client.campaigns.update("cmp_1", CampaignUpdateRequest(tone="playful"))
```

---

### `list_articles`

```python
def list_articles(
    campaign_id: str,
    *,
    limit: int = 25,
    page: int = 1,
    sort_by: str | None = None,
    order_by: str | None = None,
    as_json: bool | None = None,
) -> Paginated[CampaignArticleRow] | dict
```

Each row includes the assigned writer, current status, and the article's brief/draft/live URLs.

---

### `article_status_counts`

```python
def article_status_counts(
    campaign_id: str,
    *,
    as_json: bool | None = None,
) -> dict
```

> This endpoint returns a non-standard envelope and is always returned as a `dict`, regardless of `response_mode`:
>
> ```python
> { "records": [ { "name": "In Progress", "prefix": "...", "id": "...", "count": 3 }, ... ] }
> ```
>
> Individual entries can be materialized as `ArticleStatusCount` via `ArticleStatusCount.model_validate(entry)` if you want typed access.

---

### `assign_order_items`

Attach existing order items to a campaign.

```python
def assign_order_items(
    campaign_id: str,
    body: AssignOrderItemsRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> dict
```

**Body**: `{"order_item_ids": ["oi_1", "oi_2"]}`

Returns a non-standard `{"records": [{"id": "...", "campaign_id": "..."}, ...]}` — always a dict.

```python
from pypresscart import AssignOrderItemsRequest

client.campaigns.assign_order_items(
    "cmp_1",
    AssignOrderItemsRequest(order_item_ids=["oi_a", "oi_b"]),
)
```

---

### `link_questionnaire`

Link an uploaded file to the campaign's questionnaire (for writing samples, brand guides, etc.).

```python
def link_questionnaire(
    campaign_id: str,
    body: QuestionnaireLinkRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Questionnaire | dict
```

**Body** ([`QuestionnaireLinkRequest`](models-reference.md#questionnairelinkrequest)):

| Field | Type |
|---|---|
| `file_id` | `str` |
| `file_url` | `str` |
| `file_name` | `str` |
| `file_size` | `int` |

Typical flow:

```python
uploaded = client.files.upload("brand-guide.pdf").files[0]
client.campaigns.link_questionnaire(
    "cmp_1",
    {
        "file_id": uploaded.file_key,
        "file_url": uploaded.file_url,
        "file_name": uploaded.name,
        "file_size": uploaded.size,
    },
)
```

## Recipes

### End-to-end campaign setup

```python
# 1. Create the campaign
c = client.campaigns.create(
    CampaignCreateRequest(
        name="Q3 Launch",
        description="Announce v2.0",
        profile_id="prof_1",
        objectives="drive awareness",
        keywords="AI, SaaS",
        target_audience="VPs of Engineering",
        tone="authoritative",
        writing_samples=None,
        file_id=None,
    )
)

# 2. Place the orders first (see Resource: Orders)
order = client.orders.create_checkout({...})

# 3. Assign the order items to this campaign
order_item_ids = [li.id for li in order.line_items]
client.campaigns.assign_order_items(c.id, {"order_item_ids": order_item_ids})
```

### Progress dashboard

```python
counts = client.campaigns.article_status_counts("cmp_1")
for row in counts["records"]:
    print(f"{row['name']:20} {row['count']}")
```
