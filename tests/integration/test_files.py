"""Live integration test for the Files resource — full round-trip.

Creates a folder, uploads a tiny embedded test JPEG, fetches it, lists it,
downloads it (sha256-verified against source), moves to root, moves back,
deletes the file, deletes the folder. Self-cleaning even on failure.
"""

from __future__ import annotations

import base64
import contextlib
import hashlib
from collections.abc import Iterator
from typing import Any

import pytest

from pypresscart import (
    File,
    MoveFilesRequest,
    PresscartClient,
    UploadFilesResponse,
)

pytestmark = pytest.mark.integration


# A 1x1 white JPEG (≈ 600 bytes). Embedded so the test is self-contained — no
# need to ship a sample image file in the repo. JPEG magic bytes (FF D8 FF E0)
# are valid, so the server's upload validator will accept it as image/jpeg.
_TINY_JPEG_B64 = (
    b"/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoM"
    b"DAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsN"
    b"FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAAR"
    b"CAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAA"
    b"AgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkK"
    b"FhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWG"
    b"h4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl"
    b"5ufo6erx8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+qaiiigD/2Q=="
)
TINY_JPEG = base64.b64decode(_TINY_JPEG_B64)


@pytest.fixture
def test_folder(live_client: PresscartClient) -> Iterator[str]:
    """Create a fresh folder; delete it on teardown."""
    import time

    folder = live_client.folders.create({"name": f"pypresscart-test-files-{int(time.time())}"})
    try:
        yield folder.id
    finally:
        # deletion is best-effort cleanup
        with contextlib.suppress(Exception):
            live_client.folders.delete(folder.id)


def test_files_full_round_trip(live_client: PresscartClient, test_folder: str) -> None:
    source_sha = hashlib.sha256(TINY_JPEG).hexdigest()

    # Upload ---------------------------------------------------------------
    import io

    buf = io.BytesIO(TINY_JPEG)
    buf.name = "pypresscart-test.jpg"
    uploaded_resp = live_client.files.upload(buf, folder_id=test_folder)
    assert isinstance(uploaded_resp, UploadFilesResponse)
    assert len(uploaded_resp.files) == 1
    uploaded = uploaded_resp.files[0]
    assert uploaded.id
    assert uploaded.mime_type == "image/jpeg", (
        f"server identified MIME as {uploaded.mime_type}, expected image/jpeg; sniffer regression?"
    )
    assert uploaded.folder_id == test_folder

    file_id = uploaded.id
    try:
        # Read back ----------------------------------------------------------
        got = live_client.files.get(file_id)
        assert isinstance(got, File)
        assert got.id == file_id
        assert got.folder_id == test_folder

        # List scoped to folder ---------------------------------------------
        scoped = live_client.files.list(folder_id=test_folder)
        assert any(f.id == file_id for f in scoped.records)

        # Download + byte-for-byte match ------------------------------------
        downloaded = live_client.files.download(file_id)
        assert hashlib.sha256(downloaded).hexdigest() == source_sha, (
            "downloaded bytes do not match the uploaded file"
        )

        # Move to root (requires explicit null — dict, not Pydantic model) --
        mv: Any = live_client.files.move({"file_ids": [file_id], "folder_id": None})
        assert mv.moved_count == 1
        assert live_client.files.get(file_id).folder_id is None

        # Move back ---------------------------------------------------------
        mv = live_client.files.move(MoveFilesRequest(file_ids=[file_id], folder_id=test_folder))
        assert mv.moved_count == 1
        assert live_client.files.get(file_id).folder_id == test_folder
    finally:
        # Delete the file always; the folder fixture cleans itself up.
        with contextlib.suppress(Exception):
            live_client.files.delete(file_id)
