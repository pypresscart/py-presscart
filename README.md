<h1 align="center">pypresscart — A Python Library for the Presscart API</h1>

<p align="center">
  <a href="https://pypi.org/project/pypresscart/"><img alt="PyPI" src="https://img.shields.io/pypi/v/pypresscart.svg"></a>
  <a href="https://pypi.org/project/pypresscart/"><img alt="Python" src="https://img.shields.io/pypi/pyversions/pypresscart.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <a href="https://github.com/astral-sh/ruff"><img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
  <a href="https://mypy-lang.org/"><img alt="Checked with mypy" src="https://www.mypy-lang.org/static/mypy_badge.svg"></a>
  <a href="https://docs.pydantic.dev/"><img alt="Types - Pydantic" src="https://img.shields.io/badge/types-pydantic-E92063.svg"></a>
  <a href="https://pre-commit.com/"><img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit"></a>
  <a href="https://annjawn.github.io/py-presscart/"><img alt="Docs" src="https://img.shields.io/github/actions/workflow/status/annjawn/py-presscart/docs.yml?label=docs"></a>
</p>

<p align="center">
  <a href="https://annjawn.github.io/py-presscart/">📚 Documentation</a>
  ·
  <a href="https://pypi.org/project/pypresscart/">PyPI</a>
  ·
  <a href="https://github.com/annjawn/py-presscart/issues">Issues</a>
</p>

> ⚠️ **Unofficial library.** This project is not affiliated with, endorsed by, or supported by Presscart. It's a community-maintained Python client for the [Presscart API](https://docs.presscart.com).

- Pythonic, typed resource methods (`client.outlets.list(...)`, `client.orders.create_checkout(...)`, ...)
- **Dual-mode**: pass Pydantic models or plain dicts; get Pydantic models or plain dicts back
- Single dependency stack — `requests` + `pydantic`
- Built-in exponential-backoff retry for `429` / `5xx` responses, honoring `Retry-After`
- Typed exception hierarchy (`BadRequestError`, `AuthenticationError`, `RateLimitError`, ...)

## Install

```bash
uv add pypresscart
# or
pip install pypresscart
```

Python 3.10+.

## Quickstart

```python
from pypresscart import PresscartClient

client = PresscartClient(api_token="pc_...")

me = client.auth.whoami()
print(me.team_id, me.scopes)

outlets = client.outlets.list(limit=5, filters={"country": "United States"})
for row in outlets.records:
    print(row.outlet_name, row.website_url)
```

## Dual-mode usage

The library accepts both Pydantic models and raw dicts on the way in, and
returns either on the way out.

```python
from pypresscart import CheckoutLineItem, CheckoutRequest, PresscartClient

client = PresscartClient(api_token="pc_...")

# Pydantic in, Pydantic out (default)
order = client.orders.create_checkout(
    CheckoutRequest(
        profile_id="YOUR_PROFILE_ID",
        line_items=[CheckoutLineItem(product_id="YOUR_PRODUCT_ID", quantity=1)],
    )
)
print(order.reference_number)

# Dict in, dict out
raw = client.orders.create_checkout(
    {
        "profile_id": "YOUR_PROFILE_ID",
        "line_items": [
            {"product_id": "YOUR_PRODUCT_ID", "quantity": 1, "is_add_on": False}
        ],
        "discount": 0,
    },
    as_json=True,
)
print(raw["reference_number"])
```

You can also set the default for the whole client:

```python
client = PresscartClient(api_token="pc_...", response_mode="json")
```

Per-call `as_json=True` / `as_json=False` always wins over the client default.

## Error handling

```python
from pypresscart import (
    AuthenticationError,
    NotFoundError,
    PresscartAPIError,
    RateLimitError,
    ValidationError,
)

try:
    client.campaigns.get("missing")
except NotFoundError as exc:
    print("not found:", exc.message)
except AuthenticationError:
    print("token invalid or expired")
except RateLimitError as exc:
    print("slow down; retry after", exc.retry_after)
except ValidationError as exc:
    for issue in exc.issues:
        print("field", issue["path"], issue["message"])
except PresscartAPIError as exc:
    print(exc.status_code, exc.name, exc.message, exc.payload)
```

All API errors inherit from `PresscartAPIError`. Network-level failures raise
`PresscartTransportError` (wrapping the underlying `requests` exception).

## Client options

| Parameter | Default | Description |
|---|---|---|
| `api_token` | *(required)* | Bearer token (`pc_...`) |
| `base_url` | `https://api.presscart.com` | API origin |
| `timeout` | `30.0` | Per-request timeout (seconds) |
| `max_retries` | `3` | Additional attempts on 429/5xx/network errors |
| `retry_backoff_base` | `0.25` | Base backoff seconds |
| `retry_backoff_max` | `4.0` | Backoff cap |
| `retry_jitter` | `0.1` | Fractional jitter |
| `response_mode` | `"pydantic"` | `"pydantic"` or `"json"` |
| `user_agent` | `"pypresscart/<version>"` | `User-Agent` header |
| `session` | `None` | Inject a pre-configured `requests.Session` |

Use as a context manager to close the session automatically:

```python
with PresscartClient(api_token="pc_...") as client:
    ...
```

## Endpoints

Every endpoint documented at [docs.presscart.com](https://docs.presscart.com)
is covered by a method on one of the resource services:

| Service | Methods |
|---|---|
| `client.auth` | `whoami` |
| `client.outlets` | `list`, `get`, `list_products`, `list_countries`, `list_states`, `list_cities`, `list_tags`, `list_disclaimers` |
| `client.products` | `get`, `list_listings`, `list_categories` |
| `client.orders` | `list`, `get`, `create_checkout` |
| `client.order_items` | `list` |
| `client.profiles` | `list_team_profiles`, `list_orders`, `list_order_items`, `list_campaigns` |
| `client.campaigns` | `list`, `get`, `create`, `update`, `list_articles`, `article_status_counts`, `assign_order_items`, `link_questionnaire` |
| `client.articles` | `get`, `update`, `approve_brief`, `approve_draft` |
| `client.files` | `list`, `get`, `upload`, `download`, `move`, `delete` |
| `client.folders` | `list`, `create`, `rename`, `delete` |

Each method's docstring includes the required token scope.

## Documentation

Full documentation lives at **<https://annjawn.github.io/py-presscart/>** — Sphinx site built from `docs/` and deployed automatically by [`.github/workflows/docs.yml`](.github/workflows/docs.yml) on every push to `main`.

Build locally:

```bash
uv sync --group docs
uv run sphinx-build -b html -n -W --keep-going docs docs/_build/html
open docs/_build/html/index.html

# Or with live reload:
uv run sphinx-autobuild docs docs/_build/html --watch src/pypresscart
```

## Development

```bash
uv sync --group dev
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv build
```

### Pre-commit hooks

This repo ships a [`.pre-commit-config.yaml`](.pre-commit-config.yaml) with ruff,
mypy, whitespace/EOL/yaml/toml checks, and a pytest hook on `pre-push`.

```bash
uv run pre-commit install                      # ruff + mypy on every commit
uv run pre-commit install --hook-type pre-push # pytest on every push
uv run pre-commit run --all-files              # run everything now
```

## License

MIT — see [LICENSE](LICENSE).

> Presscart™ and the Presscart logo are trademarks of their respective owners. This library is an independent, unofficial client.
