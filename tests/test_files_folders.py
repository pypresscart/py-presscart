from __future__ import annotations

import io
import json

import responses

from pypresscart import (
    DisclaimerRecord,
    File,
    Folder,
    MoveFilesRequest,
    PresscartClient,
)
from tests.conftest import BASE_URL


def test_list_files(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/files",
        json={
            "records": [{"id": "f_1", "name": "a.pdf"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.files.list(q="a")
    assert isinstance(page.records[0], File)  # type: ignore[union-attr]


def test_upload_files_from_fileobj(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.POST,
        f"{BASE_URL}/files/upload",
        json={"files": [{"id": "f_1", "name": "a.txt"}]},
    )
    buf = io.BytesIO(b"hello")
    buf.name = "a.txt"
    resp = client.files.upload(buf, folder_id="fld_1")
    assert resp.files[0].id == "f_1"  # type: ignore[union-attr]
    req = mocked.calls[0].request
    ctype = req.headers.get("Content-Type", "")
    assert ctype.startswith("multipart/form-data")


def test_upload_sends_content_type_from_filename(
    mocked: responses.RequestsMock, client: PresscartClient, tmp_path
) -> None:
    """Server-side validation checks the multipart Content-Type, so we need
    to send one explicitly — not let requests default to text/plain."""
    img = tmp_path / "avatar.jpg"
    img.write_bytes(b"\xff\xd8\xff")  # JPEG magic bytes (content doesn't matter)
    mocked.add(
        responses.POST,
        f"{BASE_URL}/files/upload",
        json={"files": [{"id": "f_1", "name": "avatar.jpg"}]},
    )
    client.files.upload(img)
    body = mocked.calls[0].request.body
    body_str = body.decode("latin-1") if isinstance(body, bytes) else str(body)
    assert "Content-Type: image/jpeg" in body_str
    assert "Content-Type: text/plain" not in body_str


def test_move_files(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(responses.POST, f"{BASE_URL}/files/move", json={"moved_count": 2})
    resp = client.files.move(MoveFilesRequest(file_ids=["a", "b"], folder_id="fld_1"))
    assert resp.moved_count == 2  # type: ignore[union-attr]
    sent = json.loads(mocked.calls[0].request.body)
    assert sent["file_ids"] == ["a", "b"]


def test_folder_crud(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.POST,
        f"{BASE_URL}/folders",
        json={"id": "fld_1", "name": "Drafts"},
    )
    mocked.add(
        responses.PATCH,
        f"{BASE_URL}/folders/fld_1",
        json={"id": "fld_1", "name": "Archive"},
    )
    mocked.add(responses.DELETE, f"{BASE_URL}/folders/fld_1", json={"success": True})

    created = client.folders.create({"name": "Drafts"})
    assert isinstance(created, Folder)
    renamed = client.folders.rename("fld_1", {"name": "Archive"})
    assert renamed.name == "Archive"  # type: ignore[union-attr]
    deleted = client.folders.delete("fld_1")
    assert deleted.success is True  # type: ignore[union-attr]


def test_list_disclaimers(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/outlet-disclaimers",
        json={
            "records": [{"id": "d_1", "name": "sponsored"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.outlets.list_disclaimers()
    assert isinstance(page.records[0], DisclaimerRecord)  # type: ignore[union-attr]
