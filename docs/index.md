---
hide-toc: true
---

# pypresscart

An unofficial, typed Python client library for the [Presscart API](https://docs.presscart.com).

:::{warning}
This project is **not affiliated with, endorsed by, or supported by Presscart**. It's a community-maintained Python client.
:::

```{toctree}
:hidden:
:caption: Get started

installation
getting-started
authentication-and-scopes
```

```{toctree}
:hidden:
:caption: Core concepts

client-configuration
dual-mode
error-handling
pagination
retry-and-timeouts
```

```{toctree}
:hidden:
:caption: Resources

resource-auth
resource-outlets
resource-products
resource-orders
resource-order-items
resource-profiles
resource-campaigns
resource-articles
resource-files
resource-folders
```

```{toctree}
:hidden:
:caption: Reference

api-reference
models-reference
recipes
contributing
changelog
```

## What you get

- **Typed resource methods**: `client.outlets.list(...)`, `client.orders.create_checkout(...)`, and 40+ more.
- **Dual-mode I/O**: pass Pydantic models *or* plain dicts; get Pydantic models *or* plain dicts back.
- **Minimal deps**: only `requests` and `pydantic` at runtime.
- **Built-in retries**: exponential backoff with jitter on 429 / 5xx, honoring `Retry-After`.
- **Typed exceptions**: `BadRequestError`, `AuthenticationError`, `RateLimitError`, and more.

## 60-second tour

```python
from pypresscart import PresscartClient

with PresscartClient(api_token="pc_...") as client:
    me = client.auth.whoami()
    print(me.team_id, me.scopes)

    for outlet in client.outlets.list(limit=5).records:
        print(outlet.outlet_name, outlet.website_url)
```

## Next steps

::::{grid} 1 2 2 2
:gutter: 3
:class-container: sd-mt-4

:::{grid-item-card} 🚀 Get started
:link: getting-started
:link-type: doc

Install, authenticate, and make your first API call.
:::

:::{grid-item-card} 🔧 Configure the client
:link: client-configuration
:link-type: doc

Timeouts, retries, JSON mode, custom sessions.
:::

:::{grid-item-card} 📚 Browse resources
:link: resource-outlets
:link-type: doc

Reference docs for every resource service.
:::

:::{grid-item-card} 🧪 Recipes
:link: recipes
:link-type: doc

End-to-end workflows: campaign setup, pagination, FastAPI wiring, more.
:::
::::

## Links

- **PyPI**: <https://pypi.org/project/pypresscart/>
- **Source**: <https://github.com/annjawn/py-presscart>
- **Issues**: <https://github.com/annjawn/py-presscart/issues>
- **Upstream API docs**: <https://docs.presscart.com>
