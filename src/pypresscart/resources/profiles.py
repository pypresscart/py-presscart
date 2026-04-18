"""Profiles resource: team profiles and per-profile listings."""

from __future__ import annotations

from typing import Any

from pypresscart.models._common import Paginated
from pypresscart.models.campaigns import Campaign
from pypresscart.models.order_items import ProfileOrderItem
from pypresscart.models.orders import Order
from pypresscart.models.profiles import Profile
from pypresscart.resources._base import ResourceBase


class ProfilesResource(ResourceBase):
    """Profile-scoped endpoints."""

    def list_team_profiles(
        self,
        team_id: str,
        *,
        limit: int = 25,
        page: int = 1,
        as_json: bool | None = None,
    ) -> Paginated[Profile] | dict[str, Any]:
        """List all profiles for a team. Required scope: ``profiles.lists``."""
        params = {"limit": limit, "page": page}
        payload = self._client._request("GET", f"/teams/{team_id}/profiles", params=params)
        return self._parse_paginated(payload, Profile, as_json)

    def list_orders(
        self,
        profile_id: str,
        *,
        start_date: str | None = None,
        end_date: str | None = None,
        paid_orders_only: bool | None = None,
        limit: int = 25,
        page: int = 1,
        as_json: bool | None = None,
    ) -> Paginated[Order] | dict[str, Any]:
        """List orders for a single profile. Required scope: ``orders.lists``."""
        params: dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
            "paid_orders_only": paid_orders_only,
            "limit": limit,
            "page": page,
        }
        payload = self._client._request("GET", f"/profiles/{profile_id}/orders", params=params)
        return self._parse_paginated(payload, Order, as_json)

    def list_order_items(
        self,
        profile_id: str,
        *,
        type: str | None = None,
        is_add_on: bool | None = None,
        search: str | None = None,
        aggregate_add_ons: bool | None = None,
        as_json: bool | None = None,
    ) -> list[ProfileOrderItem] | list[dict[str, Any]]:
        """List order items for a profile. Required scope: ``orders.lists``.

        Note: returns a bare JSON array, not the standard paginated envelope.
        """
        params: dict[str, Any] = {
            "type": type,
            "is_add_on": is_add_on,
            "search": search,
            "aggregate_add_ons": aggregate_add_ons,
        }
        payload = self._client._request("GET", f"/profiles/{profile_id}/order-items", params=params)
        return self._parse_list(payload, ProfileOrderItem, as_json)

    def list_campaigns(
        self,
        profile_id: str,
        *,
        limit: int = 25,
        page: int = 1,
        as_json: bool | None = None,
    ) -> Paginated[Campaign] | dict[str, Any]:
        """List campaigns for a profile. Required scope: ``campaigns.lists``."""
        params = {"limit": limit, "page": page}
        payload = self._client._request("GET", f"/profiles/{profile_id}/campaigns", params=params)
        return self._parse_paginated(payload, Campaign, as_json)
