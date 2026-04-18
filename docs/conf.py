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

html_theme = "furo"
html_title = f"pypresscart {release}"
html_static_path = ["_static"]
html_last_updated_fmt = "%Y-%m-%d"

html_theme_options: dict = {
    "source_repository": "https://github.com/annjawn/py-presscart/",
    "source_branch": "main",
    "source_directory": "docs/",
    "top_of_page_buttons": ["view", "edit"],
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/annjawn/py-presscart",
            "html": (
                '<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">'
                '<path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>'
                "</svg>"
            ),
            "class": "",
        },
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
