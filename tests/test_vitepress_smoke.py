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

DEMO_DOCS = Path(__file__).parent / "demo" / "docs"

pytestmark = [
    pytest.mark.smoke,
    pytest.mark.skipif(
        not os.environ.get("VITEPRESS_SMOKE"),
        reason="set VITEPRESS_SMOKE=1 to run the real VitePress build (needs node, npm, network)",
    ),
]


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
    assert (dist / "objects.inv").exists(), "inventory must be published at the site root"


def test_cli_deploy_builds_versioned_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")
    deploy_dir = tmp_path / "gh-pages"

    rc = cli_main(
        [
            "deploy",
            str(DEMO_DOCS),
            "--deploy-dir",
            str(deploy_dir),
            "--release",
            "v0.1.0",
            "--repo-base",
            "/demo/",
        ]
    )
    assert rc == 0

    # v0.1.0 with keep=breaking -> v0.1 + stable, each a full build.
    for base in ["v0.1", "stable"]:
        assert (deploy_dir / base / "index.html").exists()
        assert (deploy_dir / base / "api.html").exists()
        assert (deploy_dir / base / "objects.inv").exists()
        siteinfo = (deploy_dir / base / "siteinfo.js").read_text(encoding="utf-8")
        assert siteinfo == f'var DOCS_CURRENT_VERSION = "{base}";\n'

    stable_html = (deploy_dir / "stable" / "api.html").read_text(encoding="utf-8")
    assert "/demo/stable/" in stable_html, "the per-base `base` must be baked into asset URLs"
    assert "/demo/versions.js" in stable_html, "the version-picker head script must be injected"

    versions_js = (deploy_dir / "versions.js").read_text(encoding="utf-8")
    assert versions_js == 'var DOC_VERSIONS = ["stable", "v0.1"];\n'
    assert "url=stable/" in (deploy_dir / "index.html").read_text(encoding="utf-8")
