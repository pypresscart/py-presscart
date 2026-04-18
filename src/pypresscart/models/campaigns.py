"""Campaign models."""

from __future__ import annotations

from datetime import datetime

from pypresscart.models._common import PresscartModel


class ProfileRef(PresscartModel):
    id: str | None = None
    name: str | None = None
    logo: str | None = None


class Questionnaire(PresscartModel):
    id: str | None = None
    campaign_id: str | None = None
    objectives: str | None = None
    keywords: str | None = None
    target_audience: str | None = None
    tone: str | None = None
    writing_samples: str | None = None
    file_id: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    file_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class CampaignArticleRef(PresscartModel):
    id: str | None = None
    name: str | None = None
    campaign_id: str | None = None
    live_url: str | None = None
    order_item: dict[str, object] | None = None


class Campaign(PresscartModel):
    """Response for ``GET /campaigns/{id}`` / ``POST /campaigns`` etc."""

    id: str
    name: str | None = None
    description: str | None = None
    reference: str | None = None
    profile_id: str | None = None
    v1_campaign_id: str | None = None
    status: str | None = None
    goals: str | None = None
    target_date: datetime | None = None
    budget: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    questionnaire_id: str | None = None
    keywords: str | None = None
    objectives: str | None = None
    target_audience: str | None = None
    tone: str | None = None
    writing_samples: str | None = None
    file_id: str | None = None
    total_articles: int | None = None
    profile: ProfileRef | None = None
    questionnaire: Questionnaire | None = None
    articles: list[CampaignArticleRef] = []


class CampaignCreateRequest(PresscartModel):
    """Body for ``POST /campaigns``.

    All fields are required by the API; send ``None`` for ones that don't apply.
    """

    name: str
    description: str | None = None
    profile_id: str
    objectives: str
    keywords: str | None = None
    target_audience: str | None = None
    tone: str | None = None
    writing_samples: str | None = None
    file_id: str | None = None


class CampaignUpdateRequest(PresscartModel):
    """Body for ``PUT /campaigns/{id}`` (all fields optional)."""

    name: str | None = None
    description: str | None = None
    keywords: str | None = None
    objectives: str | None = None
    target_audience: str | None = None
    tone: str | None = None
    writing_samples: str | None = None
    file_id: str | None = None


class AssignOrderItemsRequest(PresscartModel):
    """Body for ``POST /campaigns/{id}/order-items``."""

    order_item_ids: list[str]


class AssignOrderItemsRecord(PresscartModel):
    id: str
    campaign_id: str | None = None


class QuestionnaireLinkRequest(PresscartModel):
    """Body for ``POST /questionnaires/{campaign_id}/link``."""

    file_id: str
    file_url: str
    file_name: str
    file_size: int


class ArticleStatus(PresscartModel):
    effective_at: datetime | None = None
    notes: str | None = None
    name: str | None = None
    prefix: str | None = None
    color: str | None = None


class ArticleStatusCount(PresscartModel):
    """Entry in ``GET /campaigns/{id}/articles/status-count``."""

    name: str | None = None
    prefix: str | None = None
    id: str | None = None
    count: int | None = None


__all__ = [
    "ArticleStatus",
    "ArticleStatusCount",
    "AssignOrderItemsRecord",
    "AssignOrderItemsRequest",
    "Campaign",
    "CampaignArticleRef",
    "CampaignCreateRequest",
    "CampaignUpdateRequest",
    "ProfileRef",
    "Questionnaire",
    "QuestionnaireLinkRequest",
]
