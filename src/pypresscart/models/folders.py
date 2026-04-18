"""Folder models."""

from __future__ import annotations

from datetime import datetime

from pypresscart.models._common import PresscartModel


class Folder(PresscartModel):
    """Record returned by ``GET /folders``."""

    id: str
    name: str | None = None
    team_id: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class FolderCreateRequest(PresscartModel):
    """Body for ``POST /folders``."""

    name: str


class FolderRenameRequest(PresscartModel):
    """Body for ``PATCH /folders/{id}``."""

    name: str


class DeleteFolderResponse(PresscartModel):
    success: bool


__all__ = [
    "DeleteFolderResponse",
    "Folder",
    "FolderCreateRequest",
    "FolderRenameRequest",
]
