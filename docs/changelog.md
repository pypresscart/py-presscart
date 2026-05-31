# Changelog

All notable changes to `pypresscart` are recorded here. This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.7] — 2026-05-30

### Added
- `client.articles.list_comments()`, `create_comment()`, `update_comment()`,
  and `archive_comment()` — full coverage of the article **Comments** API
  (`GET`/`POST`/`PUT`/`DELETE
  /articles/{article_id}/comments[/{comment_reference}]`). Comments support one
  level of replies via `parent_comment_id`; the short reference returned as
  `id` (not a UUID) is the handle for update/archive. New models: `Comment`,
  `CommentList`, `CommentAuthor`, `CommentAuthorInput`, `CommentCreateRequest`,
  `CommentUpdateRequest`, and `CommentArchiveResponse` (empty — the archive
  endpoint responds `204 No Content`). All dual-mode. The comment endpoints use
  the `articles.read`/`articles.lists`/`articles.create`/`articles.update`/
  `articles.delete` scopes.

## [0.1.6] — 2026-05-14

### Fixed
- `client.campaigns.create()` now sends the nullable body fields
  (`description`, `keywords`, `target_audience`, `tone`, `writing_samples`,
  `file_id`) as explicit `null`s instead of dropping them. `POST /campaigns`
  requires these keys to be *present* in the payload even when null;
  `_serialize` previously used `exclude_none=True` unconditionally, so a
  `CampaignCreateRequest` built with the nullable fields left at their
  `None` defaults produced a payload the API rejected. `_serialize` now
  takes an `exclude_none` keyword (default `True`, unchanged for every
  other endpoint); `campaigns.create` opts into `exclude_none=False`.
  Plain `dict` bodies are still passed through untouched.

## [0.1.5] — 2026-05-10

### Added
- `client.orders.get(order_id, include_outlets_data=True)` — new keyword-only
  parameter that requests a fully-populated `outlet` block (`id`, `name`,
  `logo`, `website_url`) on each line item instead of the lean shape.
  Defaults to `None`, in which case the parameter is omitted from the URL
  and existing call sites are byte-for-byte unchanged on the wire.

## [0.1.4] — 2026-05-08

### Added
- `Order.name` and `Order.email` — top-level fields returned by
  `GET /orders/{order_id}` (the list endpoint nests these as `team.name` /
  `team.contact_email`; both shapes are now modelled in parallel).
- `LineItem.includes: list[IncludeItem] | None` — channel/placement array
  surfaced on `GET /orders/{order_id}` line items.

### Fixed
- `LineItem.id` and `LineItem.order_id` are now optional. The Presscart API
  doesn't populate them on the lean `POST /orders/checkout` response (line
  items are only persisted with an id once the order is paid, exposed via
  `GET /order-items`), which previously caused checkout responses to fail
  Pydantic validation.

### Changed
- Removed the strict-`xfail` trip-wire on the `tests/integration/test_articles.py::test_get_article` live test. Presscart fixed the `GET /articles/{article_id}` 403 for `full_access` API tokens (issue #8), and the live test now passes. Documentation under `docs/testing-status.md` and `docs/resource-articles.md` updated accordingly.

## [0.1.3] — 2026-04-18

### Fixed
- `OutletChannel.do_follow_links_allowed` now accepts string values (e.g.
  `"Unlimited"`) in addition to `bool`/`null`. The Presscart API returns a
  capacity string here on some outlet channels even though the docs type it
  as a boolean, which was causing `GET /outlets/{id}` to raise a Pydantic
  `ValidationError` whenever one of those channels appeared in the response.

## [0.1.2] — 2026-04-18

### Fixed
- `serialize_filters` now emits list-valued filters in the indexed-bracket
  form (`filters[key][0]=v1&filters[key][1]=v2`) that the Presscart API
  actually parses. The previous bare-bracket form (`filters[key][]=v1`) was
  silently ignored by the server, causing any query using `disclaimer_ids`,
  `placement_types`, `channel_types`, `tags`, or `product_ids` to return the
  full unfiltered result set instead of the expected subset.

## [0.1.1] — 2026-04-18

Housekeeping release. No runtime behavior changes.

### Changed
- Project URLs in `pyproject.toml` (and therefore the **Project links** sidebar on PyPI) now point at the new owner `pypresscart/py-presscart`. 0.1.0 still shipped with the original `annjawn/py-presscart` URLs baked into its metadata; GitHub redirects preserve them, but 0.1.1 is the first release published under the canonical URLs.
- Docs site moved from `www.anjanbiswas.dev/py-presscart/` to <https://pypresscart.github.io/py-presscart/> as a side-effect of the repo transfer to the new `pypresscart` GitHub org.
- README now documents the full release procedure end-to-end and notes that `main` is protected (CI must pass, no direct pushes, force-pushes and deletions denied).

## [0.1.0] — Initial release

Initial public release.

### Added
- `PresscartClient` with composable resource services: `auth`, `outlets`, `products`, `orders`, `order_items`, `profiles`, `campaigns`, `articles`, `files`, `folders`.
- Full coverage of the Presscart API as of release date (40+ endpoints).
- Pydantic models for every request and response shape.
- Dual-mode I/O: accept and return either Pydantic models or `dict`s, controllable per-call (`as_json=`) or at the client level (`response_mode=`).
- Typed exception hierarchy with `BadRequestError`, `ValidationError`, `AuthenticationError`, `PermissionError`, `NotFoundError`, `RateLimitError`, `ServerError`, and `PresscartTransportError`.
- Automatic exponential-backoff retry on 429/5xx/network errors, honoring `Retry-After`.
- Context-manager lifecycle.
- Typed throughout (`py.typed` shipped; mypy-strict clean).

### Dependencies
- Runtime: `pydantic>=2.7,<3`, `requests>=2.31,<3`.
- Python 3.10+.

[Unreleased]: https://github.com/pypresscart/py-presscart/compare/v0.1.7...HEAD
[0.1.7]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.7
[0.1.6]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.6
[0.1.5]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.5
[0.1.4]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.4
[0.1.3]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.3
[0.1.2]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.2
[0.1.1]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.1
[0.1.0]: https://github.com/pypresscart/py-presscart/releases/tag/v0.1.0
