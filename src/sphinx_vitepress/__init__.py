"""sphinx-vitepress — a Sphinx builder that renders documentation with VitePress."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sphinx_vitepress import accents

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
    # Site metadata for the generated .vitepress/config.mts; empty values
    # fall back to the Sphinx `project` name.
    app.add_config_value("vitepress_title", "", "html", str)
    app.add_config_value("vitepress_description", "", "html", str)
    app.add_config_value("vitepress_base", "/", "html", str)
    # "details": DocumenterVitepress-style <details> docstring blocks with
    # badges (default). "headings": plain ###-level signature headings.
    app.add_config_value("vitepress_docstring_style", "details", "html", str)
    # Write .vitepress/public/objects.inv so other Sphinx projects can
    # intersphinx-link INTO this site.
    app.add_config_value("vitepress_write_inventory", True, "html", bool)
    # Versioned deploys: the site root ABOVE the version folders (e.g.
    # "/my-repo/" while base is "/my-repo/v1/"). Set by `sphinx-vitepress
    # deploy`; when non-empty, the generated config injects versions.js /
    # siteinfo.js and a VersionPicker nav entry.
    app.add_config_value("vitepress_deploy_root", "", "html", str)
    # Repository URL — drives the navbar GitHub icon and, unless
    # vitepress_edit_link_pattern overrides it, the per-page "Edit this
    # page" link (whose path is derived by locating the source directory
    # inside the git working tree).
    app.add_config_value("vitepress_repo", "", "html", str)
    app.add_config_value("vitepress_edit_branch", "main", "html", str)
    app.add_config_value("vitepress_edit_link_pattern", "", "html", str)
    # Extra HTML shown above the copyright in the site footer.
    app.add_config_value("vitepress_footer_message", "", "html", str)
    # Logo and favicon default to Sphinx's own html_logo / html_favicon.
    app.add_config_value("vitepress_logo", "", "html", str)
    app.add_config_value("vitepress_favicon", "", "html", str)
    # Per-page VitePress frontmatter: {docname: {...}}. The main use is a
    # hero landing page ({"index": {"layout": "home", "hero": {...}}}).
    app.add_config_value("vitepress_frontmatter", {}, "html", dict)
    # Accent palette: a preset name ("afmhot", "viridis", "plasma", …), a
    # hex color, four hex stops (deep, mid, bright, glow), or a mapping
    # with separate "light"/"dark" entries. See sphinx_vitepress.accents.
    app.add_config_value("vitepress_accent", accents.DEFAULT, "html", (str, list, dict))

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
