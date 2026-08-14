"""Pruning dead index links must not take real content with it.

The collapse step is scoped to containers an actual removal emptied. A
sweep over the whole document instead blanked pages: a page whose only
content was Sphinx's stock "Indices and tables" block came out as a
0-byte file, and unrelated placeholder headings vanished.
"""

from __future__ import annotations

from pathlib import Path

from sphinx.cmd.build import build_main

ROOTS = Path(__file__).parent / "roots"


def build(out: Path) -> None:
    rc = build_main(["-b", "vitepress", "-q", str(ROOTS / "test-prune"), str(out)])
    assert rc == 0


def test_a_page_of_only_index_links_keeps_its_title(tmp_path: Path) -> None:
    build(tmp_path)
    page = (tmp_path / "only-indices.md").read_text(encoding="utf-8")

    assert page.strip(), "the page must not be emptied"
    assert "# Only Indices" in page, "its title must survive"
    # The dead block itself still goes.
    assert "Indices and tables" not in page
    assert "](genindex" not in page and "](search" not in page


def test_unrelated_empty_headings_are_untouched(tmp_path: Path) -> None:
    build(tmp_path)
    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "Empty Heading" in index, "an author's placeholder heading is content"
    assert "Intro prose." in index


def test_real_content_and_labels_survive(tmp_path: Path) -> None:
    build(tmp_path)
    page = (tmp_path / "keeps-content.md").read_text(encoding="utf-8")

    assert "Real body text that must survive." in page
    assert "Labelled Section" in page
    assert "kept-label" in page, "the :ref: target must still be reachable"
    # Only the trailing index-only section is removed.
    assert "## Indices {#" not in page
