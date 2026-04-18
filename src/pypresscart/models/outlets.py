"""Outlet models."""

from __future__ import annotations

from datetime import datetime

from pypresscart.models._common import (
    ChannelType,
    PlacementType,
    PresscartModel,
    Price,
    Tag,
)


class OutletChannelSummary(PresscartModel):
    """Channel summary included in outlet listings."""

    channel_type: ChannelType | str
    placement_type: PlacementType | str
    is_do_follow: bool | None = None
    domain_authority: int | None = None
    domain_ranking: int | None = None
    disclaimer_name: str | None = None
    disclaimer_description: str | None = None


class OutletChannel(PresscartModel):
    """Full outlet channel (from ``GET /outlets/{id}``)."""

    id: str
    outlet_id: str | None = None
    channel_type: ChannelType | str
    placement_type: PlacementType | str
    channel_handle: str | None = None
    channel_url: str | None = None
    social_links: list[str] = []
    is_do_follow: bool | None = None
    domain_authority: int | None = None
    domain_ranking: int | None = None
    do_follow_links_allowed: bool | None = None
    disclaimer_name: str | None = None
    disclaimer_description: str | None = None


class OutletListing(PresscartModel):
    """An item in the ``GET /outlets`` list.

    Note: ``id`` here is a **product id** (what you pass to checkout).
    ``outlet_id`` is what you pass to ``GET /outlets/{outlet_id}``.
    """

    id: str
    outlet_id: str | None = None
    name: str
    description: str | None = None
    requirements: str | None = None
    min_delivery_days: int | None = None
    max_delivery_days: int | None = None
    is_featured: bool | None = None
    created_at: datetime | None = None
    outlet_name: str | None = None
    website_url: str | None = None
    logo: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    channels: list[OutletChannelSummary] = []
    tags: list[Tag] = []
    prices: list[Price] = []


class Outlet(PresscartModel):
    """Response from ``GET /outlets/{outlet_id}``."""

    id: str
    name: str
    description: str | None = None
    website_url: str | None = None
    logo: str | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    is_indexed: bool | None = None
    tags: list[Tag] = []
    outlet_channels: list[OutletChannel] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CountriesResponse(PresscartModel):
    countries: list[str] = []


class StatesResponse(PresscartModel):
    states: list[str] = []


class CitiesResponse(PresscartModel):
    cities: list[str] = []


class DisclaimerRecord(PresscartModel):
    id: str
    name: str | None = None
    description: str | None = None


__all__ = [
    "CitiesResponse",
    "CountriesResponse",
    "DisclaimerRecord",
    "Outlet",
    "OutletChannel",
    "OutletChannelSummary",
    "OutletListing",
    "StatesResponse",
]
