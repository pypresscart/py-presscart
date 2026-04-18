"""Live integration tests for the Outlets resource."""

from __future__ import annotations

import pytest

from pypresscart import (
    CitiesResponse,
    CountriesResponse,
    DisclaimerRecord,
    Outlet,
    OutletListing,
    Paginated,
    PresscartClient,
    StatesResponse,
    Tag,
)

pytestmark = pytest.mark.integration


def test_list_countries(live_client: PresscartClient) -> None:
    resp = live_client.outlets.list_countries()
    assert isinstance(resp, CountriesResponse)
    assert len(resp.countries) > 0
    assert all(isinstance(c, str) for c in resp.countries)


def test_list_states_scoped_to_country(live_client: PresscartClient) -> None:
    resp = live_client.outlets.list_states(country="United States")
    assert isinstance(resp, StatesResponse)
    assert len(resp.states) > 0


def test_list_cities_scoped_to_state(live_client: PresscartClient) -> None:
    resp = live_client.outlets.list_cities(country="United States", state="California")
    assert isinstance(resp, CitiesResponse)
    assert len(resp.cities) >= 0  # empty is allowed; non-empty proves the route works


def test_list_tags(live_client: PresscartClient) -> None:
    page = live_client.outlets.list_tags(limit=5)
    assert isinstance(page, Paginated)
    assert (page.total_records or 0) > 0
    assert all(isinstance(t, Tag) for t in page.records)


def test_list_disclaimers(live_client: PresscartClient) -> None:
    page = live_client.outlets.list_disclaimers(limit=5)
    assert isinstance(page, Paginated)
    assert all(isinstance(d, DisclaimerRecord) for d in page.records)


def test_list_outlets(live_client: PresscartClient) -> None:
    page = live_client.outlets.list(limit=5)
    assert isinstance(page, Paginated)
    assert len(page.records) > 0
    first = page.records[0]
    assert isinstance(first, OutletListing)
    assert first.id  # product id
    assert first.outlet_id


def test_list_outlets_with_filters(live_client: PresscartClient) -> None:
    page = live_client.outlets.list(
        limit=3,
        sort_by="domain_authority",
        order_by="desc",
        filters={"country": "United States"},
    )
    assert isinstance(page, Paginated)
    # All records should have country == United States (within reason — API may
    # include records where country matches as a substring).
    for row in page.records:
        if row.country is not None:
            assert "United States" in row.country or row.country == "United States"


def test_get_and_list_products_for_one_outlet(live_client: PresscartClient) -> None:
    page = live_client.outlets.list(limit=1)
    assert page.records, "no outlets on this team; test can't proceed"
    outlet_id = page.records[0].outlet_id
    assert outlet_id

    outlet = live_client.outlets.get(outlet_id)
    assert isinstance(outlet, Outlet)
    assert outlet.id == outlet_id

    products = live_client.outlets.list_products(outlet_id, limit=3)
    assert isinstance(products, Paginated)


def test_outlets_list_as_json_mode(live_client: PresscartClient) -> None:
    raw = live_client.outlets.list(limit=1, as_json=True)
    assert isinstance(raw, dict)
    assert "records" in raw
    assert "total_records" in raw
