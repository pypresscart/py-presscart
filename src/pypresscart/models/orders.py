"""Order models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pypresscart.models._common import PresscartModel


class CheckoutLineItem(PresscartModel):
    """A line item in a checkout request."""

    product_id: str
    quantity: int = 1
    is_add_on: bool = False
    linked_order_line_item_id: str | None = None


class CheckoutRequest(PresscartModel):
    """Body for ``POST /orders/checkout``."""

    profile_id: str
    line_items: list[CheckoutLineItem]
    discount: float | None = 0


class OutletRef(PresscartModel):
    """Minimal outlet reference embedded in line items."""

    id: str | None = None
    name: str | None = None
    logo: str | None = None
    website_url: str | None = None


class LineItem(PresscartModel):
    """A line item on a returned order."""

    id: str
    order_id: str | None = None
    product_id: str
    quantity: int
    price: float | None = None
    is_add_on: bool | None = None
    linked_order_line_item_id: str | None = None
    name: str | None = None
    product_type_name: str | None = None
    type_id: str | None = None
    product_type_prefix: str | None = None
    outlet: OutletRef | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class TeamRef(PresscartModel):
    name: str | None = None
    contact_email: str | None = None


class Order(PresscartModel):
    """Order returned by ``GET /orders`` / ``/orders/{id}`` and ``POST /orders/checkout``."""

    id: str
    profile_id: str | None = None
    client_id: str | None = None
    checkout_by_id: str | None = None
    team_id: str | None = None
    total: float | None = None
    subtotal: float | None = None
    processing_fee: float | None = None
    discount: float | None = None
    credits_applied: float | None = None
    coupon: str | None = None
    client_secret: str | None = None
    date_paid: datetime | None = None
    status: str | None = None
    reference_number: str | None = None
    external_reference_number: str | None = None
    customer_invoice_id: str | None = None
    customer_invoice_source: str | None = None
    customer_invoice_date: datetime | None = None
    customer_invoice_url: str | None = None
    is_guest_order: bool | None = None
    guest_email: str | None = None
    account_owner_email: str | None = None
    guest_stripe_customer_id: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    team: TeamRef | None = None
    checkout_link: str | None = None
    line_items: list[LineItem] = []


__all__ = [
    "CheckoutLineItem",
    "CheckoutRequest",
    "LineItem",
    "Order",
    "OutletRef",
    "TeamRef",
]
