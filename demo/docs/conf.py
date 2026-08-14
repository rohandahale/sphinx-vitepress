import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "vpdemo"
author = "Rohan Dahale"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

myst_enable_extensions = ["dollarmath"]
napoleon_google_docstring = False
napoleon_numpy_docstring = True

# Tests set VPDEMO_OFFLINE so builds never touch the network.
if os.environ.get("VPDEMO_OFFLINE"):
    intersphinx_mapping = {}
else:
    intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

exclude_patterns = ["_build"]

# sphinx-vitepress: navbar GitHub icon + per-page edit links + footer.
vitepress_repo = "https://github.com/rohandahale/sphinx-vitepress"
vitepress_footer_message = "Built with sphinx-vitepress"
copyright = "2026, Rohan Dahale"

# VitePress hero landing page (the striking DocumenterVitepress look).
vitepress_frontmatter = {
    "index": {
        "layout": "home",
        "hero": {
            "name": "vpdemo",
            "text": "Sphinx power, VitePress polish",
            "tagline": "Autodoc, NumPy docstrings and intersphinx — rendered as a modern site.",
            "actions": [
                {"theme": "brand", "text": "Guide", "link": "/guide"},
                {"theme": "alt", "text": "API Reference", "link": "/api"},
            ],
        },
        "features": [
            {
                "title": "Keep your conf.py",
                "details": "autodoc, napoleon and MyST are read-side extensions; "
                "nothing about your Sphinx project changes.",
            },
            {
                "title": "Real cross-references",
                "details": "intersphinx resolves outward, and an objects.inv is "
                "published so other projects can link back in.",
            },
            {
                "title": "Versioned deploys",
                "details": "one command builds stable/dev folders with a version "
                "picker, ready for GitHub Pages.",
            },
        ],
    }
}
