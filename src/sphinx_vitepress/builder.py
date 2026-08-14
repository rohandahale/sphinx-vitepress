"""The ``vitepress`` Sphinx builder.

Subclasses sphinx-markdown-builder's ``MarkdownBuilder`` (MIT, Liran Funaro):
the base class provides outdated-doc tracking, ``.md`` writing, and
``get_target_uri`` (extension-suffixed links, which VitePress resolves).
This class swaps in the VitePress translator; sidebar/config generation and
``objects.inv`` emission land here in ``finish()`` during M2/M4.
"""

from __future__ import annotations

from sphinx.locale import __
from sphinx_markdown_builder.builder import MarkdownBuilder

from sphinx_vitepress.config_writer import write_project_files
from sphinx_vitepress.translator import VitepressTranslator


class VitepressBuilder(MarkdownBuilder):
    name = "vitepress"
    epilog = __("The VitePress markdown files are in %(outdir)s.")

    default_translator_class = VitepressTranslator

    def finish(self) -> None:
        super().finish()
        write_project_files(self)
