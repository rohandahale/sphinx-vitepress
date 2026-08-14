from __future__ import annotations

from pathlib import Path

from sphinx.cmd.build import build_main

from sphinx_vitepress.frontmatter import render

ROOTS = Path(__file__).parent / "roots"


def test_empty_frontmatter_renders_nothing() -> None:
    assert render({}) == ""


def test_frontmatter_is_json_which_is_valid_yaml() -> None:
    block = render({"layout": "home", "hero": {"name": "x"}})
    assert block.startswith("---\n") and block.endswith("---\n\n")
    assert '"layout": "home"' in block


def test_frontmatter_precedes_page_content(tmp_path: Path) -> None:
    rc = build_main(["-b", "vitepress", "-q", str(ROOTS / "test-frontmatter"), str(tmp_path)])
    assert rc == 0

    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert index.startswith("---\n")
    assert '"layout": "home"' in index
    assert "café ✨" in index, "unicode must not be \\u-escaped"
    assert index.index("---\n", 4) < index.index("# Frontmatter Page")

    # Pages without configured frontmatter stay untouched.
    assert (tmp_path / "plain.md").read_text(encoding="utf-8").startswith("# Plain Page")
