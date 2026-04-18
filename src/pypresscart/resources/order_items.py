"""Order items resource: ``GET /order-items``."""

from __future__ import annotations

from typing import Any

from pypresscart.models._common import Paginated
from pypresscart.models.order_items import OrderItem
from pypresscart.resources._base import ResourceBase


class OrderItemsResource(ResourceBase):
    """Order item endpoints."""

    def list(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        as_json: bool | None = None,
    ) -> Paginated[OrderItem] | dict[str, Any]:
        """List order items for the team. Required scope: ``orders.lists``."""
        params = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        payload = self._client._request("GET", "/order-items", params=params)
        return self._parse_paginated(payload, OrderItem, as_json)
