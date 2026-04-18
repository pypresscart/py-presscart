"""Order item models."""

from __future__ import annotations

from datetime import datetime

from pypresscart.models._common import IncludeItem, PresscartModel
from pypresscart.models.orders import OutletRef


class OrderItemWriter(PresscartModel):
    id: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class OrderItemClient(PresscartModel):
    first_name: str | None = None
    last_name: str | None = None


class OrderItemCampaignRef(PresscartModel):
    id: str | None = None
    name: str | None = None
    profile_id: str | None = None


class OrderItemArticle(PresscartModel):
    id: str | None = None
    name: str | None = None
    campaign: OrderItemCampaignRef | None = None
    writer: OrderItemWriter | None = None


class OrderItem(PresscartModel):
    """Record returned by ``GET /order-items``."""

    id: str
    referrer_id: str | None = None
    referrer_team_id: str | None = None
    product_id: str | None = None
    commission_amount: float | None = None
    commission_date_paid: datetime | None = None
    commission_status: str | None = None
    is_accounting_completed: bool | None = None
    is_publisher_paid: bool | None = None
    is_reseller_paid: bool | None = None
    refund_required: bool | None = None
    is_refunded: bool | None = None
    refund_date: datetime | None = None
    refund_method: str | None = None
    refund_reference: str | None = None
    vendor_invoice_id: str | None = None
    vendor_cost: float | None = None
    vendor_invoice_date: datetime | None = None
    vendor_paid_date: datetime | None = None
    vendor_invoice_url: str | None = None
    accounting_completion_date: datetime | None = None
    publisher_paid_date: datetime | None = None
    reseller_paid_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    order_id: str | None = None
    client_id: str | None = None
    date_paid: datetime | None = None
    sale_price: float | None = None
    product_name: str | None = None
    product_price: float | None = None
    product_type: str | None = None
    article_id: str | None = None
    article: OrderItemArticle | None = None
    internal_cost: float | None = None
    reseller_price: float | None = None
    client: OrderItemClient | None = None
    outlet: OutletRef | None = None


class ProfileOrderItem(PresscartModel):
    """Item returned by ``GET /profiles/{profile_id}/order-items`` (non-paginated list)."""

    id: str
    name: str | None = None
    description: str | None = None
    is_add_on: bool | None = None
    profile_id: str | None = None
    type: str | None = None
    campaign_id: str | None = None
    product_id: str | None = None
    min_delivery_days: int | None = None
    max_delivery_days: int | None = None
    outlet: OutletRef | None = None
    includes: list[IncludeItem] = []


__all__ = [
    "OrderItem",
    "OrderItemArticle",
    "OrderItemCampaignRef",
    "OrderItemClient",
    "OrderItemWriter",
    "ProfileOrderItem",
]
