# CLAUDE.md — pypresscart Python SDK

This repo is a **PyPI-publishable Python client library** (unofficial) for the [Presscart API](https://docs.presscart.com). Design is modeled on [annjawn/loops-py](https://github.com/annjawn/loops-py). The package ships on PyPI as `pypresscart` and imports as `pypresscart`.

## Directory map

| Path | Purpose |
|---|---|
| `src/pypresscart/` | Library source (importable as `pypresscart`) |
| `src/pypresscart/client.py` | `PresscartClient` façade |
| `src/pypresscart/resources/` | One module per API resource group |
| `src/pypresscart/models/` | Pydantic request/response models |
| `src/pypresscart/_transport.py` | HTTP + retry internals |
| `src/pypresscart/exceptions.py` | `PresscartAPIError` + subclasses |
| `api-docs/` | **Source of truth** — scraped Presscart API docs. Do not edit. |
| `tests/` | pytest suite, mocks via `responses` |
| `examples/` | Runnable usage examples |
| `.claude/` | Local agent config (gitignored) |

## Core invariants

1. **Runtime dependencies are `requests` and `pydantic` only.** Nothing else. Stdlib otherwise.
2. **Dual-mode everywhere.** Every resource method accepts Pydantic models or plain `dict`s for requests, and returns Pydantic models by default or `dict`s when `as_json=True` (or client configured with `response_mode="json"`). See [.claude/rules/dual-mode-invariant.md](.claude/rules/dual-mode-invariant.md).
3. **`api-docs/` is the spec.** Before writing or modifying any resource method, cross-check against the relevant `api-docs/api-reference-*.md` file. Models must match documented response shapes field-for-field.
4. **One model module per resource.** New endpoint → add request/response models in `models/<resource>.py`, a method in `resources/<resource>.py`, and a test.
5. **Public surface = `pypresscart/__init__.py` re-exports only.** Modules starting with `_` are private.

## Common commands

```bash
uv sync                        # install + lock
uv sync --group dev            # install with dev deps
uv sync --group docs           # install docs deps (Sphinx, Furo, MyST)
uv run pytest -v               # run tests
uv run pytest --cov            # with coverage
uv run ruff check --fix .      # lint + autofix (includes import sort)
uv run ruff format .           # format
uv run mypy src                # type-check
uv build                       # build wheel + sdist into dist/
uv publish                     # publish to PyPI (requires UV_PUBLISH_TOKEN)

# Docs
uv run sphinx-build -b html -n -W --keep-going docs docs/_build/html   # clean build
uv run sphinx-autobuild docs docs/_build/html --watch src/pypresscart  # live reload
```

The docs site is at <https://pypresscart.github.io/py-presscart/>, deployed by
`.github/workflows/docs.yml` on every push to `main`. Source lives in `docs/`
(Sphinx + MyST + Furo theme, with autosummary-driven API reference).

## Hard rules

- **Never** add `Co-Authored-By: Claude ...` (or any Claude/Anthropic co-author trailer) to commit messages. See [.claude/rules/no-claude-coauthor.md](.claude/rules/no-claude-coauthor.md).
- **Never** commit `CLAUDE.md` or `.claude/` — both are gitignored.
- **Never** widen the runtime dependency list without explicit user approval. See [.claude/rules/library-hygiene.md](.claude/rules/library-hygiene.md).
- **Never** implement an async variant unless asked. Single sync client only.

## Skills available

- [`add-resource`](.claude/skills/add-resource/SKILL.md) — scaffold a new resource module.
- [`add-endpoint`](.claude/skills/add-endpoint/SKILL.md) — add a method to an existing resource.
- [`release`](.claude/skills/release/SKILL.md) — bump version, build, publish.
- [`regen-docs-snapshot`](.claude/skills/regen-docs-snapshot/SKILL.md) — re-scrape `api-docs/`.

## Agents available

- [`api-fidelity-reviewer`](.claude/agents/api-fidelity-reviewer.md) — verifies resource code matches `api-docs/`.
- [`pydantic-model-auditor`](.claude/agents/pydantic-model-auditor.md) — audits model fields against documented response shapes.

## PyPI publish checklist

- Name on PyPI is `pypresscart`. Verify it's still available before the first publish.
- Bump version in `src/pypresscart/_version.py` AND `pyproject.toml`'s `[project].version`.
- Run the full verification suite (ruff, mypy, pytest, build).
