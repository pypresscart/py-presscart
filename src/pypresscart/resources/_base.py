"""Base class shared by every resource module."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel

from pypresscart.models._common import Paginated

if TYPE_CHECKING:
    from pypresscart.client import PresscartClient

M = TypeVar("M", bound=BaseModel)


class ResourceBase:
    """Common helpers for resource classes.

    Every resource method must support dual-mode (Pydantic or dict). Use
    :meth:`_serialize` for request inputs and :meth:`_parse` /
    :meth:`_parse_paginated` for response outputs.
    """

    def __init__(self, client: PresscartClient) -> None:
        self._client = client

    @staticmethod
    def _serialize(body: BaseModel | dict[str, Any] | None) -> dict[str, Any] | None:
        if body is None:
            return None
        if isinstance(body, BaseModel):
            return body.model_dump(mode="json", exclude_none=True)
        return dict(body)

    def _parse(
        self,
        payload: dict[str, Any],
        model_cls: type[M],
        as_json: bool | None,
    ) -> M | dict[str, Any]:
        if self._client._resolve_mode(as_json):
            return payload
        return model_cls.model_validate(payload)

    def _parse_paginated(
        self,
        payload: dict[str, Any],
        item_cls: type[M],
        as_json: bool | None,
    ) -> Paginated[M] | dict[str, Any]:
        if self._client._resolve_mode(as_json):
            return payload
        # Paginated is Generic; parameterizing with a TypeVar at runtime is
        # supported by pydantic but not expressible to mypy.
        return Paginated[item_cls].model_validate(payload)  # type: ignore[valid-type]

    def _parse_list(
        self,
        payload: dict[str, Any],
        item_cls: type[M],
        as_json: bool | None,
    ) -> list[M] | list[dict[str, Any]]:
        """For endpoints that return a bare JSON array. The array is wrapped in
        ``{"data": [...]}`` by the transport layer; unwrap here.
        """
        items = payload.get("data", payload)
        if not isinstance(items, list):
            items = []
        if self._client._resolve_mode(as_json):
            return list(items)
        return [item_cls.model_validate(i) for i in items]
