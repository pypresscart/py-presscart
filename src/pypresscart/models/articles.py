"""Article models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pypresscart.models._common import IncludeItem, PresscartModel
from pypresscart.models.campaigns import ArticleStatus
from pypresscart.models.orders import OutletRef


class ArticleWriter(PresscartModel):
    id: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class ArticleOrderItem(PresscartModel):
    name: str | None = None
    outlet: OutletRef | None = None
    addons: list[dict[str, Any]] = []
    includes: list[IncludeItem] = []


class CampaignArticleRow(PresscartModel):
    """Entry in ``GET /campaigns/{id}/articles``."""

    id: str
    name: str | None = None
    live_url: str | None = None
    brief_google_doc_url: str | None = None
    draft_google_doc_url: str | None = None
    campaign_id: str | None = None
    order_item_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    total_images: int | None = None
    writer: ArticleWriter | None = None
    status: list[ArticleStatus] = []
    order_item: ArticleOrderItem | None = None


class ArticleStatusRef(PresscartModel):
    name: str | None = None
    prefix: str | None = None
    color: str | None = None


class Article(PresscartModel):
    """Response from ``GET /articles/{article_id}``."""

    id: str
    name: str | None = None
    brief_google_doc_url: str | None = None
    draft_google_doc_url: str | None = None
    live_url: str | None = None
    campaign_id: str | None = None
    product_id: str | None = None
    profile_id: str | None = None
    updated_at: datetime | None = None
    writer: ArticleWriter | None = None
    support_agent: dict[str, Any] | None = None
    status: ArticleStatusRef | None = None
    files: list[dict[str, Any]] = []
    expected_completion_date: datetime | None = None
    expected_completion_date_title: str | None = None


class ArticleUpdateRequest(PresscartModel):
    """Body for ``PUT /articles/{id}``."""

    brief_google_doc_url: str | None = None
    name: str | None = None


class ApproveDraftRequest(PresscartModel):
    """Body for ``PATCH /articles/{id}/approve-draft``."""

    draft_google_doc_url: str | None = None


# --- Comments -----------------------------------------------------------------


class CommentAuthor(PresscartModel):
    """Author block on a comment response."""

    name: str | None = None
    email: str | None = None


class Comment(PresscartModel):
    """A comment on an article. Root comments carry one level of ``replies``."""

    id: str
    content: str | None = None
    author: CommentAuthor | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    parent_comment_id: str | None = None
    replies: list[Comment] = []  # one level deep; reply objects omit this key


class CommentList(PresscartModel):
    """Response from ``GET /articles/{id}/comments`` — records only, no pagination."""

    records: list[Comment] = []


class CommentAuthorInput(PresscartModel):
    """Author block for ``POST /articles/{id}/comments``."""

    name: str  # required, 1-200 characters
    email: str | None = None
    external_id: str | None = None  # your system's id for the author; audit only


class CommentCreateRequest(PresscartModel):
    """Body for ``POST /articles/{id}/comments``."""

    content: str  # required, 1-10,000 characters
    author: CommentAuthorInput
    parent_comment_id: str | None = None  # omit for root comments


class CommentUpdateRequest(PresscartModel):
    """Body for ``PUT /articles/{id}/comments/{ref}``."""

    content: str  # required, 1-10,000 characters


class CommentArchiveResponse(PresscartModel):
    """Empty body of ``DELETE /articles/{id}/comments/{ref}`` (204 No Content)."""

    # Intentionally no fields — the API returns no body; validates ``{}`` cleanly.


__all__ = [
    "ApproveDraftRequest",
    "Article",
    "ArticleOrderItem",
    "ArticleStatusRef",
    "ArticleUpdateRequest",
    "ArticleWriter",
    "CampaignArticleRow",
    "Comment",
    "CommentArchiveResponse",
    "CommentAuthor",
    "CommentAuthorInput",
    "CommentCreateRequest",
    "CommentList",
    "CommentUpdateRequest",
]
