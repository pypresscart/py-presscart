"""Live integration tests for the Articles resource.

Currently exercises the read path only. Mutating endpoints (``update``,
``approve_brief``, ``approve_draft``) are covered by mocked unit tests
in ``tests/test_profiles_products_articles.py`` — they are not run live
because they advance workflow state on the target team.
"""

from __future__ import annotations

import pytest

from pypresscart import PresscartClient

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def an_article_id(live_client: PresscartClient) -> str:
    """Discover an article id via campaigns → list_articles."""
    campaigns = live_client.campaigns.list(limit=25)
    for c in campaigns.records:
        try:
            articles = live_client.campaigns.list_articles(c.id, limit=1)
        except Exception:
            continue
        if articles.records:
            return articles.records[0].id
    pytest.skip("no articles reachable on this team via any campaign")


def test_get_article(live_client: PresscartClient, an_article_id: str) -> None:
    article = live_client.articles.get(an_article_id)
    assert article.id == an_article_id


def test_list_comments(live_client: PresscartClient, an_article_id: str) -> None:
    """Read-only comment listing. Mutating comment endpoints (create/update/
    archive) advance team state and stay mocked-only, like update/approve_*."""
    comments = live_client.articles.list_comments(an_article_id)
    assert hasattr(comments, "records")
