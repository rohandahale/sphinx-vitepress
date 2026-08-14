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
    assert "blackbody_flux" in api
    assert '<a id="vpdemo.core.blackbody_flux"></a>' in api, "signatures must be anchored"
    assert "&#123;&#123;" in api, "docstring mustaches must be Vue-escaped"
    assert "$$" in api, "docstring math must survive"

    guide = (tmp_path / "guide.md").read_text(encoding="utf-8")
    assert "::: " in guide, "admonitions must become containers"
