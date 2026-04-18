"""Outlet resource: ``/outlets`` + related location / tag / disclaimer endpoints."""

from __future__ import annotations

from typing import Any

from pypresscart.models._common import Paginated, Tag, serialize_filters
from pypresscart.models.outlets import (
    CitiesResponse,
    CountriesResponse,
    DisclaimerRecord,
    Outlet,
    OutletListing,
    StatesResponse,
)
from pypresscart.resources._base import ResourceBase


class OutletsResource(ResourceBase):
    """Endpoints for browsing outlets and their metadata."""

    def list(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        filters: dict[str, Any] | None = None,
        as_json: bool | None = None,
    ) -> Paginated[OutletListing] | dict[str, Any]:
        """List outlets. Required scope: ``outlets.lists``."""
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        params.update(serialize_filters("filters", filters))
        payload = self._client._request("GET", "/outlets", params=params)
        return self._parse_paginated(payload, OutletListing, as_json)

    def get(
        self,
        outlet_id: str,
        *,
        as_json: bool | None = None,
    ) -> Outlet | dict[str, Any]:
        """Get a single outlet by id. Required scope: ``outlets.read``."""
        payload = self._client._request("GET", f"/outlets/{outlet_id}")
        return self._parse(payload, Outlet, as_json)

    def list_products(
        self,
        outlet_id: str,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        filters: dict[str, Any] | None = None,
        as_json: bool | None = None,
    ) -> Paginated[OutletListing] | dict[str, Any]:
        """List products for one outlet. Required scope: ``outlets.read``."""
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        params.update(serialize_filters("filters", filters))
        payload = self._client._request("GET", f"/outlets/{outlet_id}/products", params=params)
        return self._parse_paginated(payload, OutletListing, as_json)

    def list_countries(
        self,
        *,
        country: str | None = None,
        as_json: bool | None = None,
    ) -> CountriesResponse | dict[str, Any]:
        """List available outlet countries. Required scope: ``outlets.read``."""
        payload = self._client._request(
            "GET", "/outlets/locations/countries", params={"country": country}
        )
        return self._parse(payload, CountriesResponse, as_json)

    def list_states(
        self,
        *,
        country: str | None = None,
        as_json: bool | None = None,
    ) -> StatesResponse | dict[str, Any]:
        """List available outlet states (optionally filtered by country). Scope: ``outlets.read``."""
        payload = self._client._request(
            "GET", "/outlets/locations/states", params={"country": country}
        )
        return self._parse(payload, StatesResponse, as_json)

    def list_cities(
        self,
        *,
        country: str | None = None,
        state: str | None = None,
        as_json: bool | None = None,
    ) -> CitiesResponse | dict[str, Any]:
        """List available outlet cities. Required scope: ``outlets.read``."""
        payload = self._client._request(
            "GET",
            "/outlets/locations/cities",
            params={"country": country, "state": state},
        )
        return self._parse(payload, CitiesResponse, as_json)

    def list_tags(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        filters: dict[str, Any] | None = None,
        as_json: bool | None = None,
    ) -> Paginated[Tag] | dict[str, Any]:
        """List available tags. Required scope: ``tags.lists``."""
        params: dict[str, Any] = {"limit": limit, "page": page}
        params.update(serialize_filters("filters", filters))
        payload = self._client._request("GET", "/tags", params=params)
        return self._parse_paginated(payload, Tag, as_json)

    def list_disclaimers(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        filters: dict[str, Any] | None = None,
        as_json: bool | None = None,
    ) -> Paginated[DisclaimerRecord] | dict[str, Any]:
        """List outlet disclaimers. Required scope: ``outlet_disclaimers.lists``."""
        params: dict[str, Any] = {"limit": limit, "page": page}
        params.update(serialize_filters("filters", filters))
        payload = self._client._request("GET", "/outlet-disclaimers", params=params)
        return self._parse_paginated(payload, DisclaimerRecord, as_json)
