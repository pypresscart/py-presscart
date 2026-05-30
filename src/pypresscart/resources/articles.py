"""Articles resource: ``/articles/{id}`` endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pypresscart.models.articles import (
    ApproveDraftRequest,
    Article,
    ArticleUpdateRequest,
    Comment,
    CommentArchiveResponse,
    CommentCreateRequest,
    CommentList,
    CommentUpdateRequest,
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

    # ---- comments --------------------------------------------------------

    def list_comments(
        self,
        article_id: str,
        *,
        as_json: bool | None = None,
    ) -> CommentList | dict[str, Any]:
        """List an article's comments, grouped by root comment with one level
        of replies. Required scopes: ``articles.read``, ``articles.lists``."""
        payload = self._client._request("GET", f"/articles/{article_id}/comments")
        return self._parse(payload, CommentList, as_json)

    def create_comment(
        self,
        article_id: str,
        body: CommentCreateRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Comment | dict[str, Any]:
        """Create a comment on an article. Pass ``parent_comment_id`` to post a
        reply. Required scope: ``articles.create``."""
        payload = self._client._request(
            "POST", f"/articles/{article_id}/comments", json=self._serialize(body)
        )
        return self._parse(payload, Comment, as_json)

    def update_comment(
        self,
        article_id: str,
        comment_reference: str,
        body: CommentUpdateRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Comment | dict[str, Any]:
        """Replace the content of a comment your token created. Required scope:
        ``articles.update``."""
        payload = self._client._request(
            "PUT",
            f"/articles/{article_id}/comments/{comment_reference}",
            json=self._serialize(body),
        )
        return self._parse(payload, Comment, as_json)

    def archive_comment(
        self,
        article_id: str,
        comment_reference: str,
        *,
        as_json: bool | None = None,
    ) -> CommentArchiveResponse | dict[str, Any]:
        """Soft-delete (archive) a comment your token created. Required scope:
        ``articles.delete``."""
        payload = self._client._request(
            "DELETE", f"/articles/{article_id}/comments/{comment_reference}"
        )
        return self._parse(payload, CommentArchiveResponse, as_json)
