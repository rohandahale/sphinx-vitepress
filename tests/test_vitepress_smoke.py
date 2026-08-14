"""Opt-in end-to-end proof of the full user path.

``sphinx-vitepress build`` runs Sphinx, emits markdown plus the GENERATED
``.vitepress/config.mts`` and ``package.json``, then npm-installs and runs the
real ``vitepress build``. VitePress's dead-link check is on (its default), so
a broken internal link in the generated markdown fails this test.

Heavy (npm install + node build), so it only runs when VITEPRESS_SMOKE=1.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from sphinx_vitepress.cli import main as cli_main

DEMO_DOCS = Path(__file__).parent.parent / "demo" / "docs"

pytestmark = pytest.mark.skipif(
    not os.environ.get("VITEPRESS_SMOKE"),
    reason="set VITEPRESS_SMOKE=1 to run the real VitePress build (needs node, npm, network)",
)


def test_cli_build_produces_site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")
    site = tmp_path / "site"

    rc = cli_main(["build", str(DEMO_DOCS), str(site)])
    assert rc == 0

    config = (site / ".vitepress" / "config.mts").read_text(encoding="utf-8")
    assert "__SVP_" not in config

    dist = site / ".vitepress" / "dist"
    assert (dist / "index.html").exists()
    assert (dist / "guide.html").exists()
    assert (dist / "api.html").exists()
