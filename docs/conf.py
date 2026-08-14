"""Documentation for sphinx-vitepress — built with sphinx-vitepress."""

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

project = "sphinx-vitepress"
author = "Rohan Dahale"
copyright = "2026, Rohan Dahale"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
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


def linkcode_resolve(domain, info):
    """Point each documented object at its source on GitHub."""
    if domain != "py" or not info.get("module"):
        return None
    path = info["module"].replace(".", "/")
    return f"{REPO}/blob/main/src/{path}.py"


# -- sphinx-vitepress -------------------------------------------------------

vitepress_repo = REPO
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
                "A Sphinx builder that renders your documentation with VitePress — "
                "keep autodoc, docstrings and intersphinx, lose the dated theme."
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
