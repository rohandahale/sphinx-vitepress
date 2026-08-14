"""Drop navigation that points at pages VitePress does not have.

Nearly every Sphinx project ends its index with the stock "Indices and
tables" block linking to ``genindex``/``modindex``/``search``. Only the
HTML builders synthesize those pages, so in a VitePress site the block is
a heading over two or three inert bullets.

Whole list items (or paragraphs) that consist of nothing but such a link
are removed, along with any list or section left empty as a result. A link
used *inside* a sentence is left in place — the translator renders it as
plain text, so the sentence still reads correctly.
"""

from __future__ import annotations

import posixpath

from docutils import nodes
from sphinx import addnodes

from sphinx_vitepress.translator import VIRTUAL_PAGES

#: Wrappers a bare link can sit in (Sphinx uses compact_paragraph in lists).
_WRAPPERS = (nodes.paragraph, nodes.list_item, addnodes.compact_paragraph)


def _is_virtual(ref: nodes.Element, suffix: str) -> bool:
    if not ref.get("internal", False):
        return False
    uri = ref.get("refuri", "")
    if not uri or "://" in uri:
        return False
    target = posixpath.basename(uri.split("#")[0])
    if suffix and target.endswith(suffix):
        target = target[: -len(suffix)]
    return target in VIRTUAL_PAGES


def _sole_content_container(ref: nodes.Element) -> nodes.Element | None:
    """Outermost ancestor whose entire text is this reference's text."""
    text = ref.astext()
    container: nodes.Element | None = None
    node: nodes.Element | None = ref.parent
    while isinstance(node, _WRAPPERS):
        if node.astext().strip() != text.strip():
            break
        container = node
        node = node.parent
    return container


def prune_virtual_page_links(doctree: nodes.document, suffix: str) -> None:
    for ref in list(doctree.findall(nodes.reference)):
        if not _is_virtual(ref, suffix):
            continue
        container = _sole_content_container(ref)
        if container is not None and container.parent is not None:
            container.parent.remove(container)

    # Collapse whatever the removals emptied out, innermost first.
    for _ in range(3):
        changed = False
        for empty_list in list(doctree.findall(nodes.bullet_list)):
            if not empty_list.children and empty_list.parent is not None:
                empty_list.parent.remove(empty_list)
                changed = True
        for section in list(doctree.findall(nodes.section)):
            body = [child for child in section.children if not isinstance(child, nodes.title)]
            if not body and section.parent is not None:
                section.parent.remove(section)
                changed = True
        if not changed:
            break
