# Testing status

Which parts of `pypresscart` have been verified against the real Presscart API, and which are implemented from the public docs only.

:::{important}
**Every method in the library is implemented.** This page is about which ones have been *empirically confirmed* to work end-to-end against a live Presscart team. A method marked "not yet exercised" is still there — we just haven't run it against production, either because it has side-effects (creates billing charges, writes non-test data) or because the server blocks it.
:::

## Read-only endpoints — fully exercised

Every GET below was hit with a `full_access` token, the response was parsed into its Pydantic model, and the dict-mode round-trip was verified. Unless noted, filter / sort / pagination variants were also tested.

| Resource | Method | Endpoint |
|---|---|---|
| Auth | `whoami` | `GET /auth/token` |
| Outlets | `list` | `GET /outlets` |
| Outlets | `get` | `GET /outlets/{outlet_id}` |
| Outlets | `list_products` | `GET /outlets/{outlet_id}/products` |
| Outlets | `list_countries` | `GET /outlets/locations/countries` |
| Outlets | `list_states` | `GET /outlets/locations/states` |
| Outlets | `list_cities` | `GET /outlets/locations/cities` |
| Outlets | `list_tags` | `GET /tags` |
| Outlets | `list_disclaimers` | `GET /outlet-disclaimers` |
| Products | `get` | `GET /products/{product_id}` |
| Products | `list_listings` | `GET /products/listings` |
| Products | `list_categories` | `GET /products/categories` |
| Orders | `list` | `GET /orders` |
| Orders | `get` | `GET /orders/{order_id}` |
| Order Items | `list` | `GET /order-items` |
| Profiles | `list_team_profiles` | `GET /teams/{team_id}/profiles` |
| Profiles | `list_orders` | `GET /profiles/{profile_id}/orders` |
| Profiles | `list_order_items` | `GET /profiles/{profile_id}/order-items` |
| Profiles | `list_campaigns` | `GET /profiles/{profile_id}/campaigns` |
| Campaigns | `list` | `GET /campaigns` |
| Campaigns | `get` | `GET /campaigns/{campaign_id}` |
| Campaigns | `list_articles` | `GET /campaigns/{campaign_id}/articles` |
| Campaigns | `article_status_counts` | `GET /campaigns/{campaign_id}/articles/status-count` |

## Files + Folders — full write round-trip

The Files and Folders resources have been exercised **end-to-end including writes** — the test creates a folder and a file, moves the file around, renames the folder, and deletes both. It's self-cleaning, so running it leaves no residue.

| Resource | Method | Endpoint |
|---|---|---|
| Folders | `list` | `GET /folders` |
| Folders | `create` | `POST /folders` |
| Folders | `rename` | `PATCH /folders/{folder_id}` |
| Folders | `delete` | `DELETE /folders/{folder_id}` |
| Files | `list` | `GET /files` |
| Files | `get` | `GET /files/{file_id}` |
| Files | `upload` | `POST /files/upload` |
| Files | `download` | `GET /files/{file_id}/download` |
| Files | `move` | `POST /files/move` |
| Files | `delete` | `DELETE /files/{file_id}` |

Download bytes are verified to match the uploaded file **SHA-256 for SHA-256** before delete — so the compression / CDN round-trip is confirmed lossless.

## Blocked upstream — tested but server denies access

| Resource | Method | Endpoint | Status |
|---|---|---|---|
| Articles | `get` | `GET /articles/{article_id}` | Server returns **403** to `full_access` tokens. See [issue #8](https://github.com/pypresscart/py-presscart/issues/8). |

Because `articles.get()` is the only way to fetch a single article's full detail (brief URL, draft URL, writer, etc.), the **Articles write endpoints below are effectively gated behind this fix**. They're wired up and type-checked, but you can't realistically use them today without first resolving issue #8 on the server side.

## Not yet exercised — write endpoints with real-world side effects

These methods are **implemented and covered by unit tests against mocked responses**, but haven't been fired against the real Presscart API. Each one either creates billing charges, modifies production data, or depends on an endpoint that's currently blocked (see above).

:::{warning}
Use in production with appropriate caution. Run a dry-run against a staging team first, or inspect the request payload with `requests` hooks before sending.
:::

### Orders

| Method | Endpoint | Why untested |
|---|---|---|
| `create_checkout` | `POST /orders/checkout` | Creates a real order and initiates billing. Not something to run as a smoke test. |

### Campaigns

| Method | Endpoint | Why untested |
|---|---|---|
| `create` | `POST /campaigns` | Creates persistent production data on the test team. |
| `update` | `PUT /campaigns/{campaign_id}` | Modifies existing campaign; side effects on the live dashboard. |
| `assign_order_items` | `POST /campaigns/{campaign_id}/order-items` | Mutates campaign ↔ order-item association. |
| `link_questionnaire` | `POST /questionnaires/{campaign_id}/link` | Mutates questionnaire state. |

### Articles

| Method | Endpoint | Why untested |
|---|---|---|
| `update` | `PUT /articles/{article_id}` | Blocked transitively by issue #8 — can't read current state first. |
| `approve_brief` | `PATCH /articles/{article_id}/approve-brief` | Same — plus approving a real brief advances the article through the workflow. |
| `approve_draft` | `PATCH /articles/{article_id}/approve-draft` | Same. |

## Unit-test coverage

All 55+ unit tests in the repo's `tests/` directory mock the HTTP layer with [`responses`](https://github.com/getsentry/responses) and assert shape, error mapping, dual-mode behavior, and retry semantics. The **untested** endpoints above all have at least one happy-path unit test; they're just not hit against the live server.

## How this was tested

Each "fully exercised" resource has a matching pytest module under [`tests/integration/`](https://github.com/pypresscart/py-presscart/tree/main/tests/integration):

| Resource | Module |
|---|---|
| Auth | `tests/integration/test_auth.py` |
| Outlets | `tests/integration/test_outlets.py` |
| Products | `tests/integration/test_products.py` |
| Orders + Order Items | `tests/integration/test_orders.py` |
| Profiles | `tests/integration/test_profiles.py` |
| Campaigns | `tests/integration/test_campaigns.py` |
| Articles | `tests/integration/test_articles.py` |
| Files | `tests/integration/test_files.py` |
| Folders | `tests/integration/test_folders.py` |

Every module is marked `@pytest.mark.integration`. Drop a token into `tests/integration/.env.local` (template: `.env.local.example`) and run them with:

```bash
uv run pytest -m integration -v -s
```

Integration tests auto-skip if `PRESSCART_API_TOKEN` is absent, so CI stays green without one.
