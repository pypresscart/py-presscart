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


_NULLABLE_CREATE_KEYS = (
    "description",
    "keywords",
    "target_audience",
    "tone",
    "writing_samples",
    "file_id",
)


def test_create_campaign(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    """``POST /campaigns`` requires the nullable fields to be *present* in the
    payload even when ``null`` — the Pydantic body must serialize with
    ``exclude_none=False`` so those keys are not dropped.
    """
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
    for key in _NULLABLE_CREATE_KEYS:
        assert key in sent, f"{key} was dropped from the create payload"
        assert sent[key] is None


def test_create_campaign_dict_body_preserves_nulls(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    """A plain ``dict`` body is passed through untouched, so explicit nulls
    survive regardless of the ``exclude_none`` default.
    """
    mocked.add(responses.POST, f"{BASE_URL}/campaigns", json=CAMPAIGN)
    raw = client.campaigns.create(
        {
            "name": "Launch",
            "profile_id": "prof_1",
            "objectives": "grow",
            "description": None,
            "keywords": None,
            "target_audience": None,
            "tone": None,
            "writing_samples": None,
            "file_id": None,
        },
        as_json=True,
    )
    assert isinstance(raw, dict)
    sent = json.loads(mocked.calls[0].request.body)
    for key in _NULLABLE_CREATE_KEYS:
        assert key in sent
        assert sent[key] is None


def test_update_campaign(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    """``PUT /campaigns/{id}`` keeps omit-to-skip semantics — unset fields are
    dropped (``exclude_none=True``, the ``_serialize`` default) so an update
    doesn't accidentally null out fields the caller didn't touch.
    """
    updated = dict(CAMPAIGN, name="Relaunch")
    mocked.add(responses.PUT, f"{BASE_URL}/campaigns/cmp_1", json=updated)
    body = CampaignUpdateRequest(name="Relaunch")
    result = client.campaigns.update("cmp_1", body)
    assert isinstance(result, Campaign)
    assert result.name == "Relaunch"
    sent = json.loads(mocked.calls[0].request.body)
    assert sent == {"name": "Relaunch"}


def test_assign_order_items(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.POST,
        f"{BASE_URL}/campaigns/cmp_1/order-items",
        json={"records": [{"id": "oi_1", "campaign_id": "cmp_1"}]},
    )
    resp = client.campaigns.assign_order_items("cmp_1", {"order_item_ids": ["oi_1"]})
    assert resp["records"][0]["campaign_id"] == "cmp_1"
