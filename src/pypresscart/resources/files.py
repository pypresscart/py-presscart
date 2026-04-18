"""Files resource: ``/files`` endpoints (list/upload/download/move/delete)."""

from __future__ import annotations

import mimetypes
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
    # Explicit tuple — caller provided the content type, trust it.
    if isinstance(item, tuple):
        return item
    if isinstance(item, (str, Path)):
        path = Path(item)
        fh = path.open("rb")
        opened.append(fh)
        return (path.name, fh, _detect_mime(fh, path.name))
    name = getattr(item, "name", "upload")
    filename = Path(name).name
    return (filename, item, _detect_mime(item, filename))


# ---- MIME detection --------------------------------------------------------

# Magic-byte signatures for the content types Presscart's upload endpoint
# accepts, plus a few adjacent ones (gif, bmp, tiff, zip) for good measure.
# Each entry is (offset, magic_bytes, mime_type). Checked in order; first
# match wins.
_MAGIC_SIGNATURES: tuple[tuple[int, bytes, str], ...] = (
    (0, b"\xff\xd8\xff", "image/jpeg"),
    (0, b"\x89PNG\r\n\x1a\n", "image/png"),
    (0, b"GIF87a", "image/gif"),
    (0, b"GIF89a", "image/gif"),
    (0, b"BM", "image/bmp"),
    (0, b"II*\x00", "image/tiff"),
    (0, b"MM\x00*", "image/tiff"),
    (0, b"%PDF-", "application/pdf"),
    # DOC (old binary Office format): OLE compound file header.
    (0, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "application/msword"),
)

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _is_riff_webp(head: bytes) -> bool:
    return len(head) >= 12 and head[0:4] == b"RIFF" and head[8:12] == b"WEBP"


def _looks_like_text(head: bytes) -> bool:
    """Heuristic: all bytes in the sniff window are printable / common whitespace."""
    if not head:
        return False
    allowed = {0x09, 0x0A, 0x0D}  # tab, LF, CR
    return all(b in allowed or 0x20 <= b < 0x7F for b in head)


def _sniff_mime(head: bytes, filename: str) -> str | None:
    """Identify a MIME type from magic bytes, with a few heuristic extras.

    Returns ``None`` if no reliable sniff is possible — callers should then
    fall back to extension-based guessing.
    """
    for offset, magic, mime in _MAGIC_SIGNATURES:
        if head[offset : offset + len(magic)] == magic:
            return mime
    if _is_riff_webp(head):
        return "image/webp"
    # ZIP container — could be docx/xlsx/pptx/etc. or a plain zip. Use the
    # filename extension to narrow it; fall back to application/zip.
    if head[:4] == b"PK\x03\x04":
        ext = Path(filename).suffix.lower()
        if ext == ".docx":
            return _DOCX_MIME
        if ext == ".xlsx":
            return (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        if ext == ".pptx":
            return (
                "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        return "application/zip"
    if _looks_like_text(head):
        return "text/plain"
    return None


def _detect_mime(source: IO[bytes], filename: str) -> str:
    """Detect the MIME type of an upload source.

    Precedence:
    1. Magic-byte sniff of the first 64 bytes (canonical).
    2. :func:`mimetypes.guess_type` on the filename.
    3. ``application/octet-stream`` as a final fallback.

    After reading, the stream is rewound to its original position so the
    subsequent multipart upload sees the full content. Non-seekable streams
    fall through to extension-based guessing only.
    """
    sniffed: str | None = None
    if hasattr(source, "seek") and hasattr(source, "tell"):
        try:
            pos = source.tell()
            head = source.read(64)
            source.seek(pos)
            sniffed = _sniff_mime(head, filename)
        except (OSError, ValueError):
            # Non-seekable stream; fall through to extension.
            sniffed = None
    if sniffed:
        return sniffed
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"
