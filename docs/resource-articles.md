# Articles

Individual articles (the content piece going to an outlet) within a campaign.

```python
client.articles  # ArticlesResource
```

:::{warning}
**The entire Articles resource is currently blocked upstream.** `GET /articles/{article_id}` returns `403 Insufficient permissions` to `full_access` API tokens, and since the write endpoints need the article's current state before you can safely change it, none of these methods can be exercised end-to-end until the server-side issue is resolved. See [Testing status](testing-status.md) and [issue #8](https://github.com/annjawn/py-presscart/issues/8).
:::

## Methods overview

| Method | HTTP | Scope |
|---|---|---|
| [`get`](#get) | `GET /articles/{article_id}` | `campaigns.read` |
| [`update`](#update) | `PUT /articles/{article_id}` | `campaigns.update` |
| [`approve_brief`](#approve_brief) | `PATCH /articles/{article_id}/approve-brief` | `campaigns.update` |
| [`approve_draft`](#approve_draft) | `PATCH /articles/{article_id}/approve-draft` | `campaigns.update` |

---

### `get`

:::{error}
**Currently returns 403** for `full_access` API tokens — [issue #8](https://github.com/annjawn/py-presscart/issues/8).
:::

```python
def get(
    article_id: str,
    *,
    as_json: bool | None = None,
) -> Article | dict
```

**Returns** {py:class}`~pypresscart.models.Article` — the article's brief URL, draft URL, live URL (when published), writer, current status, and expected completion date.

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

**Returns** {py:class}`~pypresscart.models.Article` — the updated article.

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

**Returns** {py:class}`~pypresscart.models.Article` — the updated article. No request body.

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

**Returns** {py:class}`~pypresscart.models.Article` — the updated article.

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

Use `client.campaigns.list_articles(campaign_id)` — see [Campaigns](resource-campaigns.md).
