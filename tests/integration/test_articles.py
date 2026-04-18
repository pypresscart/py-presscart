"""Live integration tests for the Articles resource.

Currently pinned to upstream issue #8: GET /articles/{id} returns 403 to
full_access API tokens. When Presscart fixes the 403, this test will fail
(the xfail reverses) — that's the signal to promote it to a real passing test.

Write endpoints (update / approve_brief / approve_draft) depend on being
able to read an article's current state first, so they are gated behind
issue #8 too and aren't exercised here.
"""

from __future__ import annotations

import pytest

from pypresscart import PermissionError as PresscartPermissionError, PresscartClient

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


@pytest.mark.xfail(
    reason="upstream issue #8: GET /articles/{id} returns 403 to full_access tokens",
    strict=True,
    raises=PresscartPermissionError,
)
def test_get_article(live_client: PresscartClient, an_article_id: str) -> None:
    """The call is the assertion — on success (once Presscart fixes the bug)
    xfail(strict=True) will turn this into a RED test to force us to remove
    the xfail and promote the full endpoint."""
    article = live_client.articles.get(an_article_id)
    assert article.id == an_article_id
