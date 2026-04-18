# Recipes

End-to-end workflows that glue multiple resources together.

---

## Table of contents

- [Run a full campaign workflow](#run-a-full-campaign-workflow)
- [Iterate every paginated resource](#iterate-every-paginated-resource)
- [Bulk outlet search with filters](#bulk-outlet-search-with-filters)
- [Monthly order report](#monthly-order-report)
- [Upload and attach a brand guide](#upload-and-attach-a-brand-guide)
- [Scope preflight](#scope-preflight)
- [Retry exhausted? Pause and alert](#retry-exhausted-pause-and-alert)
- [Share a single client in a web app](#share-a-single-client-in-a-web-app)

---

## Run a full campaign workflow

Create a campaign, place orders against it, assign the items to the campaign, and walk the article approval flow.

```python
from pypresscart import (
    CampaignCreateRequest,
    CheckoutLineItem,
    CheckoutRequest,
    PresscartClient,
)

with PresscartClient(api_token=os.environ["PRESSCART_API_TOKEN"]) as client:
    campaign = client.campaigns.create(
        CampaignCreateRequest(
            name="Q3 Launch",
            description="Announce v2.0",
            profile_id="prof_1",
            objectives="drive awareness",
            keywords="AI, SaaS, launch",
            target_audience="VPs of Engineering",
            tone="authoritative",
            writing_samples=None,
            file_id=None,
        )
    )

    order = client.orders.create_checkout(
        CheckoutRequest(
            profile_id="prof_1",
            line_items=[
                CheckoutLineItem(product_id="prod_featured"),
                CheckoutLineItem(product_id="prod_newsletter"),
            ],
        )
    )

    client.campaigns.assign_order_items(
        campaign.id,
        {"order_item_ids": [li.id for li in order.line_items]},
    )

    # Later, approve briefs + drafts as they come in
    for art in client.campaigns.list_articles(campaign.id).records:
        if art.status and art.status[0].name == "Brief Ready":
            client.articles.approve_brief(art.id)
```

---

## Iterate every paginated resource

A reusable paginator. Works for anything returning `Paginated[T]`.

```python
from collections.abc import Callable, Iterator
from typing import TypeVar

T = TypeVar("T")

def all_pages(call: Callable[..., "Paginated[T]"], /, **kwargs) -> Iterator[T]:
    page = 1
    while True:
        result = call(page=page, **kwargs)
        yield from result.records
        if result.next_page is None:
            return
        page = result.next_page

for order in all_pages(client.orders.list, limit=100):
    ...

for outlet in all_pages(client.outlets.list, limit=100, filters={"country": "United States"}):
    ...
```

---

## Bulk outlet search with filters

Find in-budget US outlets with high domain authority that accept do-follow links.

```python
def in_budget(min_cents: int, max_cents: int):
    yield from all_pages(
        client.outlets.list,
        limit=100,
        sort_by="domain_authority",
        order_by="desc",
        filters={
            "country": "United States",
            "is_do_follow": True,
            "pricing[min]": min_cents,
            "pricing[max]": max_cents,
            "domain_authority[min]": 50,
        },
    )

for o in in_budget(5000, 30000):
    print(o.outlet_name, o.channels[0].domain_authority, o.prices[0].unit_amount)
```

---

## Monthly order report

```python
from datetime import date, timedelta

start = date.today().replace(day=1)
end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

for profile in client.profiles.list_team_profiles(team_id).records:
    orders = list(
        all_pages(
            client.profiles.list_orders,
            profile_id=profile.id,
            limit=100,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            paid_orders_only=True,
        )
    )
    total = sum(o.total or 0 for o in orders) / 100
    print(f"{profile.name:30} ${total:>10,.2f}  ({len(orders)} orders)")
```

---

## Upload and attach a brand guide

```python
uploaded = client.files.upload(
    [("brand-guide-2026.pdf", open("brand-guide.pdf", "rb"), "application/pdf")],
    folder_id=folder.id,
).files[0]

client.campaigns.link_questionnaire(
    campaign.id,
    {
        "file_id": uploaded.file_key,
        "file_url": uploaded.file_url,
        "file_name": uploaded.name,
        "file_size": uploaded.size,
    },
)
```

---

## Scope preflight

Fail loudly before doing real work.

```python
REQUIRED = {"outlets.lists", "orders.create", "campaigns.create", "campaigns.update"}

info = client.auth.whoami()
if info.token_type != "full_access":
    missing = REQUIRED - set(info.scopes)
    if missing:
        raise SystemExit(f"token missing scopes: {sorted(missing)}")
```

---

## Retry exhausted? Pause and alert

`pypresscart` retries 429/5xx automatically. If it still fails, back off at the application level.

```python
import time
from pypresscart import RateLimitError, ServerError

def resilient_list_orders():
    while True:
        try:
            return client.orders.list(limit=100)
        except RateLimitError as exc:
            wait = exc.retry_after or 60
            print(f"rate limited — sleeping {wait}s")
            time.sleep(wait)
        except ServerError:
            time.sleep(30)  # back off and retry at app level
```

---

## Share a single client in a web app

Create one client at process startup, reuse it across request handlers.

```python
# fastapi example
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from pypresscart import PresscartClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.presscart = PresscartClient(
        api_token=os.environ["PRESSCART_API_TOKEN"],
        max_retries=5,
    )
    yield
    app.state.presscart.close()

app = FastAPI(lifespan=lifespan)

@app.get("/outlets")
def list_outlets(request: Request, limit: int = 20):
    client: PresscartClient = request.app.state.presscart
    # PresscartClient is sync — run in the threadpool:
    return client.outlets.list(limit=limit, as_json=True)
```

The `as_json=True` here avoids a Pydantic round-trip before FastAPI serializes the response.
