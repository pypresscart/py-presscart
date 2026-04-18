"""Tests for PresscartClient wiring, headers, and retry behavior."""

from __future__ import annotations

import pytest
import responses

from pypresscart import PresscartClient, __version__
from pypresscart._transport import Transport
from tests.conftest import BASE_URL


def test_requires_api_token() -> None:
    with pytest.raises(ValueError, match="api_token"):
        PresscartClient(api_token="")


def test_invalid_response_mode() -> None:
    with pytest.raises(ValueError, match="response_mode"):
        PresscartClient(api_token="pc_test", response_mode="raw")  # type: ignore[arg-type]


def test_sets_auth_header(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        json={"source": "api_token", "team_id": "t", "token_type": "custom", "scopes": []},
    )
    client.auth.whoami()
    call = mocked.calls[0]
    assert call.request.headers["Authorization"] == "Bearer pc_test_token"
    assert call.request.headers["Accept"] == "application/json"
    assert call.request.headers["User-Agent"] == f"pypresscart/{__version__}"


def test_custom_user_agent(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", user_agent="my-app/1.0", max_retries=0)
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        json={"source": "api_token", "team_id": "t", "token_type": "custom", "scopes": []},
    )
    c.auth.whoami()
    assert mocked.calls[0].request.headers["User-Agent"] == "my-app/1.0"


def test_retries_on_429_then_succeeds(mocked: responses.RequestsMock) -> None:
    calls: list[float] = []
    c = PresscartClient(
        api_token="pc_test",
        max_retries=2,
        retry_backoff_base=0.0,
        retry_backoff_max=0.0,
        retry_jitter=0.0,
    )
    # Swap sleep to a no-op so tests are fast.
    c._transport._sleep = lambda d: calls.append(d)  # type: ignore[assignment]

    mocked.add(
        responses.GET, f"{BASE_URL}/auth/token", status=429, json={"name": "RL", "message": "slow"}
    )
    mocked.add(
        responses.GET, f"{BASE_URL}/auth/token", status=429, json={"name": "RL", "message": "slow"}
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        json={"source": "api_token", "team_id": "t", "token_type": "custom", "scopes": []},
    )

    result = c.auth.whoami(as_json=True)
    assert result["team_id"] == "t"
    assert len(mocked.calls) == 3
    assert len(calls) == 2  # two backoff sleeps before the final success


def test_does_not_retry_on_404(mocked: responses.RequestsMock) -> None:
    from pypresscart import NotFoundError

    c = PresscartClient(
        api_token="pc_test", max_retries=3, retry_backoff_base=0.0, retry_backoff_max=0.0
    )
    mocked.add(
        responses.GET,
        f"{BASE_URL}/orders/missing",
        status=404,
        json={"name": "NotFoundError", "message": "no"},
    )
    with pytest.raises(NotFoundError):
        c.orders.get("missing")
    assert len(mocked.calls) == 1


def test_context_manager_closes_session() -> None:
    with PresscartClient(api_token="pc_test") as c:
        assert c._owned_session is True


def test_transport_strips_none_query_params(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/outlets",
        json={
            "records": [],
            "total_records": 0,
            "total_pages": 0,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    client.outlets.list(limit=10, sort_by=None, order_by=None)
    # responses records query params in the URL; "sort_by" should not appear.
    url = mocked.calls[0].request.url
    assert "sort_by" not in url
    assert "limit=10" in url


def test_transport_init_defaults() -> None:
    import requests

    t = Transport(
        session=requests.Session(),
        base_url="https://x/",
        headers={"A": "b"},
        timeout=1.0,
        max_retries=0,
        retry_backoff_base=0.0,
        retry_backoff_max=0.0,
        retry_jitter=0.0,
    )
    assert t._base_url == "https://x"
