"""Internal HTTP transport: request dispatch, retry, and error mapping.

Public consumers should use :class:`presscart.PresscartClient` instead.
"""

from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING, Any

import requests

from pypresscart.exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionError,
    PresscartAPIError,
    PresscartTransportError,
    RateLimitError,
    ServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


_RETRY_STATUSES: frozenset[int] = frozenset({429, 500, 502, 503, 504})


def _parse_retry_after(value: str | None) -> float | None:
    """Parse ``Retry-After`` header (seconds or HTTP-date). Returns None if unparseable."""
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _compute_backoff(
    attempt: int,
    *,
    base: float,
    cap: float,
    jitter: float,
    retry_after: float | None,
) -> float:
    if retry_after is not None and retry_after > 0:
        return min(retry_after, cap)
    raw: float = min(cap, base * (2**attempt))
    if jitter > 0:
        raw += raw * jitter * random.random()
    return float(raw)


def _map_error(
    status: int, payload: dict[str, Any] | None, retry_after: float | None
) -> PresscartAPIError:
    name = (payload or {}).get("name")
    message = (payload or {}).get("message") or ""
    issues = (payload or {}).get("issues")

    if status == 400:
        if issues:
            return ValidationError(
                status, message or "Validation failed", name=name, payload=payload
            )
        return BadRequestError(status, message or "Bad request", name=name, payload=payload)
    if status == 401:
        return AuthenticationError(status, message or "Unauthorized", name=name, payload=payload)
    if status == 403:
        return PermissionError(status, message or "Forbidden", name=name, payload=payload)
    if status == 404:
        return NotFoundError(status, message or "Not found", name=name, payload=payload)
    if status == 429:
        return RateLimitError(
            status,
            message or "Rate limited",
            name=name,
            payload=payload,
            retry_after=retry_after,
        )
    if 500 <= status < 600:
        return ServerError(status, message or "Server error", name=name, payload=payload)
    return PresscartAPIError(status, message or f"HTTP {status}", name=name, payload=payload)


class Transport:
    """Thin wrapper around ``requests.Session`` adding retry + error mapping."""

    def __init__(
        self,
        *,
        session: requests.Session,
        base_url: str,
        headers: Mapping[str, str],
        timeout: float,
        max_retries: int,
        retry_backoff_base: float,
        retry_backoff_max: float,
        retry_jitter: float,
        sleep: Any = time.sleep,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._default_headers = dict(headers)
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_backoff_base = retry_backoff_base
        self._retry_backoff_max = retry_backoff_max
        self._retry_jitter = retry_jitter
        self._sleep = sleep

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: Mapping[str, str] | None = None,
        stream: bool = False,
    ) -> requests.Response:
        """Send a request with retry. Returns the final ``requests.Response``.

        Raises :class:`PresscartAPIError` subclasses on 4xx/5xx after retries are
        exhausted, or :class:`PresscartTransportError` on network failures.
        """
        url = path if path.startswith("http") else f"{self._base_url}{path}"
        merged_headers = dict(self._default_headers)
        if headers:
            merged_headers.update(headers)

        attempt = 0
        while True:
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=_clean_params(params),
                    json=json,
                    data=data,
                    files=files,
                    headers=merged_headers,
                    timeout=self._timeout,
                    stream=stream,
                )
            except requests.exceptions.RequestException as exc:
                if attempt >= self._max_retries:
                    raise PresscartTransportError(str(exc)) from exc
                delay = _compute_backoff(
                    attempt,
                    base=self._retry_backoff_base,
                    cap=self._retry_backoff_max,
                    jitter=self._retry_jitter,
                    retry_after=None,
                )
                self._sleep(delay)
                attempt += 1
                continue

            if response.status_code < 400:
                return response

            payload = _safe_json(response)
            retry_after = _parse_retry_after(response.headers.get("Retry-After"))
            err = _map_error(response.status_code, payload, retry_after)

            is_retryable = response.status_code in _RETRY_STATUSES
            if is_retryable and attempt < self._max_retries:
                delay = _compute_backoff(
                    attempt,
                    base=self._retry_backoff_base,
                    cap=self._retry_backoff_max,
                    jitter=self._retry_jitter,
                    retry_after=retry_after,
                )
                self._sleep(delay)
                attempt += 1
                continue

            raise err


def _safe_json(response: requests.Response) -> dict[str, Any] | None:
    try:
        data = response.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else {"data": data}


def _clean_params(params: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Drop keys whose values are None so they don't appear in the query string."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
