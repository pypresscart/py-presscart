---
name: release
description: Release a new version of presscart to PyPI. Use when preparing a version bump.
---

# Release presscart to PyPI

## Preflight

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -v --cov
```

All must pass. If anything fails, stop and fix.

## Steps

### 1. Bump version

Edit `src/pypresscart/_version.py`:

```python
__version__ = "X.Y.Z"
```

Update `pyproject.toml`'s `[project].version` to the same string.

Follow semver:
- PATCH for bug fixes.
- MINOR for backwards-compatible additions (new endpoints, new optional
  parameters).
- MAJOR for anything that could break existing callers (renames, removed
  fields, changed defaults).

### 2. Build

```bash
rm -rf dist/
uv build
```

Inspect `dist/` — should contain `pypresscart-X.Y.Z.tar.gz` and
`pypresscart-X.Y.Z-py3-none-any.whl`.

### 3. Sanity-install the wheel

```bash
uv run --no-project --with dist/pypresscart-X.Y.Z-py3-none-any.whl \
    python -c "from pypresscart import PresscartClient; print(PresscartClient.__module__)"
```

### 4. Publish

```bash
# Preferred: uv
UV_PUBLISH_TOKEN=pypi-... uv publish

# Fallback: twine
uv run twine upload dist/*
```

For TestPyPI first:

```bash
uv publish --publish-url https://test.pypi.org/legacy/
```

### 5. Tag & push

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 6. GitHub release

Draft a release on GitHub for the tag, with a changelog derived from the
commits since the previous tag. Remember: no Claude co-author trailers (see
[.claude/rules/no-claude-coauthor.md](../../rules/no-claude-coauthor.md)).
