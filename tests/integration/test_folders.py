"""Live integration test for the Folders resource — full round-trip."""

from __future__ import annotations

import contextlib
import time

import pytest

from pypresscart import (
    Folder,
    FolderCreateRequest,
    FolderRenameRequest,
    Paginated,
    PresscartClient,
)

pytestmark = pytest.mark.integration


def test_folders_full_round_trip(live_client: PresscartClient) -> None:
    ts = int(time.time())
    name_a = f"pypresscart-folder-A-{ts}"
    name_b = f"pypresscart-folder-B-{ts}"
    name_a_renamed = f"{name_a}-renamed"

    created_ids: list[str] = []
    try:
        # Create A (Pydantic input) ------------------------------------------
        a = live_client.folders.create(FolderCreateRequest(name=name_a))
        created_ids.append(a.id)
        assert isinstance(a, Folder)
        assert a.name == name_a

        # Create B (dict input) ----------------------------------------------
        b = live_client.folders.create({"name": name_b})
        created_ids.append(b.id)
        assert b.name == name_b

        # List — both visible ------------------------------------------------
        page = live_client.folders.list()
        assert isinstance(page, Paginated)
        names = {f.name for f in page.records}
        assert name_a in names
        assert name_b in names

        # Search scoped to name_a --------------------------------------------
        search = live_client.folders.list(q=name_a)
        assert any(f.name == name_a for f in search.records)
        assert not any(f.name == name_b for f in search.records)

        # Rename A -----------------------------------------------------------
        renamed = live_client.folders.rename(a.id, FolderRenameRequest(name=name_a_renamed))
        assert renamed.name == name_a_renamed

        # Confirm the rename stuck -------------------------------------------
        after = live_client.folders.list(q=name_a_renamed)
        found = next((f for f in after.records if f.id == a.id), None)
        assert found is not None
        assert found.name == name_a_renamed
    finally:
        for fid in created_ids:
            with contextlib.suppress(Exception):
                live_client.folders.delete(fid)


def test_folders_list_as_json(live_client: PresscartClient) -> None:
    raw = live_client.folders.list(as_json=True)
    assert isinstance(raw, dict)
    assert "records" in raw
