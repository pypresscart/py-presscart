"""Live whoami sanity check."""

from __future__ import annotations

import pytest

from pypresscart import PresscartClient, TokenInfo

pytestmark = pytest.mark.integration


def test_whoami(live_client: PresscartClient) -> None:
    info = live_client.auth.whoami()
    assert isinstance(info, TokenInfo)
    assert info.team_id, "whoami response missing team_id"
    assert info.token_type in {"full_access", "custom", "read_only", None}
    # scopes may be empty for full_access tokens
    assert isinstance(info.scopes, list)


def test_whoami_as_json(live_client: PresscartClient) -> None:
    raw = live_client.auth.whoami(as_json=True)
    assert isinstance(raw, dict)
    assert "team_id" in raw
