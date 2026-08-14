"""End-to-end builds of the test roots, compared against golden files.

Regenerate goldens after an intentional output change with::

    UPDATE_GOLDEN=1 uv run pytest tests/test_build.py
"""

from __future__ import annotations

import os
from pathlib import Path

from sphinx.cmd.build import build_main

ROOTS = Path(__file__).parent / "roots"
GOLDEN = Path(__file__).parent / "golden"


def build(root: str, out: Path) -> None:
    rc = build_main(["-b", "vitepress", "-W", "-q", str(ROOTS / root), str(out)])
    assert rc == 0, f"sphinx-build -b vitepress failed for {root}"


def check_golden(name: str, produced: str) -> None:
    golden_path = GOLDEN / name
    if os.environ.get("UPDATE_GOLDEN"):
        golden_path.parent.mkdir(parents=True, exist_ok=True)
        golden_path.write_text(produced, encoding="utf-8")
    expected = golden_path.read_text(encoding="utf-8")
    assert produced == expected, f"{name} drifted from golden output"


def test_basic_rst(tmp_path: Path) -> None:
    build("test-basic", tmp_path)
    index = (tmp_path / "index.md").read_text(encoding="utf-8")

    # Load-bearing VitePress features, asserted independently of the goldens:
    assert "::: tip Note" in index
    assert "::: warning Warning" in index
    assert "::: danger Danger" in index
    assert "::: info Custom Box" in index
    assert "::: info See also" in index
    assert "{#" in index, "headings should carry explicit anchors"
    assert "&#123;&#123; mustache }}" in index, "prose mustaches must be Vue-escaped"
    assert "<span v-pre>`{{ name }}`</span>" in index, "inline-code mustaches must be v-pre'd"
    assert "1 &lt; 2 &gt; 0" in index, "angle brackets in prose must be entity-escaped"
    assert "```python" in index

    check_golden("basic-index.md", index)

    other = (tmp_path / "other.md").read_text(encoding="utf-8")
    # Sphinx's stock "Indices and tables" boilerplate points at pages only
    # the HTML builders synthesize; as links they'd fail VitePress's
    # dead-link check, so they must degrade to plain text.
    assert "](genindex" not in other and "](search" not in other
    assert "* Index\n" in other and "* Search Page\n" in other
    check_golden("basic-other.md", other)

    # The builder must leave a complete VitePress project behind.
    config = (tmp_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")
    assert 'title: "basic"' in config
    assert '"text": "Other Page"' in config
    assert '"link": "/other"' in config
    assert "__SVP_" not in config, "all placeholders must be substituted"
    assert (tmp_path / "package.json").exists()
    assert (tmp_path / ".vitepress" / "theme" / "style.css").exists()
    assert (tmp_path / ".vitepress" / "theme" / "docstrings.css").exists()


def test_site_chrome_from_config(tmp_path: Path) -> None:
    """Repo/footer/logo settings reach themeConfig, and the edit-link path
    is derived from where the source dir sits in the git working tree."""
    rc = build_main(
        [
            "-b",
            "vitepress",
            "-q",
            str(ROOTS / "test-basic"),
            str(tmp_path),
            "-D",
            "vitepress_repo=https://github.com/example/proj",
            "-D",
            "copyright=2026, Example",
            "-D",
            "vitepress_footer_message=Built with sphinx-vitepress",
        ]
    )
    assert rc == 0
    config = (tmp_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")

    assert '"icon": "github"' in config
    assert '"link": "https://github.com/example/proj"' in config
    assert "Copyright © 2026, Example" in config
    assert "Built with sphinx-vitepress" in config
    # This repo's test root lives at tests/roots/test-basic.
    assert (
        '"pattern": "https://github.com/example/proj/edit/main/tests/roots/test-basic/:path"'
        in config
    )


def test_no_chrome_without_repo(tmp_path: Path) -> None:
    build("test-basic", tmp_path)
    config = (tmp_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")
    assert "socialLinks: []" in config
    assert "editLink: null" in config, "no repo configured -> no edit link"


def test_stale_outputs_refresh_when_version_changes(tmp_path: Path) -> None:
    """Upgrading sphinx-vitepress must rewrite outputs even when the doc
    sources themselves are unchanged (the output FORMAT changed)."""
    build("test-basic", tmp_path)

    (tmp_path / "index.md").write_text("stale junk from an older release\n", encoding="utf-8")
    style = tmp_path / ".vitepress" / "theme" / "style.css"
    style.write_text("/* stale theme */\n", encoding="utf-8")
    (tmp_path / ".sphinx-vitepress-version").write_text("0.0.0\n", encoding="utf-8")

    build("test-basic", tmp_path)  # incremental build, sources untouched

    assert "stale junk" not in (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "svp-hot" in style.read_text(encoding="utf-8"), "bundled theme must refresh"


def test_myst(tmp_path: Path) -> None:
    build("test-myst", tmp_path)
    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "::: tip Note" in index
    assert "$$" in index
    assert "&#123;&#123; mustache }}" in index
    check_golden("myst-index.md", index)
