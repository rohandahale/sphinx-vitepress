"""Source links must reach the exact lines that define an object."""

from __future__ import annotations

import re
from pathlib import Path

from sphinx.cmd.build import build_main

from sphinx_vitepress.linkcode import make_resolver

BASE = "https://github.com/example/proj/blob/main"
DEMO_DOCS = Path(__file__).parent / "demo" / "docs"


def test_resolver_points_at_a_line_range() -> None:
    resolve = make_resolver(BASE)
    url = resolve("py", {"module": "sphinx_vitepress.escape", "fullname": "escape_vue"})

    assert url is not None
    # Path is relative to the git working tree, not the filesystem root.
    assert url.startswith(f"{BASE}/src/sphinx_vitepress/escape.py#L")
    match = re.search(r"#L(\d+)-L(\d+)$", url)
    assert match, url
    start, end = int(match.group(1)), int(match.group(2))
    assert 0 < start <= end, "a real, ordered line range"


def test_different_objects_get_different_ranges() -> None:
    resolve = make_resolver(BASE)
    first = resolve("py", {"module": "sphinx_vitepress.accents", "fullname": "resolve"})
    second = resolve("py", {"module": "sphinx_vitepress.accents", "fullname": "render_css"})
    assert first != second, "linking every object to the same file top is the bug"


def test_methods_and_classes_resolve() -> None:
    resolve = make_resolver(BASE)
    for fullname in ("VitepressBuilder", "VitepressBuilder.write_doc"):
        url = resolve("py", {"module": "sphinx_vitepress.builder", "fullname": fullname})
        assert url and "builder.py#L" in url, fullname


def test_unknown_targets_are_declined_rather_than_guessed() -> None:
    resolve = make_resolver(BASE)
    assert resolve("js", {"module": "whatever", "fullname": "x"}) is None
    assert resolve("py", {"module": "", "fullname": "x"}) is None
    assert resolve("py", {"module": "no.such.module.exists", "fullname": "x"}) is None


def test_trailing_slash_does_not_double_up() -> None:
    resolve = make_resolver(BASE + "/")
    url = resolve("py", {"module": "sphinx_vitepress.escape", "fullname": "escape_vue"})
    assert url and "//src/" not in url


def test_setting_produces_source_badges(tmp_path: Path, monkeypatch) -> None:
    """The config value alone should wire up linkcode."""
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")
    rc = build_main(
        [
            "-b",
            "vitepress",
            "-q",
            str(DEMO_DOCS),
            str(tmp_path),
            "-D",
            f"vitepress_source_url={BASE}",
        ]
    )
    assert rc == 0
    api = (tmp_path / "api.md").read_text(encoding="utf-8")
    assert '<Badge class="source-link"' in api
    assert re.search(rf"{re.escape(BASE)}/tests/demo/vpdemo/core\.py#L\d+-L\d+", api)


def test_source_badges_stay_clickable_in_the_theme(tmp_path: Path, monkeypatch) -> None:
    """The badge sits inside <summary>, which disables anchors by default.

    Without an explicit override the click falls through to the summary and
    collapses the card instead of opening the source.
    """
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")
    rc = build_main(["-b", "vitepress", "-q", str(DEMO_DOCS), str(tmp_path)])
    assert rc == 0

    css = (tmp_path / ".vitepress" / "theme" / "docstrings.css").read_text(encoding="utf-8")
    override = css.index(".docstring.custom-block summary .source-link a")
    blanket = css.index(".docstring.custom-block summary a")
    assert blanket < override, "the override has to come after the rule it undoes"
    assert "pointer-events: auto" in css[override:]
