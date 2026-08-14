"""Inline toctree lists duplicate VitePress's sidebar, so they are dropped."""

from __future__ import annotations

from pathlib import Path

from sphinx.cmd.build import build_main

ROOTS = Path(__file__).parent / "roots"


def build(out: Path, *extra: str) -> str:
    rc = build_main(["-b", "vitepress", "-q", str(ROOTS / "test-toctree"), str(out), *extra])
    assert rc == 0
    return (out / "index.md").read_text(encoding="utf-8")


def test_inline_toctree_is_dropped_by_default(tmp_path: Path) -> None:
    index = build(tmp_path)
    assert "Intro prose that must survive." in index
    assert "Inner Page" not in index, "the sidebar already lists it"
    assert "Documentation" not in index, "the toctree caption goes with it"

    # …but the page is still in the sidebar and still gets built.
    config = (tmp_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")
    assert '"text": "Inner Page"' in config
    assert (tmp_path / "page.md").exists()


def test_inline_toctree_can_be_kept(tmp_path: Path) -> None:
    index = build(tmp_path, "-D", "vitepress_inline_toctree=1")
    assert "[Inner Page](page.md)" in index
    assert "Documentation" in index
