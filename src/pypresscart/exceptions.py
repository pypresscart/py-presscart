"""Exception hierarchy for the presscart client."""

from __future__ import annotations

from typing import Any


class PresscartError(Exception):
    """Base class for all presscart client errors."""


class PresscartTransportError(PresscartError):
    """Network-level failure (timeout, connection reset, DNS, etc.).

    Wraps the underlying ``requests`` exception in ``__cause__``.
    """


class PresscartAPIError(PresscartError):
    """The API returned a non-2xx HTTP status.

    Attributes:
        status_code: HTTP status code returned by the API.
        name: ``name`` field from the error JSON body (e.g. ``"ForbiddenError"``).
        message: Human-readable description from the error body.
        payload: Full parsed JSON body, or ``None`` if the body was not JSON.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        name: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.name = name
        self.message = message
        self.payload: dict[str, Any] = payload or {}
        super().__init__(f"[{status_code}] {name or 'APIError'}: {message}")


class BadRequestError(PresscartAPIError):
    """HTTP 400."""


class ValidationError(BadRequestError):
    """HTTP 400 with field-level ``issues`` payload."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        name: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(status_code, message, name=name, payload=payload)
        raw_issues = (payload or {}).get("issues") or []
        self.issues: list[dict[str, Any]] = list(raw_issues)


class AuthenticationError(PresscartAPIError):
    """HTTP 401."""


class PermissionError(PresscartAPIError):
    """HTTP 403. Token valid but lacks the required scope or team access."""


class NotFoundError(PresscartAPIError):
    """HTTP 404."""


class RateLimitError(PresscartAPIError):
    """HTTP 429. ``retry_after`` is populated from the ``Retry-After`` header when present."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        name: str | None = None,
        payload: dict[str, Any] | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(status_code, message, name=name, payload=payload)
        self.retry_after = retry_after


class ServerError(PresscartAPIError):
    """HTTP 5xx."""


__all__ = [
    "AuthenticationError",
    "BadRequestError",
    "NotFoundError",
    "PermissionError",
    "PresscartAPIError",
    "PresscartError",
    "PresscartTransportError",
    "RateLimitError",
    "ServerError",
    "ValidationError",
]
