---
name: dual-mode-invariant
description: Every resource method must accept Pydantic or dict input and return Pydantic or dict output.
applies_to: src/pypresscart/resources/*.py and any new endpoint method
---

# Rule: Dual-mode invariant

## The rule

Every public method on a `ResourceBase` subclass MUST:

1. **Accept either** a Pydantic request model **or** a plain `dict` for any
   request body or complex filter parameter.
2. **Return either** a Pydantic response model (the default) **or** a plain
   `dict`, controlled by:
   - Per-call: `as_json: bool | None = None` keyword argument.
   - Client default: `PresscartClient(response_mode="pydantic" | "json")`.
3. Be covered by **two** tests — one asserting the Pydantic return, one
   asserting the `dict` return — in `tests/test_dual_mode.py` or the
   resource-specific test file.

## Why

Users of this library fall into two camps: those who want strict typed
objects with IDE autocomplete, and those who are forwarding raw JSON to
downstream systems and don't want Pydantic in the middle. We serve both
without forking the API.

## How to apply

- Request serialization helper lives on `ResourceBase`:
  `self._serialize(obj)` — returns `obj.model_dump(exclude_none=True)` for
  Pydantic models and `obj` for dicts.
- Response parsing helper lives on `ResourceBase`:
  `self._parse(payload, model_cls, as_json)` — returns `payload` (dict) if
  the effective mode is JSON, else `model_cls.model_validate(payload)`.
- Resolve `as_json` via `self._client._resolve_mode(as_json)` so per-call
  overrides trump client default.

## Checklist before merging a new endpoint method

- [ ] Signature accepts `Model | dict` for body/filter params.
- [ ] Signature has `as_json: bool | None = None` keyword.
- [ ] Return annotation is `Model | dict` (or `Paginated[Model] | dict`).
- [ ] Uses `_serialize` for inputs, `_parse` for outputs.
- [ ] Two tests cover both modes.
