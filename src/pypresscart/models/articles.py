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


__all__ = [
    "ApproveDraftRequest",
    "Article",
    "ArticleOrderItem",
    "ArticleStatusRef",
    "ArticleUpdateRequest",
    "ArticleWriter",
    "CampaignArticleRow",
]
