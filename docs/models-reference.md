# Models Reference

Every request/response shape has a Pydantic model under `pypresscart.models`, re-exported at the top level. This page lists the public models and their key fields. For full field detail, see the source or use `.model_fields` at runtime.

> All models inherit `PresscartModel` (which is `pydantic.BaseModel` with `extra="allow"` so forward-compatible API fields don't cause validation errors).

## Shared primitives

### `Paginated[T]`

Generic pagination envelope. Documented in [Pagination](pagination.md).

```python
class Paginated[T]:
    records: list[T]
    total_records: int | None
    total_pages: int | None
    current_page: int | None
    next_page: int | None
    previous_page: int | None
```

### `Tag`

```python
class Tag:
    name: str
```

### `Price`

```python
class Price:
    unit_amount: int        # cents
    currency: str | None    # usually "usd"
    pricing_tier: str | None
```

### `IncludeItem`

```python
class IncludeItem:
    channel_type: ChannelType | str
    placement_type: PlacementType | str
```

## Enums

```python
class ChannelType(str, Enum):
    WEBSITE, NEWSLETTER, INSTAGRAM, LINKEDIN,
    YOUTUBE, TIKTOK, TWITTER_X, PODCAST, OTHER

class PlacementType(str, Enum):
    FULL_FEATURE, PRESS_RELEASE, MENTION, QUOTE, LISTICLE

class OutletStatus(str, Enum):
    ACTIVE, INACTIVE, DRAFT, PENDING_REVIEW,
    PENDING_AGREEMENT, REJECTED, ARCHIVED, SUSPENDED

class TokenType(str, Enum):
    FULL_ACCESS = "full_access"
    CUSTOM = "custom"
    READ_ONLY = "read_only"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
```

All enums accept either the enum value or a raw string — models declare the type as `Enum | str` for forward compatibility.

## Auth

### `TokenInfo`

Response from [Auth](resource-auth.md)`.whoami()`.

| Field | Type |
|---|---|
| `source` | `str` |
| `team_id` | `str` |
| `token_type` | `TokenType \| str` |
| `scopes` | `list[str]` |
| `pro_pricing_enabled` | `bool \| None` |

## Outlets

### `Outlet`
Full outlet with `outlet_channels`, `tags`, metadata. Returned by `client.outlets.get()`.

### `OutletListing`
A row in `client.outlets.list()` / `client.outlets.list_products()`. `id` is a *product id*; `outlet_id` is the outlet.

### `OutletChannel`, `OutletChannelSummary`
The detailed and summary forms of a channel on an outlet.

### `CountriesResponse`, `StatesResponse`, `CitiesResponse`
Wrappers around `{"countries": [...]}` / `{"states": [...]}` / `{"cities": [...]}`.

### `DisclaimerRecord`
```python
class DisclaimerRecord:
    id: str
    name: str | None
    description: str | None
```

## Products

### `Product`
Full product (from `client.products.get()`).

### `ProductListing`
Row in `client.products.list_listings()`.

### `ProductCategoryCount`
```python
class ProductCategoryCount:
    type: str    # e.g. "FULL_FEATURE"
    count: int
```

## Orders

### `Order`
Full order; includes nested `line_items`, `team`, and payment metadata. See [Orders](resource-orders.md).

### `LineItem`
A single line on an order.

### `CheckoutRequest`
Body for `client.orders.create_checkout()`.

| Field | Type |
|---|---|
| `profile_id` | `str` |
| `line_items` | `list[CheckoutLineItem]` |
| `discount` | `int \| None` (default `0`) |

### `CheckoutLineItem`

| Field | Type |
|---|---|
| `product_id` | `str` |
| `quantity` | `int` (default `1`) |
| `is_add_on` | `bool` (default `False`) |
| `linked_order_line_item_id` | `str \| None` |

### `OutletRef`, `TeamRef`
Minimal embedded references inside `Order`.

## Order Items

### `OrderItem`
Team-wide order item (`GET /order-items`). Fields cover commissions, accounting, refunds, publisher payouts, and nested `article`/`outlet`/`client` references.

### `ProfileOrderItem`
Slimmer shape returned by `client.profiles.list_order_items()` (bare-array endpoint).

## Profiles

### `Profile`
Brand/entity the team promotes.

| Field | Type | Notes |
|---|---|---|
| `id`, `name` | `str` | |
| `type` | `str` | e.g. `"COMPANY"`, `"INDIVIDUAL"` |
| `primary_goals` | `list[str]` | e.g. `["BRAND_AWARENESS"]` |
| `website_url`, `logo`, `location` | `str \| None` | |
| (many more) | | see source |

## Campaigns

### `Campaign`
Full campaign, including optional nested `profile`, `questionnaire`, `articles`.

### `CampaignCreateRequest`
See [Campaigns](resource-campaigns.md) — all fields required at the schema level, though many may be `None`.

### `CampaignUpdateRequest`
All fields optional.

### `Questionnaire`
Linked brief/research attached to a campaign.

### `AssignOrderItemsRequest`
```python
class AssignOrderItemsRequest:
    order_item_ids: list[str]
```

### `QuestionnaireLinkRequest`

| Field | Type |
|---|---|
| `file_id` | `str` |
| `file_url` | `str` |
| `file_name` | `str` |
| `file_size` | `int` |

### `ArticleStatus`, `ArticleStatusCount`
Status change entries / aggregate counts.

## Articles

### `Article`
Full article (from `client.articles.get()`).

### `CampaignArticleRow`
Row in `client.campaigns.list_articles()`.

### `ArticleUpdateRequest`
| Field | Type |
|---|---|
| `name` | `str \| None` |
| `brief_google_doc_url` | `str \| None` |

### `ApproveDraftRequest`
```python
class ApproveDraftRequest:
    draft_google_doc_url: str | None
```

### `ArticleWriter`, `ArticleOrderItem`, `ArticleStatusRef`
Embedded references.

## Files

### `File`
A file record with `file_key`, `file_url`, `size`, `mime_type`, `folder_id`, timestamps.

### `UploadedFile`, `UploadFilesResponse`
Shape returned by `client.files.upload()`:

```python
class UploadFilesResponse:
    files: list[UploadedFile]
```

### `MoveFilesRequest`

```python
class MoveFilesRequest:
    file_ids: list[str]
    folder_id: str | None
```

### `MoveFilesResponse`

```python
class MoveFilesResponse:
    moved_count: int
```

### `DeleteFileResponse`
```python
class DeleteFileResponse:
    success: bool
```

## Folders

### `Folder`
```python
class Folder:
    id: str
    name: str | None
    team_id: str | None
    created_by: str | None
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None
```

### `FolderCreateRequest`, `FolderRenameRequest`
```python
class FolderCreateRequest:
    name: str

class FolderRenameRequest:
    name: str
```

### `DeleteFolderResponse`
```python
class DeleteFolderResponse:
    success: bool
```

## Working with models

### Construct

```python
from pypresscart import CheckoutRequest, CheckoutLineItem

body = CheckoutRequest(
    profile_id="prof_1",
    line_items=[CheckoutLineItem(product_id="prod_1")],
)
```

### Validate from a dict

```python
from pypresscart import Order

order = Order.model_validate(raw_dict)
```

### Dump to JSON-compatible dict

```python
body.model_dump(mode="json", exclude_none=True)
```

### Forward compatibility

All models use `extra="allow"`, so new fields the API adds don't break validation — they're preserved on the instance (accessible via `model.model_extra`) but not type-checked.
