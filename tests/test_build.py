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
    check_golden("basic-other.md", (tmp_path / "other.md").read_text(encoding="utf-8"))

    # The builder must leave a complete VitePress project behind.
    config = (tmp_path / ".vitepress" / "config.mts").read_text(encoding="utf-8")
    assert 'title: "basic"' in config
    assert '"text": "Other Page"' in config
    assert '"link": "/other"' in config
    assert "__SVP_" not in config, "all placeholders must be substituted"
    assert (tmp_path / "package.json").exists()


def test_myst(tmp_path: Path) -> None:
    build("test-myst", tmp_path)
    index = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "::: tip Note" in index
    assert "$$" in index
    assert "&#123;&#123; mustache }}" in index
    check_golden("myst-index.md", index)
