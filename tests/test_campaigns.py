from __future__ import annotations

import json

import responses

from pypresscart import (
    Campaign,
    CampaignCreateRequest,
    CampaignUpdateRequest,
    PresscartClient,
)
from tests.conftest import BASE_URL

CAMPAIGN = {
    "id": "cmp_1",
    "name": "Launch",
    "profile_id": "prof_1",
    "objectives": "grow",
}


def test_list_campaigns(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/campaigns",
        json={
            "records": [CAMPAIGN],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.campaigns.list()
    assert isinstance(page.records[0], Campaign)  # type: ignore[union-attr]


def test_create_campaign(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(responses.POST, f"{BASE_URL}/campaigns", json=CAMPAIGN)
    body = CampaignCreateRequest(
        name="Launch",
        description=None,
        profile_id="prof_1",
        objectives="grow",
        keywords=None,
        target_audience=None,
        tone=None,
        writing_samples=None,
        file_id=None,
    )
    created = client.campaigns.create(body)
    assert isinstance(created, Campaign)
    sent = json.loads(mocked.calls[0].request.body)
    assert sent["name"] == "Launch"


def test_update_campaign(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    updated = dict(CAMPAIGN, name="Relaunch")
    mocked.add(responses.PUT, f"{BASE_URL}/campaigns/cmp_1", json=updated)
    body = CampaignUpdateRequest(name="Relaunch")
    result = client.campaigns.update("cmp_1", body)
    assert isinstance(result, Campaign)
    assert result.name == "Relaunch"


def test_assign_order_items(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.POST,
        f"{BASE_URL}/campaigns/cmp_1/order-items",
        json={"records": [{"id": "oi_1", "campaign_id": "cmp_1"}]},
    )
    resp = client.campaigns.assign_order_items("cmp_1", {"order_item_ids": ["oi_1"]})
    assert resp["records"][0]["campaign_id"] == "cmp_1"
