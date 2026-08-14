"""Emit the VitePress project files into the build output.

Follows DocumenterVitepress.jl's proven pattern: a template ``config.mts``
containing placeholders, filled by string substitution. A user-supplied
``<sourcedir>/.vitepress/`` directory overrides the bundled template (its
files are copied through, and placeholders in its ``config.mts`` — if any —
are still substituted), so full customization never requires forking us.
"""

from __future__ import annotations

import json
import posixpath
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sphinx.util import logging

from sphinx_vitepress.sidebar import build_nav, build_sidebar

if TYPE_CHECKING:
    from sphinx_vitepress.builder import VitepressBuilder

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "template"


def _substitutions(builder: VitepressBuilder) -> dict[str, str]:
    config = builder.config
    sidebar = build_sidebar(builder.env)
    nav = build_nav(sidebar)
    title = config.vitepress_title or config.project
    description = config.vitepress_description or f"Documentation for {config.project}"

    # Versioned deploys: inject the version-picker machinery. The deploy
    # command sets vitepress_deploy_root to the site root ABOVE the version
    # folders (e.g. "/my-repo/" while base is "/my-repo/v1/").
    deploy_root = config.vitepress_deploy_root
    head: list[Any] = []
    if deploy_root:
        head = [
            ["script", {"src": posixpath.join(deploy_root, "versions.js")}],
            ["script", {"src": posixpath.join(config.vitepress_base, "siteinfo.js")}],
        ]
        nav.append({"component": "VersionPicker"})

    return {
        "__SVP_TITLE__": json.dumps(title),
        "__SVP_DESCRIPTION__": json.dumps(description),
        "__SVP_BASE__": json.dumps(config.vitepress_base),
        "__SVP_HEAD__": json.dumps(head, indent=2),
        "__SVP_NAV__": json.dumps(nav, indent=2),
        "__SVP_SIDEBAR__": json.dumps(sidebar, indent=2),
        "__SVP_DEPLOY_ROOT_VALUE__": json.dumps(deploy_root or config.vitepress_base),
    }


def write_project_files(builder: VitepressBuilder) -> None:
    outdir = Path(builder.outdir)
    srcdir = Path(builder.srcdir)
    subs = _substitutions(builder)

    user_vp = srcdir / ".vitepress"
    out_vp = outdir / ".vitepress"
    if user_vp.is_dir():
        shutil.copytree(
            user_vp, out_vp, dirs_exist_ok=True, ignore=shutil.ignore_patterns("cache", "dist")
        )
    out_vp.mkdir(parents=True, exist_ok=True)

    user_config = user_vp / "config.mts"
    template = user_config if user_config.is_file() else TEMPLATE_DIR / "config.mts"
    content = template.read_text(encoding="utf-8")
    for placeholder, value in subs.items():
        content = content.replace(placeholder, value)
    (out_vp / "config.mts").write_text(content, encoding="utf-8")

    # Theme: the user's own .vitepress/theme (already copied above) wins;
    # otherwise ship the bundled DocumenterVitepress-derived theme.
    theme_dst = out_vp / "theme"
    if not theme_dst.exists():
        shutil.copytree(TEMPLATE_DIR / "theme", theme_dst)

    user_package = srcdir / "package.json"
    package_source = user_package if user_package.is_file() else TEMPLATE_DIR / "package.json"
    shutil.copyfile(package_source, outdir / "package.json")

    logger.info("sphinx-vitepress: wrote .vitepress/config.mts, theme, and package.json")
