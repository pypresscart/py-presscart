from __future__ import annotations

import responses

from pypresscart import Outlet, OutletListing, PresscartClient
from tests.conftest import BASE_URL


def test_list_outlets_with_filters(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/outlets",
        json={
            "records": [
                {
                    "id": "prod_1",
                    "outlet_id": "out_1",
                    "name": "Ink",
                    "channels": [],
                    "tags": [],
                    "prices": [],
                }
            ],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.outlets.list(limit=5, filters={"search": "ink"})
    assert page.current_page == 1  # type: ignore[union-attr]
    assert isinstance(page.records[0], OutletListing)  # type: ignore[union-attr]
    assert page.records[0].outlet_id == "out_1"  # type: ignore[union-attr]

    url = mocked.calls[0].request.url
    assert "filters%5Bsearch%5D=ink" in url or "filters[search]=ink" in url


def test_get_outlet(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/outlets/out_1",
        json={"id": "out_1", "name": "Ink", "outlet_channels": [], "tags": []},
    )
    outlet = client.outlets.get("out_1")
    assert isinstance(outlet, Outlet)
    assert outlet.name == "Ink"


def test_list_countries(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/outlets/locations/countries",
        json={"countries": ["US", "CA"]},
    )
    resp = client.outlets.list_countries()
    assert resp.countries == ["US", "CA"]  # type: ignore[union-attr]


def test_list_tags_json_mode(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/tags",
        json={
            "records": [{"name": "tech"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    raw = client.outlets.list_tags(as_json=True)
    assert isinstance(raw, dict)
    assert raw["records"][0]["name"] == "tech"
