"""The ``vitepress`` Sphinx builder.

Subclasses sphinx-markdown-builder's ``MarkdownBuilder`` (MIT, Liran Funaro):
the base class provides outdated-doc tracking, ``.md`` writing, and
``get_target_uri`` (extension-suffixed links, which VitePress resolves).
This class swaps in the VitePress translator; sidebar/config generation and
``objects.inv`` emission land here in ``finish()`` during M2/M4.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from sphinx.locale import __
from sphinx_markdown_builder.builder import MarkdownBuilder

import sphinx_vitepress
from sphinx_vitepress.config_writer import write_project_files
from sphinx_vitepress.inventory import write_inventory
from sphinx_vitepress.translator import VitepressTranslator


class VitepressBuilder(MarkdownBuilder):
    name = "vitepress"
    epilog = __("The VitePress markdown files are in %(outdir)s.")

    default_translator_class = VitepressTranslator

    def init(self) -> None:
        super().init()
        # The base class treats a doc as up to date when the target .md is
        # newer than its source — but our OUTPUT FORMAT changes across
        # sphinx-vitepress releases. Stamp the outdir with the version that
        # produced it and force a full rewrite on mismatch.
        self._version_stamp = Path(self.outdir) / ".sphinx-vitepress-version"
        try:
            previous = self._version_stamp.read_text(encoding="utf-8").strip()
        except OSError:
            previous = None
        self._rewrite_all = previous != sphinx_vitepress.__version__

    def get_outdated_docs(self) -> Iterator[str]:
        if self._rewrite_all:
            yield from self.env.found_docs
        else:
            yield from super().get_outdated_docs()

    def finish(self) -> None:
        super().finish()
        write_project_files(self)
        if self.config.vitepress_write_inventory:
            write_inventory(self)
        self._version_stamp.write_text(sphinx_vitepress.__version__ + "\n", encoding="utf-8")
