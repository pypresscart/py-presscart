"""Tests for error mapping and exception payload exposure."""

from __future__ import annotations

import pytest
import responses

from pypresscart import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionError,
    PresscartAPIError,
    PresscartClient,
    RateLimitError,
    ServerError,
    ValidationError,
)
from tests.conftest import BASE_URL


@pytest.mark.parametrize(
    "status,err_cls",
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (403, PermissionError),
        (404, NotFoundError),
        (500, ServerError),
    ],
)
def test_status_codes_map_to_classes(
    status: int,
    err_cls: type[PresscartAPIError],
    mocked: responses.RequestsMock,
) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0)
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        status=status,
        json={"name": f"E{status}", "message": "boom"},
    )
    with pytest.raises(err_cls) as excinfo:
        c.auth.whoami()
    assert excinfo.value.status_code == status
    assert excinfo.value.name == f"E{status}"
    assert excinfo.value.message == "boom"
    assert excinfo.value.payload == {"name": f"E{status}", "message": "boom"}


def test_validation_error_exposes_issues(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0)
    body = {
        "name": "ValidationError",
        "message": "Invalid payload",
        "issues": [{"path": ["profile_id"], "message": "Required"}],
    }
    mocked.add(responses.POST, f"{BASE_URL}/orders/checkout", status=400, json=body)
    with pytest.raises(ValidationError) as excinfo:
        c.orders.create_checkout({"profile_id": "", "line_items": []})
    assert excinfo.value.issues == [{"path": ["profile_id"], "message": "Required"}]


def test_rate_limit_captures_retry_after(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0)
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        status=429,
        json={"name": "RL", "message": "slow"},
        headers={"Retry-After": "7"},
    )
    with pytest.raises(RateLimitError) as excinfo:
        c.auth.whoami()
    assert excinfo.value.retry_after == 7.0


def test_error_without_json_body(mocked: responses.RequestsMock) -> None:
    c = PresscartClient(api_token="pc_test", max_retries=0)
    mocked.add(
        responses.GET,
        f"{BASE_URL}/auth/token",
        status=500,
        body="plain text",
    )
    with pytest.raises(ServerError) as excinfo:
        c.auth.whoami()
    assert excinfo.value.status_code == 500
    assert excinfo.value.name is None
