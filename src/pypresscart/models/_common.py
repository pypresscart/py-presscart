"""Shared enums and generic pagination envelope."""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

T = TypeVar("T")


class ChannelType(str, Enum):
    WEBSITE = "WEBSITE"
    NEWSLETTER = "NEWSLETTER"
    INSTAGRAM = "INSTAGRAM"
    LINKEDIN = "LINKEDIN"
    YOUTUBE = "YOUTUBE"
    TIKTOK = "TIKTOK"
    TWITTER_X = "TWITTER_X"
    PODCAST = "PODCAST"
    OTHER = "OTHER"


class PlacementType(str, Enum):
    FULL_FEATURE = "FULL_FEATURE"
    PRESS_RELEASE = "PRESS_RELEASE"
    MENTION = "MENTION"
    QUOTE = "QUOTE"
    LISTICLE = "LISTICLE"


class OutletStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    PENDING_AGREEMENT = "PENDING_AGREEMENT"
    REJECTED = "REJECTED"
    ARCHIVED = "ARCHIVED"
    SUSPENDED = "SUSPENDED"


class TokenType(str, Enum):
    FULL_ACCESS = "full_access"
    CUSTOM = "custom"
    READ_ONLY = "read_only"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PresscartModel(BaseModel):
    """Base for all models in this package. Permissive on unknown fields for forward compat."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def _coerce_empty_strings(cls, data: Any) -> Any:
        """Normalize empty strings to ``None`` before type coercion.

        The Presscart API occasionally returns ``""`` instead of ``null`` for
        fields that are semantically optional bools, numbers, or datetimes.
        Pydantic's strict parsers reject that; treating it as ``None`` is the
        pragmatic choice since no endpoint documents ``""`` as meaningful.
        """
        if not isinstance(data, dict):
            return data
        return {k: (None if isinstance(v, str) and v == "" else v) for k, v in data.items()}


class Paginated(PresscartModel, Generic[T]):
    """Standard Presscart paginated envelope."""

    records: Sequence[T] = Field(default_factory=list)
    total_records: int | None = None
    total_pages: int | None = None
    current_page: int | None = None
    next_page: int | None = None
    previous_page: int | None = None


class Tag(PresscartModel):
    name: str


class Price(PresscartModel):
    unit_amount: float
    currency: str | None = None
    pricing_tier: str | None = None


class IncludeItem(PresscartModel):
    channel_type: ChannelType | str | None = None
    placement_type: PlacementType | str | None = None


class Disclaimer(PresscartModel):
    id: str | None = None
    name: str | None = None
    description: str | None = None


def serialize_filters(prefix: str, values: dict[str, Any] | None) -> dict[str, Any]:
    """Turn a dict into ``prefix[key]=value`` query params (server's expected shape).

    List values are emitted as ``prefix[key][]=v1&prefix[key][]=v2`` (PHP/Rails
    bracket notation) — the Presscart API requires that form for array filters
    like ``channel_types``, ``tags``, ``product_ids``.
    """
    if not values:
        return {}
    out: dict[str, Any] = {}
    for key, val in values.items():
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            out[f"{prefix}[{key}][]"] = list(val)
        else:
            out[f"{prefix}[{key}]"] = val
    return out


__all__ = [
    "ChannelType",
    "Disclaimer",
    "IncludeItem",
    "OutletStatus",
    "Paginated",
    "PlacementType",
    "PresscartModel",
    "Price",
    "SortOrder",
    "Tag",
    "TokenType",
    "serialize_filters",
]
