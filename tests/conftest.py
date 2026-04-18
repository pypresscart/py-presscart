"""Shared fixtures for presscart tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
import responses

from pypresscart import PresscartClient

BASE_URL = "https://api.presscart.com"


@pytest.fixture
def mocked() -> Iterator[responses.RequestsMock]:
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def client() -> PresscartClient:
    # max_retries=0 keeps tests deterministic — we assert exact call counts.
    return PresscartClient(
        api_token="pc_test_token",
        max_retries=0,
    )


@pytest.fixture
def paginated_envelope():
    return {
        "records": [],
        "total_records": 0,
        "total_pages": 0,
        "current_page": 1,
        "next_page": None,
        "previous_page": None,
    }
