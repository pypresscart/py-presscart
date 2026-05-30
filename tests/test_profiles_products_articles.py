"""Spot tests for profiles / products / articles / order_items."""

from __future__ import annotations

import responses

from pypresscart import (
    Article,
    Comment,
    CommentArchiveResponse,
    CommentCreateRequest,
    CommentList,
    OrderItem,
    PresscartClient,
    Product,
    ProductListing,
    Profile,
    ProfileOrderItem,
)
from tests.conftest import BASE_URL


def test_get_product(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/products/prod_1",
        json={"id": "prod_1", "name": "Feature"},
    )
    product = client.products.get("prod_1")
    assert isinstance(product, Product)


def test_list_product_listings(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/products/listings",
        json={
            "records": [
                {"id": "prod_1", "name": "Feature", "tags": [], "prices": [], "includes": []}
            ],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.products.list_listings(filters={"min_price": 100})
    assert isinstance(page.records[0], ProductListing)  # type: ignore[union-attr]


def test_list_product_listings_array_filter_is_indexed(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    """Array filters must go out as filters[key][0]=... indexed brackets —
    the bare [] form is silently ignored by the Presscart API."""
    mocked.add(
        responses.GET,
        f"{BASE_URL}/products/listings",
        json={
            "records": [],
            "total_records": 0,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    client.products.list_listings(
        filters={
            "disclaimer_ids": ["abc", "def"],
            "placement_types": ["FULL_FEATURE"],
            "country": "United States",
        },
    )
    url = mocked.calls[0].request.url
    assert "filters%5Bdisclaimer_ids%5D%5B0%5D=abc" in url
    assert "filters%5Bdisclaimer_ids%5D%5B1%5D=def" in url
    assert "filters%5Bplacement_types%5D%5B0%5D=FULL_FEATURE" in url
    assert "filters%5Bcountry%5D=United+States" in url
    assert "filters%5Bdisclaimer_ids%5D%5B%5D" not in url


def test_list_product_categories(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/products/categories",
        json=[{"type": "FULL_FEATURE", "count": 5}],
    )
    cats = client.products.list_categories()
    assert cats[0].type == "FULL_FEATURE"  # type: ignore[union-attr]


def test_profile_order_items_bare_array(
    mocked: responses.RequestsMock, client: PresscartClient
) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/profiles/prof_1/order-items",
        json=[
            {"id": "oi_1", "name": "Feature", "includes": []},
        ],
    )
    items = client.profiles.list_order_items("prof_1")
    assert isinstance(items[0], ProfileOrderItem)


def test_list_team_profiles(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/teams/team_1/profiles",
        json={
            "records": [{"id": "prof_1", "name": "Brand"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.profiles.list_team_profiles("team_1")
    assert isinstance(page.records[0], Profile)  # type: ignore[union-attr]


def test_profile_primary_goals_accepts_json_array() -> None:
    prof = Profile.model_validate(
        {"id": "prof_1", "primary_goals": ["BRAND_AWARENESS", "THOUGHT_LEADERSHIP"]}
    )
    assert prof.primary_goals == ["BRAND_AWARENESS", "THOUGHT_LEADERSHIP"]


def test_profile_primary_goals_accepts_pg_array_literal() -> None:
    prof = Profile.model_validate(
        {"id": "prof_1", "primary_goals": "{BRAND_AWARENESS,THOUGHT_LEADERSHIP}"}
    )
    assert prof.primary_goals == ["BRAND_AWARENESS", "THOUGHT_LEADERSHIP"]


def test_profile_primary_goals_accepts_empty_pg_array() -> None:
    assert Profile.model_validate({"id": "p", "primary_goals": "{}"}).primary_goals == []
    assert Profile.model_validate({"id": "p", "primary_goals": ""}).primary_goals == []


def test_list_order_items(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/order-items",
        json={
            "records": [{"id": "oi_1"}],
            "total_records": 1,
            "total_pages": 1,
            "current_page": 1,
            "next_page": None,
            "previous_page": None,
        },
    )
    page = client.order_items.list()
    assert isinstance(page.records[0], OrderItem)  # type: ignore[union-attr]


def test_article_approve_brief(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.PATCH,
        f"{BASE_URL}/articles/art_1/approve-brief",
        json={"id": "art_1", "name": "approved"},
    )
    result = client.articles.approve_brief("art_1")
    assert isinstance(result, Article)


def test_article_update(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.PUT,
        f"{BASE_URL}/articles/art_1",
        json={"id": "art_1", "name": "New"},
    )
    result = client.articles.update("art_1", {"name": "New"})
    assert isinstance(result, Article)


def test_article_approve_draft(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.PATCH,
        f"{BASE_URL}/articles/art_1/approve-draft",
        json={"id": "art_1", "name": "approved"},
    )
    result = client.articles.approve_draft(
        "art_1", {"draft_google_doc_url": "https://docs.example/abc"}
    )
    assert isinstance(result, Article)


# --- Comments -----------------------------------------------------------------

_COMMENT = {
    "id": "K7M2Q9XA",
    "content": "Can you clarify the requested change?",
    "author": {"name": "Jane Smith", "email": "jane@example.com"},
    "created_at": "2026-03-20T10:00:00.000Z",
    "updated_at": "2026-03-20T10:00:00.000Z",
    "parent_comment_id": None,
    "replies": [
        {
            "id": "M4R8T1QZ",
            "content": "Yes, we updated the introduction.",
            "author": {"name": "Pat Lee", "email": None},
            "created_at": "2026-03-20T10:05:00.000Z",
            "updated_at": "2026-03-20T10:05:00.000Z",
            "parent_comment_id": "K7M2Q9XA",
        }
    ],
}


def test_list_comments(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/articles/art_1/comments",
        json={"records": [_COMMENT]},
    )
    result = client.articles.list_comments("art_1")
    assert isinstance(result, CommentList)
    assert isinstance(result.records[0], Comment)
    assert isinstance(result.records[0].replies[0], Comment)  # one level deep
    assert result.records[0].replies[0].parent_comment_id == "K7M2Q9XA"


def test_list_comments_json(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.GET,
        f"{BASE_URL}/articles/art_1/comments",
        json={"records": [_COMMENT]},
    )
    result = client.articles.list_comments("art_1", as_json=True)
    assert isinstance(result, dict)
    assert result["records"][0]["replies"][0]["id"] == "M4R8T1QZ"


def test_create_comment(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.POST,
        f"{BASE_URL}/articles/art_1/comments",
        json={**_COMMENT, "replies": []},
        status=201,
    )
    body = CommentCreateRequest(
        content="Can you clarify the requested change?",
        author={"name": "Jane Smith", "email": "jane@example.com", "external_id": "u-123"},  # type: ignore[arg-type]
    )
    result = client.articles.create_comment("art_1", body)
    assert isinstance(result, Comment)
    assert result.id == "K7M2Q9XA"


def test_create_comment_json(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.POST,
        f"{BASE_URL}/articles/art_1/comments",
        json={**_COMMENT, "replies": []},
        status=201,
    )
    result = client.articles.create_comment(
        "art_1",
        {"content": "Hi", "author": {"name": "Jane Smith"}},
        as_json=True,
    )
    assert isinstance(result, dict)
    assert result["id"] == "K7M2Q9XA"


def test_update_comment(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.PUT,
        f"{BASE_URL}/articles/art_1/comments/K7M2Q9XA",
        json={**_COMMENT, "content": "Updated comment text."},
    )
    result = client.articles.update_comment(
        "art_1", "K7M2Q9XA", {"content": "Updated comment text."}
    )
    assert isinstance(result, Comment)
    assert result.content == "Updated comment text."


def test_update_comment_json(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.PUT,
        f"{BASE_URL}/articles/art_1/comments/K7M2Q9XA",
        json={**_COMMENT, "content": "Updated comment text."},
    )
    result = client.articles.update_comment(
        "art_1", "K7M2Q9XA", {"content": "Updated comment text."}, as_json=True
    )
    assert isinstance(result, dict)
    assert result["content"] == "Updated comment text."


def test_archive_comment(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.DELETE,
        f"{BASE_URL}/articles/art_1/comments/K7M2Q9XA",
        status=204,
    )
    result = client.articles.archive_comment("art_1", "K7M2Q9XA")
    assert isinstance(result, CommentArchiveResponse)


def test_archive_comment_json(mocked: responses.RequestsMock, client: PresscartClient) -> None:
    mocked.add(
        responses.DELETE,
        f"{BASE_URL}/articles/art_1/comments/K7M2Q9XA",
        status=204,
    )
    result = client.articles.archive_comment("art_1", "K7M2Q9XA", as_json=True)
    assert result == {}
