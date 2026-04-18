"""Tests enforcing the dual-mode invariant: Pydantic by default, dict on ``as_json=True``
and via ``response_mode='json'`` client default.
"""

from __future__ import annotations

import responses

from pypresscart import (
    Article,
    Campaign,
    File,
    Folder,
    Order,
    Outlet,
    PresscartClient,
    Product,
    Profile,
    TokenInfo,
)
from tests.conftest import BASE_URL


def _setup(mocked: responses.RequestsMock) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        json={"source": "api_token", "team_id": "t", "token_type": "custom", "scopes": []},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/outlets/out_1",
        json={"id": "out_1", "name": "Ink", "outlet_channels": [], "tags": []},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/products/prod_1",
        json={"id": "prod_1", "name": "Listing"},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/orders/ord_1",
        json={"id": "ord_1", "status": "PAID", "line_items": []},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/campaigns/cmp_1",
        json={"id": "cmp_1", "name": "L", "profile_id": "p"},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/articles/art_1",
        json={"id": "art_1", "name": "hi"},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/files/file_1",
        json={"id": "file_1", "name": "doc.pdf"},
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/teams/team_1/profiles",
        json={
            "records": [{"id": "prof_1", "name": "Brand"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/folders",
        json={
            "records": [{"id": "fld_1", "name": "Drafts"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )


def test_pydantic_mode_by_default(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0)
    _setup(mocked)
    assert isinstance(c.auth.whoami(), TokenInfo)
    assert isinstance(c.outlets.get("out_1"), Outlet)
    assert isinstance(c.products.get("prod_1"), Product)
    assert isinstance(c.orders.get("ord_1"), Order)
    assert isinstance(c.campaigns.get("cmp_1"), Campaign)
    assert isinstance(c.articles.get("art_1"), Article)
    assert isinstance(c.files.get("file_1"), File)
    assert isinstance(
        c.profiles.list_team_profiles("team_1").records[0],  # type: ignore[union-attr]
        Profile,
    )
    assert isinstance(c.folders.list().records[0], Folder)  # type: ignore[union-attr]


def test_per_call_json_override(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0)
    _setup(mocked)
    assert isinstance(c.auth.whoami(as_json=True), dict)
    assert isinstance(c.outlets.get("out_1", as_json=True), dict)
    assert isinstance(c.products.get("prod_1", as_json=True), dict)
    assert isinstance(c.orders.get("ord_1", as_json=True), dict)
    assert isinstance(c.campaigns.get("cmp_1", as_json=True), dict)


def test_client_default_json_mode(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0, response_mode="json")
    _setup(mocked)
    assert isinstance(c.auth.whoami(), dict)
    assert isinstance(c.folders.list(), dict)


def test_per_call_can_force_pydantic(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0, response_mode="json")
    _setup(mocked)
    assert isinstance(c.auth.whoami(as_json=False), TokenInfo)
