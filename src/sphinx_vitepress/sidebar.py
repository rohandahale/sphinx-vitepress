"""Sidebar and nav generation from Sphinx's toctree structure.

Each ``.. toctree::`` becomes a VitePress sidebar group: its ``:caption:``
is the group heading and its entries are the items, recursing into the
toctrees those entries declare. Captioned groups also become nav dropdowns,
which is how a multi-section manual reads as a menu rather than a flat row.

Titles come from the toctree entries themselves where the author supplied
one, and from ``env.titles`` otherwise.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sphinx import addnodes

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

#: Guard against pathological nesting (and any toctree cycle we missed).
_MAX_DEPTH = 6


def _title_of(env: BuildEnvironment, docname: str) -> str:
    node = env.titles.get(docname)
    return node.astext() if node is not None else docname


def _is_external(target: str) -> bool:
    return "://" in target or target.startswith("mailto:")


def _toctrees(env: BuildEnvironment, docname: str) -> list[addnodes.toctree]:
    try:
        doctree = env.get_doctree(docname)
    except FileNotFoundError:  # pragma: no cover - stale environment
        return []
    return list(doctree.findall(addnodes.toctree))


def _items_for(
    env: BuildEnvironment, docname: str, seen: set[str], depth: int
) -> list[dict[str, Any]]:
    """Sidebar items contributed by the toctrees inside ``docname``."""
    if depth > _MAX_DEPTH:
        return []
    items: list[dict[str, Any]] = []
    for toctree in _toctrees(env, docname):
        for title, target in toctree["entries"]:
            if _is_external(target):
                items.append({"text": title or target, "link": target})
                continue
            if target in seen:
                continue
            seen.add(target)
            item: dict[str, Any] = {
                "text": title or _title_of(env, target),
                "link": f"/{target}",
            }
            children = _items_for(env, target, seen, depth + 1)
            if children:
                item["items"] = children
                item["collapsed"] = False
            items.append(item)
    return items


def build_sidebar(env: BuildEnvironment) -> list[dict[str, Any]]:
    """Nested VitePress sidebar mirroring the root document's toctrees."""
    root = env.config.root_doc
    seen: set[str] = {root}
    sidebar: list[dict[str, Any]] = []

    for toctree in _toctrees(env, root):
        caption = toctree.get("caption")
        entries: list[dict[str, Any]] = []
        for title, target in toctree["entries"]:
            if _is_external(target):
                entries.append({"text": title or target, "link": target})
                continue
            if target in seen:
                continue
            seen.add(target)
            item: dict[str, Any] = {
                "text": title or _title_of(env, target),
                "link": f"/{target}",
            }
            children = _items_for(env, target, seen, 1)
            if children:
                item["items"] = children
                item["collapsed"] = False
            entries.append(item)

        if not entries:
            continue
        if caption:
            sidebar.append({"text": caption, "items": entries, "collapsed": False})
        else:
            sidebar.extend(entries)
    return sidebar


def build_nav(sidebar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Top navigation: home, then each sidebar group as a dropdown.

    A captioned group (one with items but no page of its own) becomes a
    VitePress nav dropdown; a plain page becomes a direct link.
    """
    nav: list[dict[str, Any]] = [{"text": "Home", "link": "/"}]
    for item in sidebar[:6]:
        if "link" not in item and item.get("items"):
            nav.append(
                {
                    "text": item["text"],
                    "items": [
                        {"text": child["text"], "link": child["link"]}
                        for child in item["items"]
                        if "link" in child
                    ],
                }
            )
        elif "link" in item:
            nav.append({"text": item["text"], "link": item["link"]})
    return nav
