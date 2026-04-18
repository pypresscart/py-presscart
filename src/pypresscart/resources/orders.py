"""Orders resource: ``/orders`` endpoints."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pypresscart.models._common import Paginated
from pypresscart.models.orders import CheckoutRequest, Order
from pypresscart.resources._base import ResourceBase


class OrdersResource(ResourceBase):
    """Order endpoints (list, get, create checkout)."""

    def list(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        as_json: bool | None = None,
    ) -> Paginated[Order] | dict[str, Any]:
        """List orders for the team. Required scope: ``orders.lists``."""
        params = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        payload = self._client._request("GET", "/orders", params=params)
        return self._parse_paginated(payload, Order, as_json)

    def get(
        self,
        order_id: str,
        *,
        as_json: bool | None = None,
    ) -> Order | dict[str, Any]:
        """Get a single order by id. Required scope: ``orders.read``."""
        payload = self._client._request("GET", f"/orders/{order_id}")
        return self._parse(payload, Order, as_json)

    def create_checkout(
        self,
        body: CheckoutRequest | BaseModel | dict[str, Any],
        *,
        as_json: bool | None = None,
    ) -> Order | dict[str, Any]:
        """Create a checkout order. Required scope: ``orders.create``."""
        payload = self._client._request("POST", "/orders/checkout", json=self._serialize(body))
        return self._parse(payload, Order, as_json)
