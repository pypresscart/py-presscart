"""Products resource: ``/products`` endpoints."""

from __future__ import annotations

from typing import Any

from pypresscart.models._common import Paginated, serialize_filters
from pypresscart.models.products import Product, ProductCategoryCount, ProductListing
from pypresscart.resources._base import ResourceBase


class ProductsResource(ResourceBase):
    """Product endpoints."""

    def get(
        self,
        product_id: str,
        *,
        as_json: bool | None = None,
    ) -> Product | dict[str, Any]:
        """Get a product by id. Required scope: ``products.read``."""
        payload = self._client._request("GET", f"/products/{product_id}")
        return self._parse(payload, Product, as_json)

    def list_listings(
        self,
        *,
        limit: int = 25,
        page: int = 1,
        sort_by: str | None = None,
        order_by: str | None = None,
        filters: dict[str, Any] | None = None,
        as_json: bool | None = None,
    ) -> Paginated[ProductListing] | dict[str, Any]:
        """List products across outlets. Required scope: ``products.read``."""
        params: dict[str, Any] = {
            "limit": limit,
            "page": page,
            "sort_by": sort_by,
            "order_by": order_by,
        }
        params.update(serialize_filters("filters", filters))
        payload = self._client._request("GET", "/products/listings", params=params)
        return self._parse_paginated(payload, ProductListing, as_json)

    def list_categories(
        self,
        *,
        as_json: bool | None = None,
    ) -> list[ProductCategoryCount] | list[dict[str, Any]]:
        """List product category counts. Required scope: ``products.read``."""
        payload = self._client._request("GET", "/products/categories")
        return self._parse_list(payload, ProductCategoryCount, as_json)
