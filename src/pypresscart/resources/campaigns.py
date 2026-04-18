"""Campaigns resource: ``/campaigns`` + related questionnaire / article endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pypresscart.models._common import Paginated, serialize_filters
from pypresscart.models.articles import CampaignArticleRow
from pypresscart.models.campaigns import (
    AssignOrderItemsRequest,
    Campaign,
    CampaignCreateRequest,
    CampaignUpdateRequest,
    Questionnaire,
    QuestionnaireLinkRequest,
)
from pypresscart.resources._base import ResourceBase


class CampaignsResource(ResourceBase):
    """Campaign, article listing, and questionnaire endpoints."""

    def list(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        filters: dict[str, Any] | None = None,
        as_json: bool | None = None,
    ) -> Paginated[Campaign] | dict[str, Any]:
        """List campaigns. Required scope: ``campaigns.lists``."""
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        params.update(serialize_filters("filters", filters))
        payload = self._client._request("GET", "/campaigns", params=params)
        return self._parse_paginated(payload, Campaign, as_json)

    def get(
        self,
        campaign_id: str,
        *,
        as_json: bool | None = None,
    ) -> Campaign | dict[str, Any]:
        """Get a campaign by id. Required scope: ``campaigns.read``."""
        payload = self._client._request("GET", f"/campaigns/{campaign_id}")
        return self._parse(payload, Campaign, as_json)

    def create(
        self,
        body: CampaignCreateRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Campaign | dict[str, Any]:
        """Create a campaign. Required scope: ``campaigns.create``."""
        payload = self._client._request("POST", "/campaigns", json=self._serialize(body))
        return self._parse(payload, Campaign, as_json)

    def update(
        self,
        campaign_id: str,
        body: CampaignUpdateRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Campaign | dict[str, Any]:
        """Update a campaign. Required scope: ``campaigns.update``."""
        payload = self._client._request(
            "PUT", f"/campaigns/{campaign_id}", json=self._serialize(body)
        )
        return self._parse(payload, Campaign, as_json)

    def list_articles(
        self,
        campaign_id: str,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        as_json: bool | None = None,
    ) -> Paginated[CampaignArticleRow] | dict[str, Any]:
        """List articles for a campaign. Required scope: ``campaigns.read``."""
        params = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        payload = self._client._request("GET", f"/campaigns/{campaign_id}/articles", params=params)
        return self._parse_paginated(payload, CampaignArticleRow, as_json)

    def article_status_counts(
        self,
        campaign_id: str,
        *,
        as_json: bool | None = None,
    ) -> dict[str, Any]:
        """Counts of articles by status for a campaign. Required scope: ``campaigns.read``.

        Returns the raw envelope ``{"records": [...]}``. Individual entries are
        parsed as :class:`presscart.models.ArticleStatusCount` when accessed.
        """
        payload = self._client._request("GET", f"/campaigns/{campaign_id}/articles/status-count")
        # This endpoint's envelope is non-standard (no pagination fields);
        # return as-is in either mode.
        return payload

    def assign_order_items(
        self,
        campaign_id: str,
        body: AssignOrderItemsRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> dict[str, Any]:
        """Attach order items to a campaign. Required scope: ``campaigns.update``."""
        payload = self._client._request(
            "POST",
            f"/campaigns/{campaign_id}/order-items",
            json=self._serialize(body),
        )
        # Non-standard envelope (``{"records": [...]}``); return as dict.
        return payload

    def link_questionnaire(
        self,
        campaign_id: str,
        body: QuestionnaireLinkRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Questionnaire | dict[str, Any]:
        """Link an uploaded file to a campaign's questionnaire. Scope: ``campaigns.update``."""
        payload = self._client._request(
            "POST",
            f"/questionnaires/{campaign_id}/link",
            json=self._serialize(body),
        )
        return self._parse(payload, Questionnaire, as_json)
