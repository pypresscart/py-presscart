# Articles

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
| [`list_comments`](#list_comments) | `GET /articles/{article_id}/comments` | `articles.read`, `articles.lists` |
| [`create_comment`](#create_comment) | `POST /articles/{article_id}/comments` | `articles.create` |
| [`update_comment`](#update_comment) | `PUT /articles/{article_id}/comments/{comment_reference}` | `articles.update` |
| [`archive_comment`](#archive_comment) | `DELETE /articles/{article_id}/comments/{comment_reference}` | `articles.delete` |

---

### `get`

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

---

## Comments

Discussions attached to an article. An API-token integration can list, create, update, and archive comments on behalf of its own end-users. Replies are one level deep via `parent_comment_id`. The short reference returned as `id` (e.g. `K7M2Q9XA`) — not a UUID — is the handle for update/archive.

### `list_comments`

```python
def list_comments(
    article_id: str,
    *,
    as_json: bool | None = None,
) -> CommentList | dict
```

**Returns** {py:class}`~pypresscart.models.CommentList` — `records` is a list of root {py:class}`~pypresscart.models.Comment`s, each carrying up to one level of `replies`. There is no pagination envelope; the endpoint returns `records` only.

```python
thread = client.articles.list_comments("art_1")
for comment in thread.records:
    print(comment.author.name, comment.content)
    for reply in comment.replies:
        print("  ->", reply.author.name, reply.content)
```

---

### `create_comment`

```python
def create_comment(
    article_id: str,
    body: CommentCreateRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Comment | dict
```

**Returns** {py:class}`~pypresscart.models.Comment` — the created comment (HTTP 201). Pass `parent_comment_id` to post a reply.

**Body** ([`CommentCreateRequest`](models-reference.md#commentcreaterequest)):

| Field | Type |
|---|---|
| `content` | `str` (1–10,000 chars) |
| `author` | `CommentAuthorInput` — `name` required; optional `email`, `external_id` |
| `parent_comment_id` | `str \| None` (omit for root comments) |

```python
from pypresscart import CommentCreateRequest

client.articles.create_comment(
    "art_1",
    CommentCreateRequest(
        content="Can you clarify the requested change?",
        author={"name": "Jane Smith", "email": "jane@example.com"},
    ),
)
```

---

### `update_comment`

Replace the content of a comment your token created. Updating someone else's comment (or one created from the dashboard) returns HTTP 403.

```python
def update_comment(
    article_id: str,
    comment_reference: str,
    body: CommentUpdateRequest | BaseModel | dict,
    *,
    as_json: bool | None = None,
) -> Comment | dict
```

**Returns** {py:class}`~pypresscart.models.Comment` — the updated comment.

```python
client.articles.update_comment("art_1", "K7M2Q9XA", {"content": "Updated text."})
```

---

### `archive_comment`

Soft-delete a comment your token created. Archived comments drop out of `list_comments` and the dashboard.

```python
def archive_comment(
    article_id: str,
    comment_reference: str,
    *,
    as_json: bool | None = None,
) -> CommentArchiveResponse | dict
```

**Returns** {py:class}`~pypresscart.models.CommentArchiveResponse` — an empty marker object; the API responds `204 No Content`, so in JSON mode this is `{}`. Success is signalled by the absence of an exception (a 403 means the comment isn't yours).

```python
client.articles.archive_comment("art_1", "K7M2Q9XA")
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
