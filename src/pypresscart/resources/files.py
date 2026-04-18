"""Files resource: ``/files`` endpoints (list/upload/download/move/delete)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import IO, Any

from pydantic import BaseModel

from pypresscart.models._common import Paginated
from pypresscart.models.files import (
    DeleteFileResponse,
    File,
    MoveFilesRequest,
    MoveFilesResponse,
    UploadFilesResponse,
)
from pypresscart.resources._base import ResourceBase


class FilesResource(ResourceBase):
    """File upload and management."""

    def list(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        q: str | None = None,
        folder_id: str | None = None,
        as_json: bool | None = None,
    ) -> Paginated[File] | dict[str, Any]:
        """List files. Required scope: ``files.lists``."""
        params = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
            "q": q,
            "folder_id": folder_id,
        }
        payload = self._client._request("GET", "/files", params=params)
        return self._parse_paginated(payload, File, as_json)

    def get(
        self,
        file_id: str,
        *,
        as_json: bool | None = None,
    ) -> File | dict[str, Any]:
        """Get a single file record. Required scope: ``files.read``."""
        payload = self._client._request("GET", f"/files/{file_id}")
        return self._parse(payload, File, as_json)

    def upload(
        self,
        files: str | Path | IO[bytes] | tuple[str, IO[bytes], str] | Sequence[Any],
        *,
        folder_id: str | None = None,
        as_json: bool | None = None,
    ) -> UploadFilesResponse | dict[str, Any]:
        """Upload 1-5 files. Required scope: ``files.create``.

        Accepts:
          - a path (``str`` or :class:`pathlib.Path`)
          - an open binary file handle
          - a ``(filename, fileobj, content_type)`` tuple
          - a list mixing any of the above
        """
        items: Sequence[Any] = files if isinstance(files, list) else [files]
        multipart: list[tuple[str, Any]] = []
        opened: list[IO[bytes]] = []
        try:
            for item in items:
                multipart.append(("files", _prepare_upload(item, opened)))
            data: dict[str, Any] = {}
            if folder_id is not None:
                data["folder_id"] = folder_id
            payload = self._client._request("POST", "/files/upload", data=data, files=multipart)
        finally:
            for fh in opened:
                fh.close()
        return self._parse(payload, UploadFilesResponse, as_json)

    def download(self, file_id: str) -> bytes:
        """Download the raw bytes of a file. Required scope: ``files.read``."""
        return self._client._request_raw("GET", f"/files/{file_id}/download")

    def move(
        self,
        body: MoveFilesRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> MoveFilesResponse | dict[str, Any]:
        """Move files into a folder (or to root with ``folder_id=None``). Scope: ``files.update``."""
        payload = self._client._request("POST", "/files/move", json=self._serialize(body))
        return self._parse(payload, MoveFilesResponse, as_json)

    def delete(
        self,
        file_id: str,
        *,
        as_json: bool | None = None,
    ) -> DeleteFileResponse | dict[str, Any]:
        """Delete a file. Required scope: ``files.delete``."""
        payload = self._client._request("DELETE", f"/files/{file_id}")
        return self._parse(payload, DeleteFileResponse, as_json)


def _prepare_upload(
    item: str | Path | IO[bytes] | tuple[str, IO[bytes], str],
    opened: list[IO[bytes]],
) -> tuple[str, IO[bytes]] | tuple[str, IO[bytes], str]:
    if isinstance(item, tuple):
        return item
    if isinstance(item, (str, Path)):
        path = Path(item)
        fh = path.open("rb")
        opened.append(fh)
        return (path.name, fh)
    name = getattr(item, "name", "upload")
    return (Path(name).name, item)
