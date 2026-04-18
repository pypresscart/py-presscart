"""Auth resource: ``GET /auth/token``."""

from __future__ import annotations

from typing import Any

from pypresscart.models.auth import TokenInfo
from pypresscart.resources._base import ResourceBase


class AuthResource(ResourceBase):
    """Authentication endpoints."""

    def whoami(self, *, as_json: bool | None = None) -> TokenInfo | dict[str, Any]:
        """Verify the current API token. Required scope: any valid token.

        See: https://docs.presscart.com/getting-started/authentication
        """
        payload = self._client._request("GET", "/auth/token")
        return self._parse(payload, TokenInfo, as_json)
