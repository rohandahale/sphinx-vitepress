"""The intersphinx round trip: our sites publish objects.inv, others link in.

Two directions are covered:
- inbound: the demo build's inventory contains resolvable ``.html`` URIs,
  and a second Sphinx project pointed at that inventory (as a local file)
  resolves ``:py:func:`` references into absolute links to the demo site.
- outbound already works by construction (intersphinx resolves before the
  builder runs) and is exercised by the demo's own configuration.
"""

from __future__ import annotations

import zlib
from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

DEMO_DOCS = Path(__file__).parent.parent / "demo" / "docs"
ROOTS = Path(__file__).parent / "roots"


def _build_demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("VPDEMO_OFFLINE", "1")
    out = tmp_path / "site"
    rc = build_main(["-b", "vitepress", "-q", str(DEMO_DOCS), str(out)])
    assert rc == 0
    return out


def _read_inventory_text(inv_path: Path) -> str:
    raw = inv_path.read_bytes()
    # Four '#' header lines, then a zlib-compressed body.
    body_start = 0
    for _ in range(4):
        body_start = raw.index(b"\n", body_start) + 1
    return zlib.decompress(raw[body_start:]).decode("utf-8")


def test_inventory_is_written_with_html_uris(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _build_demo(tmp_path, monkeypatch)
    inv = out / "public" / "objects.inv"
    assert inv.exists(), "objects.inv must land in public/ (copied verbatim to the site root)"

    text = _read_inventory_text(inv)
    # '$' means "anchor equals the object name" (Sphinx's compression).
    assert "vpdemo.core.blackbody_flux py:function 1 api.html#$ -" in text
    assert "vpdemo.core.Simulation py:class 1 api.html#$ -" in text
    assert "guide std:doc -1 guide.html Guide" in text
    assert ".md#" not in text, "inventory URIs must target served .html routes"


def test_second_project_resolves_into_our_site(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = _build_demo(tmp_path, monkeypatch)
    inv = out / "public" / "objects.inv"

    monkeypatch.setenv("VPDEMO_INV", str(inv))
    consumer_out = tmp_path / "consumer"
    rc = build_main(["-b", "vitepress", "-q", str(ROOTS / "test-xref"), str(consumer_out)])
    assert rc == 0

    index = (consumer_out / "index.md").read_text(encoding="utf-8")
    assert "https://demo.example/site/api.html#vpdemo.core.blackbody_flux" in index
    assert "https://demo.example/site/api.html#vpdemo.core.Simulation" in index
