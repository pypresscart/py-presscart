---
name: release
description: Release a new version of presscart to PyPI. Use when preparing a version bump.
---

# Release presscart to PyPI

Releases go out via the **Release** GitHub Actions workflow, which uses
**OIDC trusted publishing** — no PyPI tokens are stored locally or in the
repo. Cutting a release means landing a bump PR on `main`, then dispatching
the workflow twice (TestPyPI, then PyPI). Never publish from a local machine.

## Preflight (local)

```bash
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -v --cov
```

All must pass. If anything fails, stop and fix.

## Steps

### 1. Decide the version

Follow semver:
- **PATCH** — bug fixes only.
- **MINOR** — backwards-compatible additions (new endpoints, new optional
  parameters).
- **MAJOR** — anything that could break existing callers (renames, removed
  fields, changed defaults, raised minimum Python).

### 2. Open a bump PR

From a branch, update all three:

- `src/pypresscart/_version.py` — `__version__ = "X.Y.Z"`
- `pyproject.toml` — `[project].version = "X.Y.Z"`
- `docs/changelog.md` — add a new `## [X.Y.Z] — <YYYY-MM-DD>` section under
  `## [Unreleased]` describing what changed, and bump the link refs at the
  bottom:
  - Update `[Unreleased]: .../compare/vX.Y.Z...HEAD`.
  - Add `[X.Y.Z]: .../releases/tag/vX.Y.Z`.

Open the PR against `main`. `main` is branch-protected — no direct pushes.
Wait for CI (ruff, ruff format, mypy, pytest across Python 3.10–3.13, and
the distribution build) to go green, then squash-merge.

### 3. Publish to TestPyPI

```bash
gh workflow run release.yml -f target=testpypi
gh run watch $(gh run list --workflow release.yml --limit 1 --json databaseId -q '.[0].databaseId') --exit-status
```

### 4. Smoke-test TestPyPI

```bash
uv run --no-project --index-strategy unsafe-best-match \
    --with pypresscart==X.Y.Z \
    --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    python -c "from pypresscart import PresscartClient, __version__; print(__version__)"
```

Also exercise whatever behavior the release is fixing/adding — instantiate
the affected model, call the affected resource method with a mocked or real
response, etc. A passing import is necessary but not sufficient.

### 5. Publish to PyPI

```bash
gh workflow run release.yml -f target=pypi
gh run watch $(gh run list --workflow release.yml --limit 1 --json databaseId -q '.[0].databaseId') --exit-status
```

If required reviewers are configured on the `pypi` environment, approve the
deployment when prompted.

### 6. Smoke-test PyPI

```bash
uv run --no-project --refresh \
    --with pypresscart==X.Y.Z \
    python -c "from pypresscart import __version__; print(__version__)"
```

`--refresh` avoids stale uv cache on the first install after publish. If the
version isn't resolvable yet, wait a minute for PyPI's index to catch up.

### 7. Tag and announce

```bash
git checkout main && git pull
git tag -a vX.Y.Z -m "pypresscart X.Y.Z"
git push origin vX.Y.Z

gh release create vX.Y.Z \
    --title "pypresscart X.Y.Z" \
    --notes "$(awk '/^## \[X\.Y\.Z\]/,/^## \[/' docs/changelog.md | sed '$d')"
```

Remember: no Claude co-author trailers (see
[.claude/rules/no-claude-coauthor.md](../../rules/no-claude-coauthor.md)).

## If something goes wrong

- **Published a broken version?** You can't overwrite a PyPI release. Cut a
  new patch release (`X.Y.Z+1`) that reverts or fixes the issue. `yank` on
  PyPI hides the broken version from resolvers but keeps it available to
  pinned installs.
- **TestPyPI upload failed but PyPI didn't run?** Re-dispatch with
  `target=testpypi`. The workflow has `skip-existing: true` on TestPyPI so
  re-uploading the same version is a no-op.
- **Trusted publisher rejected the OIDC token?** Confirm the pending
  publisher on PyPI has the exact workflow filename (`release.yml`) and
  environment name (`pypi` / `testpypi`). One-character typos fail silently.
