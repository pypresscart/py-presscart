"""Folders resource: ``/folders`` endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pypresscart.models._common import Paginated
from pypresscart.models.folders import (
    DeleteFolderResponse,
    Folder,
    FolderCreateRequest,
    FolderRenameRequest,
)
from pypresscart.resources._base import ResourceBase


class FoldersResource(ResourceBase):
    """Folder management."""

    def list(
        self,
        *,
        q: str | None = None,
        as_json: bool | None = None,
    ) -> Paginated[Folder] | dict[str, Any]:
        """List folders. Required scope: ``folders.lists``."""
        payload = self._client._request("GET", "/folders", params={"q": q})
        return self._parse_paginated(payload, Folder, as_json)

    def create(
        self,
        body: FolderCreateRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Folder | dict[str, Any]:
        """Create a folder. Required scope: ``folders.create``."""
        payload = self._client._request("POST", "/folders", json=self._serialize(body))
        return self._parse(payload, Folder, as_json)

    def rename(
        self,
        folder_id: str,
        body: FolderRenameRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Folder | dict[str, Any]:
        """Rename a folder. Required scope: ``folders.update``."""
        payload = self._client._request(
            "PATCH", f"/folders/{folder_id}", json=self._serialize(body)
        )
        return self._parse(payload, Folder, as_json)

    def delete(
        self,
        folder_id: str,
        *,
        as_json: bool | None = None,
    ) -> DeleteFolderResponse | dict[str, Any]:
        """Delete a folder (files within lose their folder association). Scope: ``folders.delete``."""
        payload = self._client._request("DELETE", f"/folders/{folder_id}")
        return self._parse(payload, DeleteFolderResponse, as_json)
