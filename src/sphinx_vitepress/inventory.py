"""Emit a Sphinx ``objects.inv`` for the built VitePress site.

Only Sphinx's HTML builders write an inventory natively, so we do it
ourselves: every documented object (``py:*`` roles, ``std:doc`` pages,
``std:label`` targets) becomes resolvable FROM other Sphinx projects via
ordinary intersphinx. The file goes to ``public/`` under the source root
(VitePress's static-assets directory), which is copied verbatim to the
site root — exactly where intersphinx looks (``<site>/objects.inv``).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from sphinx.util import logging
from sphinx.util.inventory import InventoryFile

if TYPE_CHECKING:
    from sphinx.builders import Builder

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
    public = Path(builder.outdir) / "public"
    public.mkdir(parents=True, exist_ok=True)
    target = public / "objects.inv"
    InventoryFile.dump(str(target), builder.env, cast("Builder", _HtmlUriBuilder(builder)))
    logger.info("sphinx-vitepress: wrote %s", target)
