from __future__ import annotations

from pathlib import Path

import pytest
from sphinx.cmd.build import build_main

from sphinx_vitepress.accents import DEFAULT, PRESETS, render_css, resolve

ROOTS = Path(__file__).parent / "roots"


def test_default_is_a_known_preset() -> None:
    assert DEFAULT in PRESETS
    assert resolve(None)["light"] == PRESETS[DEFAULT]


def test_preset_name_applies_to_both_modes() -> None:
    palette = resolve("viridis")
    assert palette["light"] == palette["dark"] == PRESETS["viridis"]


def test_per_mode_palettes() -> None:
    palette = resolve({"light": "plasma", "dark": "afmhot"})
    assert palette["light"] == PRESETS["plasma"]
    assert palette["dark"] == PRESETS["afmhot"]


def test_dark_defaults_to_light_when_omitted() -> None:
    palette = resolve({"light": "ocean"})
    assert palette["dark"] == PRESETS["ocean"]


def test_explicit_stops_and_single_color() -> None:
    stops = ["#111111", "#222222", "#333333", "#444444"]
    assert resolve(stops)["light"] == tuple(stops)
    assert resolve("#abc")["dark"] == ("#abc",) * 4


@pytest.mark.parametrize(
    "bad",
    ["not-a-color", ["#111111", "#222222"], ["#111111", "#222", "#333333", "nope"], 42],
)
def test_bad_values_are_rejected_with_guidance(bad: object) -> None:
    with pytest.raises((ValueError, TypeError)) as excinfo:
        resolve(bad)
    assert "vitepress_accent" in str(excinfo.value)


def test_render_css_defines_both_modes() -> None:
    css = render_css("viridis")
    assert ":root {" in css and ".dark {" in css
    assert "--svp-accent-deep: #3b528b;" in css


def test_accent_reaches_the_built_theme(tmp_path: Path) -> None:
    rc = build_main(
        [
            "-b",
            "vitepress",
            "-q",
            str(ROOTS / "test-basic"),
            str(tmp_path),
            "-D",
            "vitepress_accent=plasma",
        ]
    )
    assert rc == 0
    accent = (tmp_path / ".vitepress" / "theme" / "accent.css").read_text(encoding="utf-8")
    assert "--svp-accent-bright: #e16462;" in accent

    theme_entry = (tmp_path / ".vitepress" / "theme" / "index.ts").read_text(encoding="utf-8")
    assert "./accent.css" in theme_entry, "the generated file must actually be imported"
