---
name: add-resource
description: Scaffold a new API resource module (models + resource class + tests + client wiring) for the presscart SDK. Use when Presscart ships a new top-level resource group not yet covered.
---

# Add a new resource to presscart

Use this when there's a new resource in `api-docs/api-reference-<name>.md` that has no matching file in `src/pypresscart/resources/`.

## Steps

### 1. Verify the doc exists

```
ls api-docs/api-reference-<name>.md
```

If not, stop — the spec must land first.

### 2. Create `src/pypresscart/models/<name>.py`

Include:
- One Pydantic `BaseModel` per documented response shape.
- One Pydantic `BaseModel` per documented request body (suffix `Request`).
- Enums in `src/pypresscart/models/_common.py` if they're shared.
- All fields match the doc field-for-field, nullable where doc says `| null`.

### 3. Create `src/pypresscart/resources/<name>.py`

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from pypresscart.models.<name> import ...
from pypresscart.resources._base import ResourceBase

if TYPE_CHECKING:
    from pypresscart.client import PresscartClient


class <Name>Resource(ResourceBase):
    """<one-line description>."""

    def <method>(
        self,
        ...,
        *,
        as_json: bool | None = None,
    ) -> <Model> | dict:
        """<verb> <noun>. Required scope: `<scope>`."""
        payload = self._client._request("GET", "/...")
        return self._parse(payload, <Model>, as_json)
```

Every method must follow the dual-mode invariant ([.claude/rules/dual-mode-invariant.md](../../rules/dual-mode-invariant.md)).

### 4. Wire it into `PresscartClient.__init__`

In `src/pypresscart/client.py`:

```python
from pypresscart.resources.<name> import <Name>Resource
...
self.<name>: <Name>Resource = <Name>Resource(self)
```

### 5. Re-export from `src/pypresscart/__init__.py`

Add model classes and resource class to `__all__` where appropriate. Keep the public surface small — only re-export what users import.

### 6. Add `tests/test_<name>.py`

At minimum:
- One happy-path test per method using `responses`.
- One test asserting `as_json=True` returns a raw dict.
- One test asserting Pydantic return by default.
- One test for the first error path (e.g. 404).

### 7. Run the verification suite

```
uv run ruff check --fix .
uv run ruff format .
uv run mypy src
uv run pytest -v
```

All must pass before merge.

### 8. Spawn the auditors (optional but encouraged)

- `api-fidelity-reviewer` on the new resource file.
- `pydantic-model-auditor` on the new models file.
