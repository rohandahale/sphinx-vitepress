"""Toctree captions become sidebar groups and nav dropdowns."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sphinx.cmd.build import build_main

ROOTS = Path(__file__).parent / "roots"


def _extract(config: str, key: str) -> Any:
    """Pull a JSON array out of the generated config.mts.

    The substituted arrays are dumped with indent=2, so the closing bracket
    of the array itself is the next one at column 0 (nested ones are
    indented).
    """
    match = re.search(rf"^\s*{key}: (\[.*?^\]),$", config, re.S | re.M)
    assert match, f"{key} not found in config"
    return json.loads(match.group(1))


def build(tmp_path: Path) -> tuple[list[Any], list[Any]]:
    rc = build_main(["-b", "vitepress", "-q", str(ROOTS / "test-nav"), str(tmp_path)])
    assert rc == 0
    config = (tmp_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")
    return _extract(config, "sidebar"), _extract(config, "nav")


def test_captions_become_collapsible_sidebar_groups(tmp_path: Path) -> None:
    sidebar, _ = build(tmp_path)

    manual = sidebar[0]
    assert manual["text"] == "Manual"
    assert "link" not in manual, "a caption is a heading, not a page"
    assert manual["collapsed"] is False
    assert [item["text"] for item in manual["items"]] == ["Guide", "Renamed Entry"]

    # Nesting continues into the pages' own toctrees.
    assert manual["items"][0]["items"][0]["text"] == "Guide Detail"
    assert manual["items"][0]["items"][0]["link"] == "/guide-detail"

    assert sidebar[1]["text"] == "Reference"
    assert sidebar[1]["items"][0]["link"] == "/api"

    # An uncaptioned toctree contributes its pages directly.
    assert {"text": "Loose Page", "link": "/loose"} in sidebar

    # `self` and the HTML-only index pages are legal toctree entries, but
    # this builder emits no such pages, and VitePress cannot catch a dead
    # link that lives in the generated config.
    links = {item.get("link") for item in sidebar}
    assert "/self" not in links and "/genindex" not in links


def test_captioned_groups_become_nav_dropdowns(tmp_path: Path) -> None:
    _, nav = build(tmp_path)

    assert nav[0] == {"text": "Home", "link": "/"}
    manual = next(entry for entry in nav if entry["text"] == "Manual")
    assert "link" not in manual, "dropdowns have items, not a link"
    assert [child["text"] for child in manual["items"]] == ["Guide", "Renamed Entry"]

    # Plain top-level pages stay direct links.
    assert {"text": "Loose Page", "link": "/loose"} in nav
