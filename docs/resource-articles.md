# Resource: Articles

Individual articles (the content piece going to an outlet) within a campaign.

```python
client.articles  # ArticlesResource
```

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`get`](#get) | `GET /articles/{article_id}` | `campaigns.read` |
| [`update`](#update) | `PUT /articles/{article_id}` | `campaigns.update` |
| [`approve_brief`](#approve_brief) | `PATCH /articles/{article_id}/approve-brief` | `campaigns.update` |
| [`approve_draft`](#approve_draft) | `PATCH /articles/{article_id}/approve-draft` | `campaigns.update` |

---

### `get`

```python
def get(
    article_id: str,
    *,
    as_json: bool | None = None,
) -> Article | dict
```

Returns the article's brief URL, draft URL, live URL (when published), writer, current status, and expected completion date.

```python
art = client.articles.get("art_1")
print(art.name, art.status.name, art.expected_completion_date)
```

---

### `update`

```python
def update(
    article_id: str,
    body: ArticleUpdateRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Article | dict
```

**Body** ([`ArticleUpdateRequest`](models-reference.md#articleupdaterequest)):

| Field | Type |
|---|---|
| `name` | `str \| None` |
| `brief_google_doc_url` | `str \| None` |

**Example**

```python
from pypresscart import ArticleUpdateRequest

client.articles.update(
    "art_1",
    ArticleUpdateRequest(brief_google_doc_url="https://docs.google.com/document/d/..."),
)
```

---

### `approve_brief`

Mark the brief as approved — moves the article forward in the workflow.

```python
def approve_brief(
    article_id: str,
    *,
    as_json: bool | None = None,
) -> Article | dict
```

No body. Returns the updated article.

```python
client.articles.approve_brief("art_1")
```

---

### `approve_draft`

Approve the draft, optionally providing the Google Doc URL if it's not already set.

```python
def approve_draft(
    article_id: str,
    body: ApproveDraftRequest | BaseModel | dict | None = None,
    *,
    as_json: bool | None = None,
) -> Article | dict
```

**Body** (optional) — `ApproveDraftRequest(draft_google_doc_url=...)`.

```python
client.articles.approve_draft(
    "art_1",
    {"draft_google_doc_url": "https://docs.google.com/document/d/..."},
)
```

## Recipes

### Walk the approval flow

```python
art = client.articles.get("art_1")

if art.status.name == "Brief Ready":
    client.articles.approve_brief(art.id)

# ...later, when writer submits draft...
client.articles.approve_draft(
    art.id,
    {"draft_google_doc_url": draft_url},
)
```

### List all articles for a campaign

Use `client.campaigns.list_articles(campaign_id)` — see [Resource: Campaigns](resource-campaigns.md).
