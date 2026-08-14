"""Emit a Sphinx ``objects.inv`` for the built VitePress site.

Only Sphinx's HTML builders write an inventory natively, so we do it
ourselves: every documented object (``py:*`` roles, ``std:doc`` pages,
``std:label`` targets) becomes resolvable FROM other Sphinx projects via
ordinary intersphinx. The file goes to ``public/`` under the source root
(VitePress's static-assets directory), which is copied verbatim to the
site root, exactly where intersphinx looks (``<site>/objects.inv``).
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from sphinx.util import logging
from sphinx.util.inventory import InventoryFile

from sphinx_vitepress.translator import VIRTUAL_PAGES

if TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.builders import Builder
    from sphinx.environment import BuildEnvironment

    from sphinx_vitepress.builder import VitepressBuilder

logger = logging.getLogger(__name__)


class _HtmlUriBuilder:
    """``get_target_uri`` shim for ``InventoryFile.dump``.

    Internal markdown links use ``docname.md`` (resolved by VitePress at
    build time), but inventory URIs are consumed by OTHER sites and must
    point at the served routes: ``docname.html`` works both with and
    without ``cleanUrls``, since the file exists on disk either way.
    """

    def __init__(self, builder: VitepressBuilder) -> None:
        self._builder = builder

    def get_target_uri(self, docname: str, typ: str | None = None) -> str:
        return f"{docname}.html"

    def __getattr__(self, name: str) -> Any:
        return getattr(self._builder, name)


def write_inventory(builder: VitepressBuilder) -> None:
    """Write ``objects.inv`` for the built site.

    Parameters
    ----------
    builder : sphinx_vitepress.builder.VitepressBuilder
        The running builder; its output directory receives the file.
    """
    public = Path(builder.outdir) / "public"
    public.mkdir(parents=True, exist_ok=True)
    target = public / "objects.inv"
    with _without_virtual_pages(builder.env):
        InventoryFile.dump(str(target), builder.env, cast("Builder", _HtmlUriBuilder(builder)))
    logger.info("sphinx-vitepress: wrote %s", target)


@contextmanager
def _without_virtual_pages(env: BuildEnvironment) -> Iterator[None]:
    """Hide the HTML-only index pages while the inventory is written.

    The std domain advertises ``genindex``/``modindex``/``py-modindex``/
    ``search`` as labels. This builder never emits those pages, so leaving
    them in the inventory hands other projects cross-references that 404.
    """
    # Go through the domain object: that is what InventoryFile.dump reads.
    # Both mappings matter, since get_objects falls back to anonlabels for
    # any name missing from labels.
    domain = env.domains.standard_domain
    labels = {name: domain.labels.pop(name) for name in VIRTUAL_PAGES if name in domain.labels}
    anon = {
        name: domain.anonlabels.pop(name) for name in VIRTUAL_PAGES if name in domain.anonlabels
    }
    try:
        yield
    finally:
        domain.labels.update(labels)
        domain.anonlabels.update(anon)
