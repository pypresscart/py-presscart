"""Live integration tests for the Campaigns resource (read-only).

Write endpoints (create / update / assign_order_items / link_questionnaire)
are intentionally out of scope — they mutate live campaign state.
"""

from __future__ import annotations

import pytest

from pypresscart import (
    Campaign,
    CampaignArticleRow,
    Paginated,
    PresscartClient,
)

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def first_campaign_id(live_client: PresscartClient) -> str:
    page = live_client.campaigns.list(limit=1)
    if not page.records:
        pytest.skip("no campaigns on this team")
    return page.records[0].id


def test_list_campaigns(live_client: PresscartClient) -> None:
    page = live_client.campaigns.list(limit=5)
    assert isinstance(page, Paginated)
    for c in page.records:
        assert isinstance(c, Campaign)


def test_list_campaigns_with_search(live_client: PresscartClient) -> None:
    # Search for a single letter is very permissive; should always match
    # something if any campaign exists.
    page = live_client.campaigns.list(limit=3, filters={"search": "a"})
    assert isinstance(page, Paginated)


def test_get_campaign(live_client: PresscartClient, first_campaign_id: str) -> None:
    campaign = live_client.campaigns.get(first_campaign_id)
    assert isinstance(campaign, Campaign)
    assert campaign.id == first_campaign_id
    # Detail endpoint populates total_articles (issue #7: list endpoint
    # returns null, detail returns the count).
    assert campaign.total_articles is not None or campaign.total_articles == 0


def test_list_campaign_articles(live_client: PresscartClient, first_campaign_id: str) -> None:
    page = live_client.campaigns.list_articles(first_campaign_id, limit=5)
    assert isinstance(page, Paginated)
    for a in page.records:
        assert isinstance(a, CampaignArticleRow)


def test_campaign_article_status_counts(
    live_client: PresscartClient, first_campaign_id: str
) -> None:
    counts = live_client.campaigns.article_status_counts(first_campaign_id)
    # Non-standard envelope — always a dict with a "records" key.
    assert isinstance(counts, dict)
    assert "records" in counts
    assert all("name" in r and "count" in r for r in counts["records"])
