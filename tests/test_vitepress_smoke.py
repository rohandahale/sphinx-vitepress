"""Opt-in end-to-end proof: sphinx -> markdown -> real `vitepress build`.

Heavy (npm install + node build), so it only runs when VITEPRESS_SMOKE=1.
VitePress's dead-link check is on (its default), so a broken internal link
in the generated markdown fails this test.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

DEMO_DOCS = Path(__file__).parent.parent / "demo" / "docs"

pytestmark = pytest.mark.skipif(
    not os.environ.get("VITEPRESS_SMOKE"),
    reason="set VITEPRESS_SMOKE=1 to run the real VitePress build (needs node, npm, network)",
)

PACKAGE_JSON = """\
{
  "private": true,
  "type": "module",
  "devDependencies": {
    "vitepress": "^1.6.4",
    "markdown-it-mathjax3": "^4"
  }
}
"""

CONFIG_MTS = """\
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'vpdemo',
  description: 'sphinx-vitepress demo',
  markdown: { math: true },
  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide' },
      { text: 'API', link: '/api' },
    ],
    sidebar: [
      { text: 'Guide', link: '/guide' },
      { text: 'API Reference', link: '/api' },
    ],
    search: { provider: 'local' },
  },
})
"""


def test_vitepress_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")
    site = tmp_path / "site"
    rc = build_main(["-b", "vitepress", "-q", str(DEMO_DOCS), str(site)])
    assert rc == 0

    (site / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
    vp_dir = site / ".vitepress"
    vp_dir.mkdir()
    (vp_dir / "config.mts").write_text(CONFIG_MTS, encoding="utf-8")

    npm = shutil.which("npm")
    npx = shutil.which("npx")
    assert npm and npx, "npm/npx are required for the smoke test"

    subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=site, check=True)
    subprocess.run([npx, "--no-install", "vitepress", "build", "."], cwd=site, check=True)

    dist = vp_dir / "dist"
    assert (dist / "index.html").exists()
    assert (dist / "guide.html").exists()
    assert (dist / "api.html").exists()
