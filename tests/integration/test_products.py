"""Live integration tests for the Products resource."""

from __future__ import annotations

import pytest

from pypresscart import (
    Paginated,
    PresscartClient,
    Product,
    ProductCategoryCount,
    ProductListing,
)

pytestmark = pytest.mark.integration


def test_list_categories(live_client: PresscartClient) -> None:
    cats = live_client.products.list_categories()
    assert isinstance(cats, list)
    assert all(isinstance(c, ProductCategoryCount) for c in cats)
    # Don't assert non-empty — a fresh team could have zero products in the
    # catalog — but if there are any, the shape should be right.


def test_list_listings_default(live_client: PresscartClient) -> None:
    page = live_client.products.list_listings(limit=5)
    assert isinstance(page, Paginated)
    if page.records:
        assert all(isinstance(p, ProductListing) for p in page.records)


def test_list_listings_with_array_filter(live_client: PresscartClient) -> None:
    """Regression guard for the filters[channel_types][0]=... indexed bracket
    notation. Earlier shapes filters[channel_types]=WEBSITE (issue #5) and
    filters[channel_types][]=WEBSITE were both silently ignored by the API."""
    page = live_client.products.list_listings(limit=3, filters={"channel_types": ["WEBSITE"]})
    assert isinstance(page, Paginated)


def test_list_listings_sorted_cheapest_first(live_client: PresscartClient) -> None:
    page = live_client.products.list_listings(limit=3, sort_by="price", order_by="asc")
    assert isinstance(page, Paginated)
    if len(page.records) >= 2:
        prices = [r.prices[0].unit_amount for r in page.records if r.prices]
        assert prices == sorted(prices), "prices not monotonic ascending"


def test_get_product_by_id(live_client: PresscartClient) -> None:
    page = live_client.products.list_listings(limit=1)
    if not page.records:
        pytest.skip("no products in catalog on this team")
    product = live_client.products.get(page.records[0].id)
    assert isinstance(product, Product)
    assert product.id == page.records[0].id
