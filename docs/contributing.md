# Contributing

Thanks for helping improve `pypresscart`.

## Ground rules

- Runtime deps stay at `requests` + `pydantic`. If you think you need a third, open an issue first.
- Single sync client. No async variant without a clear design proposal.
- Every new endpoint method needs matching Pydantic models and at least one test.
- Every public method supports dual-mode (Pydantic **and** dict). See [Dual-Mode I/O](dual-mode.md).

## Local setup

```bash
git clone https://github.com/pypresscart/py-presscart.git
cd py-presscart
uv sync --group dev
```

Activate pre-commit hooks:

```bash
uv run pre-commit install                        # ruff + mypy on every commit
uv run pre-commit install --hook-type pre-push   # pytest on every push
```

## Development loop

```bash
uv run pytest -v                # unit tests
uv run pytest --cov             # with coverage (≥75% required)
uv run ruff check --fix .       # lint + autofix (includes isort)
uv run ruff format .            # format
uv run mypy src                 # type-check (strict)
```

Before opening a PR, all five commands must pass. The pre-commit hooks run the first three; the pre-push hook runs pytest.

## Building the library

```bash
uv build
# produces dist/pypresscart-<version>-py3-none-any.whl
#          dist/pypresscart-<version>.tar.gz
```

## Adding a new endpoint

When Presscart ships a new endpoint:

1. Locate (or add) the spec in `api-docs/api-reference-<resource>.md`.
2. Add or extend the Pydantic model(s) in `src/pypresscart/models/<resource>.py`.
3. Add a method on the corresponding `*Resource` class in `src/pypresscart/resources/<resource>.py`. Include the scope in its docstring.
4. Re-export user-facing model types from `src/pypresscart/__init__.py`.
5. Add tests under `tests/test_<resource>.py`: happy path, dual-mode coverage, one error path if interesting.
6. Run the full dev loop.
7. Update the matching docs page (e.g. `docs/resource-<name>.md`) and `docs/models-reference.md`.

## Adding a new resource

If Presscart adds a whole new resource group:

1. Create `src/pypresscart/models/<name>.py`.
2. Create `src/pypresscart/resources/<name>.py` with a `<Name>Resource(ResourceBase)` class.
3. Wire it into `PresscartClient.__init__` as `self.<name>: <Name>Resource = <Name>Resource(self)`.
4. Re-export from `pypresscart/__init__.py`.
5. Add a docs page: `docs/resource-<name>.md`.
6. Add a `toctree` entry in `docs/index.md` and the resource table in the project `README.md`.

## Commits and PRs

- Commit messages describe **why**, not **what**. `fix` for bug fixes, `feat` for additions, `refactor` for non-behavioral changes, `docs` for documentation.
- **Do not add `Co-Authored-By: Claude ...` trailers** (or any AI attribution) to commits.
- Rebase on `main` before opening a PR; squash noise into meaningful commits.

## Releasing

Releases are cut from `main` by maintainers. See the release skill in `.claude/skills/release/` for the full procedure. In short:

```bash
# bump src/pypresscart/_version.py AND pyproject.toml
uv build
uv publish                          # needs UV_PUBLISH_TOKEN
git tag v<X.Y.Z> && git push --tags
```

## Docs

Docs in `docs/` build a Sphinx site deployed to [GitHub Pages](https://pypresscart.github.io/py-presscart/) by `.github/workflows/docs.yml`. See `docs/README.md` in the repo for the local authoring workflow.

## Code of conduct

Be kind. Assume good faith. Flag issues, not people.
