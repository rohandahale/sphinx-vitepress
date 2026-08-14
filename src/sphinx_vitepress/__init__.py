"""sphinx-vitepress — a Sphinx builder that renders documentation with VitePress."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "0.1.0.dev0"


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the ``vitepress`` builder and its configuration values."""
    from sphinx_vitepress.builder import VitepressBuilder

    # Our builder subclasses sphinx-markdown-builder's, which registers the
    # markdown_* config values our translator reads.
    app.setup_extension("sphinx_markdown_builder")
    app.add_builder(VitepressBuilder)
    # How `raw:: html` blocks are emitted: "v-pre" wraps them so Vue does not
    # compile their contents (safe default), "passthrough" emits them verbatim
    # (for trusted HTML that needs Vue), "drop" removes them.
    app.add_config_value("vitepress_raw_html", "v-pre", "html", str)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
