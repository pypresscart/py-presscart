"""Sphinx configuration for pypresscart.

See https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the package importable for autodoc (not installed into the build env
# when running inside some CI reconfigurations).
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pypresscart._version import __version__  # noqa: E402

# -- Project information -----------------------------------------------------

project = "pypresscart"
author = "pypresscart contributors"
copyright = "2026, pypresscart contributors"
release = __version__
version = __version__

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
]

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

master_doc = "index"

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "README.md",
]

templates_path = ["_templates"]

# -- MyST ---------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "smartquotes",
    "substitution",
    "tasklist",
    "linkify",
]
myst_heading_anchors = 3

# -- autodoc / autosummary ----------------------------------------------------

autosummary_generate = True
autosummary_imported_members = False
autoclass_content = "class"
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "inherited-members": False,
    # Hide Pydantic v2 boilerplate that would otherwise swamp every model page.
    "exclude-members": ",".join(
        [
            "model_config",
            "model_fields",
            "model_computed_fields",
            "model_extra",
            "model_fields_set",
            "model_construct",
            "model_copy",
            "model_dump",
            "model_dump_json",
            "model_json_schema",
            "model_parametrized_name",
            "model_post_init",
            "model_rebuild",
            "model_validate",
            "model_validate_json",
            "model_validate_strings",
            "copy",
            "dict",
            "json",
            "parse_file",
            "parse_obj",
            "parse_raw",
            "from_orm",
            "schema",
            "schema_json",
            "update_forward_refs",
            "validate",
            "construct",
        ]
    ),
}
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# -- intersphinx --------------------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# -- HTML output --------------------------------------------------------------

html_theme = "shibuya"
html_title = "pypresscart"
html_baseurl = "https://pypresscart.github.io/py-presscart/"
html_static_path = ["_static"]
html_last_updated_fmt = "%Y-%m-%d"

html_context = {
    "source_type": "github",
    "source_user": "pypresscart",
    "source_repo": "py-presscart",
    "source_version": "main",
    "source_docs_path": "/docs/",
}

html_theme_options: dict = {
    "accent_color": "iris",
    "github_url": "https://github.com/pypresscart/py-presscart",
    "nav_links": [
        {"title": "PyPI", "url": "https://pypi.org/project/pypresscart/"},
        {"title": "Source", "url": "https://github.com/pypresscart/py-presscart"},
        {"title": "API", "url": "https://docs.presscart.com"},
    ],
}

# -- copybutton ---------------------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False

# -- nitpicky -----------------------------------------------------------------
# Treat unresolved cross-references as errors in strict mode only. We keep
# this off because MyST inline markdown links to anchors vary by extension.

nitpicky = False

# Silence noise from Pydantic-generated internals that aren't part of our
# public surface and unknown-domain refs from dunder docstrings.
nitpick_ignore_regex = [
    ("py:class", r"pydantic\..*"),
    ("py:obj", r"pydantic\..*"),
]
suppress_warnings = [
    "ref.class",
    "ref.python",
    "ref.obj",
]
