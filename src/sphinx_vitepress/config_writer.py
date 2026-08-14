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

from sphinx_vitepress import accents
from sphinx_vitepress.sidebar import build_nav, build_sidebar

if TYPE_CHECKING:
    from sphinx_vitepress.builder import VitepressBuilder

logger = logging.getLogger(__name__)


def _json(value: Any, indent: int | None = None) -> str:
    """JSON for embedding in config.mts — real UTF-8, not \\uXXXX escapes."""
    return json.dumps(value, indent=indent, ensure_ascii=False)


TEMPLATE_DIR = Path(__file__).parent / "template"


def _git_relative_srcdir(srcdir: Path) -> str | None:
    """Path of ``srcdir`` relative to its git working tree, if any.

    Used to build an edit-link pattern that points at the real file in the
    repository (``docs/`` for a typical layout) without asking the user.
    """
    for candidate in [srcdir, *srcdir.parents]:
        if (candidate / ".git").exists():
            relative = srcdir.relative_to(candidate).as_posix()
            return relative if relative != "." else ""
    return None


def _edit_link(builder: VitepressBuilder) -> dict[str, str] | None:
    config = builder.config
    pattern = config.vitepress_edit_link_pattern
    if not pattern:
        if not config.vitepress_repo:
            return None
        relative = _git_relative_srcdir(Path(builder.srcdir).resolve())
        if relative is None:
            return None
        repo = config.vitepress_repo.rstrip("/")
        prefix = f"{relative}/" if relative else ""
        pattern = f"{repo}/edit/{config.vitepress_edit_branch}/{prefix}:path"
    return {"pattern": pattern, "text": "Edit this page on GitHub"}


def _copy_asset(builder: VitepressBuilder, setting: str, fallback: str) -> str | None:
    """Copy a logo/favicon into ``public/`` and return its site-root URL."""
    name = setting or fallback
    if not name:
        return None
    source = Path(builder.confdir) / name
    if not source.is_file():
        logger.warning("sphinx-vitepress: asset not found: %s", source)
        return None
    public = Path(builder.outdir) / "public"
    public.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, public / source.name)
    return f"/{source.name}"


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

    favicon = _copy_asset(builder, config.vitepress_favicon, config.html_favicon or "")
    if favicon:
        href = posixpath.join(config.vitepress_base, favicon.lstrip("/"))
        head.append(["link", {"rel": "icon", "href": href}])

    social_links = []
    if config.vitepress_repo:
        social_links.append({"icon": "github", "link": config.vitepress_repo})

    footer: dict[str, str] = {}
    if config.vitepress_footer_message:
        footer["message"] = config.vitepress_footer_message
    if config.copyright:
        footer["copyright"] = f"Copyright © {config.copyright}"

    logo = _copy_asset(builder, config.vitepress_logo, config.html_logo or "")

    return {
        "__SVP_TITLE__": _json(title),
        "__SVP_DESCRIPTION__": _json(description),
        "__SVP_BASE__": _json(config.vitepress_base),
        "__SVP_HEAD__": _json(head, indent=2),
        "__SVP_NAV__": _json(nav, indent=2),
        "__SVP_SIDEBAR__": _json(sidebar, indent=2),
        "__SVP_LOGO__": _json(logo),
        "__SVP_SOCIAL_LINKS__": _json(social_links, indent=2),
        "__SVP_EDIT_LINK__": _json(_edit_link(builder), indent=2),
        "__SVP_FOOTER__": _json(footer or None, indent=2),
        "__SVP_DEPLOY_ROOT_VALUE__": _json(deploy_root or config.vitepress_base),
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
    # otherwise ship the bundled theme, REFRESHING it every build so theme
    # updates in sphinx-vitepress releases actually reach existing outdirs.
    theme_dst = out_vp / "theme"
    if not (user_vp / "theme").is_dir():
        if theme_dst.exists():
            shutil.rmtree(theme_dst)
        shutil.copytree(TEMPLATE_DIR / "theme", theme_dst)
        (theme_dst / "accent.css").write_text(
            accents.render_css(builder.config.vitepress_accent), encoding="utf-8"
        )

    user_package = srcdir / "package.json"
    package_source = user_package if user_package.is_file() else TEMPLATE_DIR / "package.json"
    shutil.copyfile(package_source, outdir / "package.json")

    logger.info("sphinx-vitepress: wrote .vitepress/config.mts, theme, and package.json")
