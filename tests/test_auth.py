from __future__ import annotations

import responses

from pypresscart import PresscartClient, TokenInfo
from tests.conftest import BASE_URL


def test_whoami_pydantic(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        json={
            "source": "api_token",
            "team_id": "11111111-1111-1111-1111-111111111111",
            "token_type": "custom",
            "scopes": ["products.read"],
            "pro_pricing_enabled": True,
        },
    )
    info = client.auth.whoami()
    assert isinstance(info, TokenInfo)
    assert info.team_id == "11111111-1111-1111-1111-111111111111"
    assert info.scopes == ["products.read"]
    assert info.pro_pricing_enabled is True


def test_whoami_json(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        json={"source": "api_token", "team_id": "t", "token_type": "custom", "scopes": []},
    )
    info = client.auth.whoami(as_json=True)
    assert isinstance(info, dict)
    assert info["team_id"] == "t"
