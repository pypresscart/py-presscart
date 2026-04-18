"""File models."""

from __future__ import annotations

from datetime import datetime

from pypresscart.models._common import PresscartModel


class File(PresscartModel):
    """Record returned by ``GET /files`` / ``GET /files/{id}``."""

    id: str
    name: str | None = None
    file_key: str | None = None
    file_url: str | None = None
    size: int | None = None
    mime_type: str | None = None
    team_id: str | None = None
    folder_id: str | None = None
    uploaded_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class UploadedFile(PresscartModel):
    """Entry in the ``POST /files/upload`` response."""

    id: str
    file_key: str | None = None
    file_url: str | None = None
    name: str | None = None
    size: int | None = None
    mime_type: str | None = None
    folder_id: str | None = None


class UploadFilesResponse(PresscartModel):
    files: list[UploadedFile] = []


class MoveFilesRequest(PresscartModel):
    """Body for ``POST /files/move``."""

    file_ids: list[str]
    folder_id: str | None = None


class MoveFilesResponse(PresscartModel):
    moved_count: int


class DeleteFileResponse(PresscartModel):
    success: bool


__all__ = [
    "DeleteFileResponse",
    "File",
    "MoveFilesRequest",
    "MoveFilesResponse",
    "UploadFilesResponse",
    "UploadedFile",
]
