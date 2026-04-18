# Integration tests

End-to-end tests that exercise `pypresscart` against the real Presscart API.
Everything in this directory is marked `@pytest.mark.integration` and pulls
the shared `live_client` fixture.

If `PRESSCART_API_TOKEN` is not set, every test here **skips cleanly** —
CI runs the normal unit tests and reports a skip for the integration
suite without failing.

## Running locally

```bash
# one time — copy the template and add your real token
cp tests/integration/.env.local.example tests/integration/.env.local
$EDITOR tests/integration/.env.local

# run only the integration tests
uv run pytest -m integration -v -s

# or the whole suite (unit + integration); integration tests that can't
# auth will skip themselves
uv run pytest -v
```

The `-s` flag keeps the informative `print()` output visible so you can
eyeball the live responses as each test progresses.

## What each module covers

| Module | Endpoint(s) | Notes |
|---|---|---|
| `test_auth.py` | `GET /auth/token` | Sanity + whoami shape |
| `test_outlets_live.py` | all of `client.outlets.*` | List, get, locations, tags, disclaimers |
| `test_products_live.py` | all of `client.products.*` | List listings, filters, get by id |
| `test_orders_live.py` | read-only orders + order items | No `create_checkout`; that has billing side effects |
| `test_profiles_live.py` | all of `client.profiles.*` | team + profile-scoped reads |
| `test_campaigns_live.py` | read-only campaigns | No `create` / `update` / `assign_order_items` |
| `test_articles_live.py` | `GET /articles/{id}` | Expected to raise `PermissionError`; pinned to [issue #8](https://github.com/pypresscart/py-presscart/issues/8). When the server fixes the 403, this test will fail — that's your signal to promote it. |
| `test_files_live.py` | full round-trip | Creates a folder, uploads a tiny embedded JPEG, downloads it, verifies SHA-256, moves, deletes — all self-cleaning. |
| `test_folders_live.py` | full round-trip | Creates two folders, renames, deletes. Self-cleaning. |

## Self-cleaning guarantee

`test_files_live.py` and `test_folders_live.py` create real resources on the
target team. Both wrap the work in `try: ... finally: delete` so even if an
assertion fails mid-test, the created folder + file are removed. Asserted via
a pre/post folder count check at the end of the test.

## Adding new live tests

1. Put the file here as `test_<resource>_live.py`.
2. At module level, add `pytestmark = pytest.mark.integration`.
3. Use the `live_client` fixture instead of constructing a `PresscartClient`.
4. Any resources you create must be cleaned up in `try/finally` — the
   target team is production.
