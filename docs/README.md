# docs/

Sphinx source for the **pypresscart** documentation site.

- **Live site**: <https://pypresscart.github.io/py-presscart/>
- **Theme**: [Furo](https://pradyunsg.me/furo/)
- **Markdown parser**: [MyST](https://myst-parser.readthedocs.io/) (MyST markdown, not RST)
- **API reference**: auto-generated via `sphinx.ext.autosummary` from source docstrings
- **CI**: built + deployed by [`.github/workflows/docs.yml`](../.github/workflows/docs.yml) on every push to `main`

## Local development

```bash
# From the repo root
uv sync --group docs

# Clean build (same flags CI uses — warnings fail the build)
uv run sphinx-build -b html -n -W --keep-going docs docs/_build/html
open docs/_build/html/index.html

# Live reload while editing
uv run sphinx-autobuild docs docs/_build/html --watch src/pypresscart
# → open http://127.0.0.1:8000

# Inside docs/, use the Makefile shortcuts
cd docs
make html      # build
make clean     # wipe _build and _autosummary
make livehtml  # autobuild with watching
make linkcheck # validate external URLs
```

## Authoring

- Every page is a single `.md` file under `docs/`. MyST markdown supports all standard features plus directives (`:::`), fields (`:name: value`), tab sets, grids, etc.
- **Internal links**: use relative markdown `[text](other-page.md)` or `[text](other-page.md#anchor)`. Don't use GitHub-wiki `[[Page]]` syntax — that's gone.
- **Sphinx directives** inside markdown: wrap in an `eval-rst` block:
  ````md
  ```{eval-rst}
  .. autoclass:: pypresscart.PresscartClient
     :members:
  ```
  ````
- **Page structure**: one `#` h1 per page (becomes the page title). Sidebar titles and `toctree` captions are driven by [`index.md`](index.md).

## Adding a new page

1. Create `docs/<slug>.md` (lowercase, hyphenated).
2. Add the slug (no extension) to the appropriate `toctree` in [`index.md`](index.md).
3. Build locally — `-W` will flag orphan pages or broken refs.
4. Commit and push.

## API reference regeneration

The [API Reference](api-reference.md) page uses `autosummary :recursive:`. Stubs land under `_autosummary/` at build time and are **not committed**. If a new module or class isn't showing up:

- Confirm it's exported from `pypresscart/__init__.py` (or lives inside a listed submodule).
- `make clean && make html` — Sphinx caches autosummary output aggressively.

## Files

| Path | Purpose |
|---|---|
| `conf.py` | Sphinx configuration (theme, extensions, MyST settings, autodoc options) |
| `index.md` | Landing page; drives sidebar via `toctree` |
| `api-reference.md` | Auto-generated API docs anchor |
| `installation.md` … `resource-*.md` | Hand-written narrative pages |
| `_static/` | Custom CSS, images (currently empty) |
| `_templates/` | Optional custom Sphinx templates |
| `Makefile`, `make.bat` | Convenience wrappers around `sphinx-build` |
| `requirements.txt` | Mirror of the `docs` dep group for non-uv environments |
| `README.md` | This file — excluded from the Sphinx build |
