"""Top-level ``PresscartClient`` — the public entry point for the SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import requests

from pypresscart._transport import Transport
from pypresscart._version import __version__

if TYPE_CHECKING:
    from collections.abc import Mapping

from pypresscart.resources.articles import ArticlesResource
from pypresscart.resources.auth import AuthResource
from pypresscart.resources.campaigns import CampaignsResource
from pypresscart.resources.files import FilesResource
from pypresscart.resources.folders import FoldersResource
from pypresscart.resources.order_items import OrderItemsResource
from pypresscart.resources.orders import OrdersResource
from pypresscart.resources.outlets import OutletsResource
from pypresscart.resources.products import ProductsResource
from pypresscart.resources.profiles import ProfilesResource

ResponseMode = Literal["pydantic", "json"]


class PresscartClient:
    """HTTP client for the Presscart API.

    Example:
        >>> client = PresscartClient(api_token="pc_...")
        >>> whoami = client.auth.whoami()
        >>> outlets = client.outlets.list(limit=10)

    Parameters:
        api_token: Bearer token. Required.
        base_url: API base URL. Defaults to ``https://api.presscart.com``.
        timeout: Per-request timeout in seconds.
        max_retries: Additional attempts on 429/5xx/network errors.
        retry_backoff_base: Base seconds for exponential backoff.
        retry_backoff_max: Max backoff cap.
        retry_jitter: Fractional jitter added to each backoff.
        response_mode: ``"pydantic"`` (default) returns typed models;
            ``"json"`` returns raw dicts. Individual method calls may
            override with ``as_json=True``.
        user_agent: Custom ``User-Agent`` header.
        session: Pre-configured ``requests.Session`` to reuse.
    """

    def __init__(
        self,
        api_token: str,
        *,
        base_url: str = "https://api.presscart.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff_base: float = 0.25,
        retry_backoff_max: float = 4.0,
        retry_jitter: float = 0.1,
        response_mode: ResponseMode = "pydantic",
        user_agent: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        if not api_token:
            raise ValueError("api_token is required")
        if response_mode not in ("pydantic", "json"):
            raise ValueError("response_mode must be 'pydantic' or 'json'")

        self._api_token = api_token
        self._response_mode: ResponseMode = response_mode
        owned_session = session is None
        sess = session or requests.Session()

        default_headers: dict[str, str] = {
            "Authorization": f"Bearer {api_token}",
            "Accept": "application/json",
            "User-Agent": user_agent or f"pypresscart/{__version__}",
        }

        self._transport = Transport(
            session=sess,
            base_url=base_url,
            headers=default_headers,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff_base=retry_backoff_base,
            retry_backoff_max=retry_backoff_max,
            retry_jitter=retry_jitter,
        )
        self._owned_session = owned_session
        self._session = sess

        self.auth: AuthResource = AuthResource(self)
        self.outlets: OutletsResource = OutletsResource(self)
        self.products: ProductsResource = ProductsResource(self)
        self.orders: OrdersResource = OrdersResource(self)
        self.order_items: OrderItemsResource = OrderItemsResource(self)
        self.profiles: ProfilesResource = ProfilesResource(self)
        self.campaigns: CampaignsResource = CampaignsResource(self)
        self.articles: ArticlesResource = ArticlesResource(self)
        self.files: FilesResource = FilesResource(self)
        self.folders: FoldersResource = FoldersResource(self)

    # ---- internal helpers ------------------------------------------------

    def _resolve_mode(self, as_json: bool | None) -> bool:
        """Return True iff effective mode is JSON for this call."""
        if as_json is None:
            return self._response_mode == "json"
        return as_json

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        """Send a request and return the parsed JSON body as a dict."""
        response = self._transport.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
            headers=headers,
        )
        if not response.content:
            return {}
        data_out: Any = response.json()
        if isinstance(data_out, list):
            return {"data": data_out}
        if not isinstance(data_out, dict):
            return {"data": data_out}
        return data_out

    def _request_raw(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> bytes:
        """Return raw response bytes (for file downloads)."""
        response = self._transport.request(
            method, path, params=params, headers=headers, stream=False
        )
        return response.content

    # ---- lifecycle -------------------------------------------------------

    def close(self) -> None:
        """Close the underlying session if we own it."""
        if self._owned_session:
            self._session.close()

    def __enter__(self) -> PresscartClient:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()
