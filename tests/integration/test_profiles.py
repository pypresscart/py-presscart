"""Live integration tests for the Profiles resource."""

from __future__ import annotations

import pytest

from pypresscart import (
    Campaign,
    Order,
    Paginated,
    PresscartClient,
    Profile,
    ProfileOrderItem,
)

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def first_profile_id(live_client: PresscartClient) -> str:
    team_id = live_client.auth.whoami().team_id
    assert team_id, "whoami returned no team_id"
    page = live_client.profiles.list_team_profiles(team_id, limit=1)
    if not page.records:
        pytest.skip("no profiles on this team")
    return page.records[0].id


def test_list_team_profiles(live_client: PresscartClient) -> None:
    team_id = live_client.auth.whoami().team_id
    page = live_client.profiles.list_team_profiles(team_id, limit=5)
    assert isinstance(page, Paginated)
    for p in page.records:
        assert isinstance(p, Profile)


def test_profile_primary_goals_accepts_pg_array(
    live_client: PresscartClient, first_profile_id: str
) -> None:
    """Regression guard for issue #2 — Profile.primary_goals is returned as
    a Postgres-array literal. The field validator normalizes it to list[str]."""
    team_id = live_client.auth.whoami().team_id
    page = live_client.profiles.list_team_profiles(team_id, limit=10)
    profile = next((p for p in page.records if p.id == first_profile_id), None)
    assert profile is not None
    assert isinstance(profile.primary_goals, list)
    assert all(isinstance(g, str) for g in profile.primary_goals)


def test_profile_orders(live_client: PresscartClient, first_profile_id: str) -> None:
    page = live_client.profiles.list_orders(first_profile_id, limit=5)
    assert isinstance(page, Paginated)
    for o in page.records:
        assert isinstance(o, Order)


def test_profile_orders_paid_only(live_client: PresscartClient, first_profile_id: str) -> None:
    """Regression guard for issue #6 — boolean query param `paid_orders_only=True`
    (capitalized) used to be rejected as 400. `_clean_params` now lowercases it."""
    page = live_client.profiles.list_orders(first_profile_id, paid_orders_only=True, limit=5)
    assert isinstance(page, Paginated)
    for o in page.records:
        assert o.status == "PAID"


def test_profile_order_items_bare_array(
    live_client: PresscartClient, first_profile_id: str
) -> None:
    items = live_client.profiles.list_order_items(first_profile_id)
    # Documented as a bare array, not a Paginated envelope.
    assert isinstance(items, list)
    for item in items:
        assert isinstance(item, ProfileOrderItem)


def test_profile_campaigns(live_client: PresscartClient, first_profile_id: str) -> None:
    page = live_client.profiles.list_campaigns(first_profile_id, limit=5)
    assert isinstance(page, Paginated)
    for c in page.records:
        assert isinstance(c, Campaign)
