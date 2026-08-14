"""Build the bundled demo project (autodoc + napoleon + MyST) end to end."""

from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

DEMO_DOCS = Path(__file__).parent.parent / "demo" / "docs"


def test_demo_builds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")  # skip intersphinx network fetch
    rc = build_main(["-b", "vitepress", "-q", str(DEMO_DOCS), str(tmp_path)])
    assert rc == 0

    api = (tmp_path / "api.md").read_text(encoding="utf-8")
    assert '<details class="docstring custom-block" open>' in api
    assert (
        '<summary><a id="vpdemo.core.blackbody_flux" href="#vpdemo.core.blackbody_flux">' in api
    ), "signatures must be anchored in the summary"
    assert '<Badge type="info" text="function" />' in api
    assert '<Badge type="info" text="class" />' in api
    assert '<Badge type="info" text="property" />' in api
    assert "```python\nvpdemo.core.blackbody_flux(temperature: float)" in api
    assert api.count("</details>") == api.count('<details class="docstring custom-block" open>')
    assert "*[*" not in api, "napoleon type annotations must not emit emphasis soup"
    assert "&#123;&#123;" in api, "docstring mustaches must be Vue-escaped"
    assert "$$" in api, "docstring math must survive"

    guide = (tmp_path / "guide.md").read_text(encoding="utf-8")
    assert "::: " in guide, "admonitions must become containers"
