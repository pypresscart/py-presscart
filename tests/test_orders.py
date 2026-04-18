from __future__ import annotations

import json

import responses

from pypresscart import CheckoutLineItem, CheckoutRequest, Order, PresscartClient
from tests.conftest import BASE_URL


def _order_payload() -> dict:
    return {
        "id": "ord_1",
        "profile_id": "prof_1",
        "status": "CREATED",
        "total": 50000,
        "subtotal": 50000,
        "line_items": [{"id": "li_1", "product_id": "prod_1", "quantity": 1, "price": 50000}],
    }


def test_list_orders(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/orders",
        json={
            "records": [_order_payload()],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.orders.list()
    assert isinstance(page.records[0], Order)  # type: ignore[union-attr]
    assert page.records[0].id == "ord_1"  # type: ignore[union-attr]


def test_create_checkout_with_pydantic_body(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    mocked.add(responses.POST, f"{BASE_URL}/orders/checkout", json=_order_payload())
    body = CheckoutRequest(
        profile_id="prof_1",
        line_items=[CheckoutLineItem(product_id="prod_1", quantity=1)],
    )
    order = client.orders.create_checkout(body)
    assert isinstance(order, Order)
    sent = json.loads(mocked.calls[0].request.body)
    assert sent["profile_id"] == "prof_1"
    assert sent["line_items"][0]["product_id"] == "prod_1"


def test_create_checkout_with_dict_body(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    mocked.add(responses.POST, f"{BASE_URL}/orders/checkout", json=_order_payload())
    raw = client.orders.create_checkout(
        {
            "profile_id": "prof_1",
            "line_items": [{"product_id": "prod_1", "quantity": 1, "is_add_on": False}],
        },
        as_json=True,
    )
    assert isinstance(raw, dict)
    assert raw["id"] == "ord_1"
