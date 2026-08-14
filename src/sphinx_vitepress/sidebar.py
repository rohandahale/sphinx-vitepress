"""Sidebar and nav generation from Sphinx's toctree structure.

Reads ``env.toctree_includes`` (docname -> included docnames) and
``env.titles`` after the read phase — no doctree re-walking required.
Documents outside every toctree are, as in Sphinx itself, not listed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment


def _title_of(env: BuildEnvironment, docname: str) -> str:
    node = env.titles.get(docname)
    return node.astext() if node is not None else docname


def build_sidebar(env: BuildEnvironment) -> list[dict[str, Any]]:
    """Nested VitePress sidebar items mirroring the root document's toctree."""
    root = env.config.root_doc
    seen: set[str] = {root}

    def entry(docname: str) -> dict[str, Any]:
        item: dict[str, Any] = {"text": _title_of(env, docname), "link": f"/{docname}"}
        children = [child for child in env.toctree_includes.get(docname, []) if child not in seen]
        seen.update(children)
        if children:
            item["items"] = [entry(child) for child in children]
            item["collapsed"] = False
        return item

    top = [doc for doc in env.toctree_includes.get(root, []) if doc not in seen]
    seen.update(top)
    return [entry(doc) for doc in top]


def build_nav(sidebar: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Top navigation: home plus the first few top-level sidebar entries."""
    nav: list[dict[str, Any]] = [{"text": "Home", "link": "/"}]
    nav.extend({"text": item["text"], "link": item["link"]} for item in sidebar[:5])
    return nav
