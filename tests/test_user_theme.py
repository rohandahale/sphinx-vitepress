"""A user-supplied theme replaces the bundled one but still gets accent.css.

Copying the bundled theme into ``<srcdir>/.vitepress/theme/`` is the
documented way to customize it. The copied entry point imports
``./accent.css``, which is generated rather than shipped, so failing to
write it into a user theme breaks the VitePress build with an unresolved
import.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from sphinx.cmd.build import build_main

from sphinx_vitepress.config_writer import TEMPLATE_DIR

CONF = """\
project = "usertheme"
extensions: list[str] = []
exclude_patterns = ["_build"]
vitepress_accent = "plasma"
"""


def _make_source(root: Path, with_theme: bool) -> Path:
    src = root / "src"
    src.mkdir(parents=True)
    (src / "conf.py").write_text(CONF, encoding="utf-8")
    (src / "index.rst").write_text("Home\n====\n\nBody.\n", encoding="utf-8")
    if with_theme:
        shutil.copytree(TEMPLATE_DIR / "theme", src / ".vitepress" / "theme")
    return src


def test_user_theme_still_gets_generated_accent(tmp_path: Path) -> None:
    src = _make_source(tmp_path, with_theme=True)
    out = tmp_path / "out"
    assert build_main(["-b", "vitepress", "-q", str(src), str(out)]) == 0

    theme = out / ".vitepress" / "theme"
    entry = (theme / "index.ts").read_text(encoding="utf-8")
    assert "./accent.css" in entry, "the theme entry point imports it..."
    accent = theme / "accent.css"
    assert accent.exists(), "...so it has to exist next to it"
    assert "--svp-accent-deep: #6a00a8;" in accent.read_text(encoding="utf-8"), (
        "the configured palette must reach a user theme too"
    )


def test_user_theme_files_are_not_replaced_by_the_bundled_ones(tmp_path: Path) -> None:
    src = _make_source(tmp_path, with_theme=True)
    (src / ".vitepress" / "theme" / "overrides.css").write_text("/* mine */\n", encoding="utf-8")
    out = tmp_path / "out"
    assert build_main(["-b", "vitepress", "-q", str(src), str(out)]) == 0

    overrides = (out / ".vitepress" / "theme" / "overrides.css").read_text(encoding="utf-8")
    assert overrides == "/* mine */\n", "a user theme wins over the bundled one"
