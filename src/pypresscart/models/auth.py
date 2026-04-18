"""Auth models."""

from __future__ import annotations

from pypresscart.models._common import PresscartModel, TokenType


class TokenInfo(PresscartModel):
    """Response from ``GET /auth/token``."""

    source: str | None = None
    team_id: str | None = None
    token_type: TokenType | str | None = None
    scopes: list[str] = []
    pro_pricing_enabled: bool | None = None


__all__ = ["TokenInfo"]
