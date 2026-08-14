"""Documentation for sphinx-vitepress, built with sphinx-vitepress."""

import os
import sys
from importlib.metadata import version as _package_version

sys.path.insert(0, os.path.abspath("../src"))

project = "sphinx-vitepress"
author = "Rohan Dahale"
copyright = "2026, Rohan Dahale"
# Underscore-prefixed so Sphinx does not treat the import as a config value.
release = _package_version("sphinx-vitepress")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "myst_parser",
    "sphinx_vitepress",
]

myst_enable_extensions = ["dollarmath", "colon_fence"]
napoleon_numpy_docstring = True
napoleon_google_docstring = False
autodoc_typehints = "description"
autodoc_member_order = "bysource"

# ADRs are internal decision records kept in the repository, not user docs.
exclude_patterns = ["_build", "adr/*"]

REPO = "https://github.com/rohandahale/sphinx-vitepress"

# Offline mode keeps CI and tests off the network.
if os.environ.get("SVP_OFFLINE"):
    intersphinx_mapping = {}
else:
    intersphinx_mapping = {
        "python": ("https://docs.python.org/3", None),
        "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    }


# -- sphinx-vitepress -------------------------------------------------------

vitepress_repo = REPO
# Each documented object links to the exact lines that define it. CI builds
# pin the commit so a released version keeps pointing at its own code;
# local builds track main.
vitepress_source_url = f"{REPO}/blob/{os.environ.get('GITHUB_SHA', 'main')}"
vitepress_footer_message = (
    'Built with <a href="https://github.com/rohandahale/sphinx-vitepress">sphinx-vitepress</a>'
)
vitepress_accent = "blue"

vitepress_frontmatter = {
    "index": {
        "layout": "home",
        "hero": {
            "name": "sphinx-vitepress",
            "text": "Sphinx power, VitePress polish",
            "tagline": (
                "A Sphinx builder that renders your documentation with VitePress. "
                "Keep autodoc, docstrings and intersphinx, lose the dated theme."
            ),
            "actions": [
                {"theme": "brand", "text": "Get started", "link": "/guide/getting-started"},
                {"theme": "alt", "text": "Configuration", "link": "/guide/configuration"},
                {"theme": "alt", "text": "GitHub", "link": REPO},
            ],
        },
        "features": [
            {
                "title": "Keep your conf.py",
                "details": (
                    "autodoc, napoleon, intersphinx and MyST are read-side extensions. "
                    "Point sphinx-build at a new builder and your project is unchanged."
                ),
            },
            {
                "title": "Cross-references both ways",
                "details": (
                    "intersphinx resolves outward as always, and your site publishes an "
                    "objects.inv so other projects can link straight back into it."
                ),
            },
            {
                "title": "Versioned deploys",
                "details": (
                    "One command builds stable/ and dev/ trees with a version picker and "
                    "a root redirect, ready to push to GitHub Pages."
                ),
            },
        ],
    }
}
