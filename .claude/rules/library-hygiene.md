---
name: library-hygiene
description: Constraints that keep the presscart library minimal, robust, and lightweight.
applies_to: all edits under src/pypresscart/
---

# Rule: Library hygiene

## The rules

1. **Runtime dependencies are frozen at `requests` + `pydantic`.** Do not add a
   new runtime dep in `pyproject.toml`'s `[project.dependencies]` without
   explicit user approval. Dev-only tools go in `[dependency-groups].dev`.
2. **No async.** Single synchronous client. Don't add `httpx`, `aiohttp`, or
   `asyncio` code paths unless asked.
3. **No speculative abstractions.** No helper modules, mixins, or base classes
   without at least two concrete callers. Inline until the third duplication.
4. **Public surface = what's re-exported from `pypresscart/__init__.py`.**
   Everything else is `_private`. Modules starting with `_` stay internal.
5. **Typed throughout.** All public functions have full type hints. All public
   classes have short docstrings explaining purpose + one usage hint.
6. **No logging side effects at import time.** The library must not emit logs,
   read env vars, or touch the network when imported. All of that happens in
   `PresscartClient.__init__` or later.
7. **No global state.** No module-level mutable singletons. Everything hangs
   off a client instance.

## Why

This library is meant to be embedded in other people's apps. Each added
dependency, import-time side effect, or premature abstraction is friction the
user pays for forever.

## How to apply

- Before `uv add <pkg>`, stop and ask the user if it's a runtime need.
- When tempted to add a `utils.py`, put the code in the one place that uses
  it first.
- When tempted to re-export a new symbol from `__init__.py`, confirm the user
  actually needs that symbol public — otherwise keep it scoped.
