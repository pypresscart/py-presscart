---
name: add-endpoint
description: Add a single new method to an existing resource class. Use when Presscart adds a new endpoint inside a resource group that already exists.
---

# Add an endpoint to an existing resource

## Steps

### 1. Read the doc entry for the new endpoint

Find it in `api-docs/api-reference-<resource>.md`. Note:
- HTTP method and path
- Required scope
- Path / query / body parameters
- Response shape

### 2. Add request/response models (if new) to `src/pypresscart/models/<resource>.py`

Reuse existing models where the shape already matches. Don't duplicate.

### 3. Add the method to `src/pypresscart/resources/<resource>.py`

Follow the dual-mode invariant. Template:

```python
def <verb>_<noun>(
    self,
    <path_param>: str,
    *,
    body: <RequestModel> | dict | None = None,
    as_json: bool | None = None,
) -> <ResponseModel> | dict:
    """<Verb> <noun>. Required scope: `<scope>`.

    See: https://docs.presscart.com/api-reference/<resource>
    """
    payload = self._client._request(
        "<METHOD>",
        f"/<path>/{<path_param>}",
        json=self._serialize(body) if body is not None else None,
    )
    return self._parse(payload, <ResponseModel>, as_json)
```

### 4. Re-export new model types from `src/pypresscart/__init__.py` if they're user-facing.

### 5. Add tests to `tests/test_<resource>.py`

- Happy path.
- Dual-mode coverage (both `as_json` values).
- One error path if the endpoint has interesting failure semantics (e.g. 403 for scope).

### 6. Verify

```
uv run ruff check --fix .
uv run mypy src
uv run pytest -v
```
