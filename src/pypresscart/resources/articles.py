"""Articles resource: ``/articles/{id}`` endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pypresscart.models.articles import (
    ApproveDraftRequest,
    Article,
    ArticleUpdateRequest,
)
from pypresscart.resources._base import ResourceBase


class ArticlesResource(ResourceBase):
    """Endpoints for articles produced by campaigns."""

    def get(
        self,
        article_id: str,
        *,
        as_json: bool | None = None,
    ) -> Article | dict[str, Any]:
        """Get an article by id. Required scope: ``campaigns.read``."""
        payload = self._client._request("GET", f"/articles/{article_id}")
        return self._parse(payload, Article, as_json)

    def update(
        self,
        article_id: str,
        body: ArticleUpdateRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Article | dict[str, Any]:
        """Update an article. Required scope: ``campaigns.update``."""
        payload = self._client._request(
            "PUT", f"/articles/{article_id}", json=self._serialize(body)
        )
        return self._parse(payload, Article, as_json)

    def approve_brief(
        self,
        article_id: str,
        *,
        as_json: bool | None = None,
    ) -> Article | dict[str, Any]:
        """Approve the brief for an article. Required scope: ``campaigns.update``."""
        payload = self._client._request("PATCH", f"/articles/{article_id}/approve-brief")
        return self._parse(payload, Article, as_json)

    def approve_draft(
        self,
        article_id: str,
        body: ApproveDraftRequest | BaseModel | dict[str, Any] | None = None,
        *,
        as_json: bool | None = None,
    ) -> Article | dict[str, Any]:
        """Approve the draft for an article. Required scope: ``campaigns.update``."""
        payload = self._client._request(
            "PATCH",
            f"/articles/{article_id}/approve-draft",
            json=self._serialize(body),
        )
        return self._parse(payload, Article, as_json)
