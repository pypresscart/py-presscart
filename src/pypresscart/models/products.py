"""Product models."""

from __future__ import annotations

from datetime import datetime

from pypresscart.models._common import (
    ChannelType,
    IncludeItem,
    PlacementType,
    PresscartModel,
    Price,
    Tag,
)


class Product(PresscartModel):
    """Response from ``GET /products/{product_id}``."""

    id: str
    name: str
    description: str | None = None
    requirements: str | None = None
    min_delivery_days: int | None = None
    max_delivery_days: int | None = None
    is_featured: bool | None = None
    active: bool | None = None
    example_links: list[str] = []
    image: str | None = None
    logo: str | None = None
    example_screenshot: str | None = None
    type_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    prices: list[Price] = []


class ProductListing(PresscartModel):
    """An item in ``GET /products/listings``."""

    id: str
    name: str
    description: str | None = None
    requirements: str | None = None
    min_delivery_days: int | None = None
    max_delivery_days: int | None = None
    is_featured: bool | None = None
    example_links: list[str] = []
    created_at: datetime | None = None
    outlet_id: str | None = None
    outlet_name: str | None = None
    website_url: str | None = None
    logo: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    is_indexed: bool | None = None
    channel_id: str | None = None
    channel_type: ChannelType | str | None = None
    placement_type: PlacementType | str | None = None
    domain_authority: int | None = None
    domain_ranking: int | None = None
    is_do_follow: bool | None = None
    disclaimer: str | None = None
    prices: list[Price] = []
    tags: list[Tag] = []
    includes: list[IncludeItem] = []


class ProductCategoryCount(PresscartModel):
    """An entry in ``GET /products/categories``."""

    type: str
    count: int


__all__ = [
    "Product",
    "ProductCategoryCount",
    "ProductListing",
]
