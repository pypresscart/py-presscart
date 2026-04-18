"""Live integration tests for Orders + Order Items (read-only).

`POST /orders/checkout` is intentionally out of scope — it has real billing
side effects. See tests/integration/README.md.
"""

from __future__ import annotations

import pytest

from pypresscart import Order, OrderItem, Paginated, PresscartClient

pytestmark = pytest.mark.integration


def test_list_orders(live_client: PresscartClient) -> None:
    page = live_client.orders.list(limit=5)
    assert isinstance(page, Paginated)
    if page.records:
        assert all(isinstance(o, Order) for o in page.records)
        # Regression guard for issue #1 — the API returns money fields as
        # dollar floats on /orders. Our models accept float | None.
        for o in page.records:
            assert o.total is None or isinstance(o.total, (int, float))
            assert o.subtotal is None or isinstance(o.subtotal, (int, float))


def test_list_orders_sorted_asc(live_client: PresscartClient) -> None:
    page = live_client.orders.list(limit=3, sort_by="created_at", order_by="asc")
    assert isinstance(page, Paginated)
    if len(page.records) >= 2:
        created = [o.created_at for o in page.records if o.created_at]
        assert created == sorted(created), "created_at not ascending"


def test_get_order_detail(live_client: PresscartClient) -> None:
    page = live_client.orders.list(limit=1)
    if not page.records:
        pytest.skip("no orders on this team")
    order_id = page.records[0].id
    detail = live_client.orders.get(order_id)
    assert isinstance(detail, Order)
    assert detail.id == order_id
    # checkout_link should be present for CREATED orders, absent for PAID.
    if detail.status == "PAID":
        assert detail.date_paid is not None


def test_list_order_items(live_client: PresscartClient) -> None:
    page = live_client.order_items.list(limit=5)
    assert isinstance(page, Paginated)
    if page.records:
        assert all(isinstance(oi, OrderItem) for oi in page.records)
        # internal_cost / reseller_price are documented as null for API tokens.
        for oi in page.records:
            assert oi.internal_cost is None
            assert oi.reseller_price is None


def test_orders_as_json_mode(live_client: PresscartClient) -> None:
    raw = live_client.orders.list(limit=1, as_json=True)
    assert isinstance(raw, dict)
    assert "records" in raw
