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
    # Omitted apply_credits is dropped so the server default (true) stands.
    assert "apply_credits" not in sent


def test_create_checkout_sends_apply_credits_false(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    mocked.add(responses.POST, f"{BASE_URL}/orders/checkout", json=_order_payload())
    body = CheckoutRequest(
        profile_id="prof_1",
        line_items=[CheckoutLineItem(product_id="prod_1", quantity=1)],
        apply_credits=False,
    )
    client.orders.create_checkout(body)
    sent = json.loads(mocked.calls[0].request.body)
    assert sent["apply_credits"] is False


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


def test_create_checkout_parses_line_items_without_id(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    """The live Presscart API doesn't include an `id` on line items in
    the checkout response (line items are only persisted with an id
    once the order is paid, exposed via ``GET /order-items``). The
    ``LineItem`` model must therefore allow ``id`` to be missing.
    """
    payload = {
        "id": "ord_2",
        "profile_id": "prof_1",
        "status": "CREATED",
        "total": 50000,
        "subtotal": 50000,
        "checkout_link": "https://pay.example/abc",
        "line_items": [
            {
                "product_id": "prod_1",
                "quantity": 1,
                "is_add_on": False,
                "linked_order_line_item_id": None,
            }
        ],
    }
    mocked.add(responses.POST, f"{BASE_URL}/orders/checkout", json=payload)
    order = client.orders.create_checkout(
        CheckoutRequest(
            profile_id="prof_1",
            line_items=[CheckoutLineItem(product_id="prod_1", quantity=1)],
        )
    )
    assert isinstance(order, Order)
    assert order.id == "ord_2"
    assert order.checkout_link == "https://pay.example/abc"
    assert len(order.line_items) == 1
    assert order.line_items[0].id is None
    assert order.line_items[0].product_id == "prod_1"


def test_get_order_parses_line_item_includes(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    """``GET /orders/{order_id}`` returns ``includes`` (channel/placement)
    on each line item, plus top-level ``name`` and ``email`` (which the
    list endpoint nests under ``team`` instead). All must parse.
    """
    payload = {
        "id": "ord_3",
        "profile_id": "prof_1",
        "status": "PAID",
        "name": "Acme Corp",
        "email": "team@example.com",
        "line_items": [
            {
                "id": "li_1",
                "order_id": "ord_3",
                "product_id": "prod_1",
                "quantity": 1,
                "price": 1500,
                "is_add_on": False,
                "includes": [{"channel_type": "NEWSLETTER", "placement_type": "MENTION"}],
            }
        ],
    }
    mocked.add(responses.GET, f"{BASE_URL}/orders/ord_3", json=payload)
    order = client.orders.get("ord_3")
    assert isinstance(order, Order)
    assert order.name == "Acme Corp"
    assert order.email == "team@example.com"
    assert order.team is None
    assert order.line_items[0].includes is not None
    assert len(order.line_items[0].includes) == 1
    assert order.line_items[0].includes[0].channel_type == "NEWSLETTER"
    assert order.line_items[0].includes[0].placement_type == "MENTION"


def test_get_order_with_include_outlets_data(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    payload = {
        "id": "ord_4",
        "profile_id": "prof_1",
        "status": "CREATED",
        "line_items": [
            {
                "id": "li_1",
                "order_id": "ord_4",
                "product_id": "prod_1",
                "quantity": 1,
                "price": 125,
                "is_add_on": False,
                "name": "VC Magazine",
                "outlet": {
                    "id": "out_1",
                    "name": "VC Magazine",
                    "logo": "https://cdn.example/logo.png",
                    "website_url": "https://vcmagazine.com/",
                },
                "includes": [{"channel_type": "WEBSITE", "placement_type": "FULL_FEATURE"}],
            }
        ],
    }
    mocked.add(responses.GET, f"{BASE_URL}/orders/ord_4", json=payload)
    order = client.orders.get("ord_4", include_outlets_data=True)
    assert isinstance(order, Order)
    assert mocked.calls[0].request.url.endswith("?include_outlets_data=true")
    outlet = order.line_items[0].outlet
    assert outlet is not None
    assert outlet.id == "out_1"
    assert outlet.name == "VC Magazine"
    assert outlet.website_url == "https://vcmagazine.com/"


def test_get_order_omits_include_outlets_data_when_unset(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    mocked.add(responses.GET, f"{BASE_URL}/orders/ord_5", json=_order_payload())
    client.orders.get("ord_5")
    assert "include_outlets_data" not in mocked.calls[0].request.url
