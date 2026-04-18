---
name: regen-docs-snapshot
description: Re-scrape https://docs.presscart.com into api-docs/ as Markdown. Use when Presscart ships new endpoints or updates the docs site.
---

# Regenerate `api-docs/` from docs.presscart.com

The library treats `api-docs/` as the source of truth. When the upstream docs
change, refresh the snapshot.

## Dependencies

```bash
uv add --group dev beautifulsoup4 httpx lxml markdownify
```

(These live in the dev group — they are NOT a runtime dependency.)

## Script (paste into a throwaway `scripts/scrape.py` and delete after)

```python
"""Scrape docs.presscart.com into api-docs/ as markdown.

Run with: uv run python scripts/scrape.py
"""
from __future__ import annotations

import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

BASE = "https://docs.presscart.com"
OUT = Path("api-docs")
OUT.mkdir(exist_ok=True)

# Enumerate routes by fetching the SPA route bundle. The bundle filename
# changes on each deploy; inspect the homepage HTML to find the current one.
HOMEPAGE = httpx.get(BASE, follow_redirects=True).text
route_asset = re.search(r'/assets/(routes-[^"]+\.js)', HOMEPAGE).group(1)
routes_js = httpx.get(f"{BASE}/assets/{route_asset}").text
routes = sorted(set(re.findall(r'"(/[a-z0-9/_-]+)"', routes_js)))

for route in routes:
    if route in ("/", "/api-reference"):
        continue
    url = f"{BASE}{route}"
    html = httpx.get(url, follow_redirects=True).text
    soup = BeautifulSoup(html, "lxml")
    main = soup.select_one("main") or soup
    md = markdownify(str(main), heading_style="ATX")
    slug = route.strip("/").replace("/", "-") + ".md"
    (OUT / slug).write_text(
        f"---\ntitle: {route}\nsource: {url}\n---\n\n{md}\n"
    )
    print("wrote", slug)
```

## Workflow

1. Run the script above.
2. `git diff api-docs/` — review added / removed / renamed endpoints.
3. For each new or changed endpoint:
   - Update the Pydantic model in `src/pypresscart/models/<resource>.py` (invoke
     `pydantic-model-auditor` agent to double-check).
   - Add or update the method in `src/pypresscart/resources/<resource>.py`
     (invoke `api-fidelity-reviewer` agent).
   - Add tests.
4. Delete `scripts/scrape.py`. It's one-shot; we don't ship it.
5. Bump minor version via the `release` skill.

## Why isn't this committed as code?

The scraper is a one-shot maintenance tool. Shipping it as part of the library
would drag `httpx`/`bs4`/`markdownify` into either runtime or always-installed
dev deps for no user benefit. Keeping it as a skill recipe means it's
available when needed and invisible when not.
