"""The ``sphinx-vitepress`` command line interface.

``build`` and ``dev`` run Sphinx with the ``vitepress`` builder (markdown +
generated ``.vitepress/config.mts`` + ``package.json``) and then hand the
output to the real VitePress via npm/npx. ``init`` scaffolds a minimal docs
source directory. ``deploy`` (versioned gh-pages trees) lands in M4.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sphinx_vitepress import __version__
from sphinx_vitepress.nodejs import NodeToolchainError, run_vitepress

_DEFAULT_OUTPUT = "_build/vitepress"

_CONF_TEMPLATE = """\
project = "My Project"
author = "Me"

extensions = [
    "myst_parser",
    # "sphinx.ext.autodoc",
    # "sphinx.ext.napoleon",
    # "sphinx.ext.intersphinx",
]
myst_enable_extensions = ["dollarmath"]
exclude_patterns = ["_build"]

# sphinx-vitepress options (all optional):
# vitepress_title = "My Project"
# vitepress_description = "What this project does"
# vitepress_base = "/"
"""

_INDEX_TEMPLATE = """\
# My Project

Welcome! Preview this site with:

    sphinx-vitepress dev .

or build it with:

    sphinx-vitepress build .
"""


def _sphinx_build(source: str, output: str) -> int:
    from sphinx.cmd.build import build_main

    return build_main(["-b", "vitepress", "-q", source, output])


def cmd_build(args: argparse.Namespace) -> int:
    rc = _sphinx_build(args.source, args.output)
    if rc != 0:
        return rc
    print(f"markdown + VitePress config written to {args.output}")
    if args.no_build:
        return 0
    try:
        return run_vitepress(Path(args.output), "build")
    except NodeToolchainError as err:
        print(err)
        return 1


def cmd_dev(args: argparse.Namespace) -> int:
    rc = _sphinx_build(args.source, args.output)
    if rc != 0:
        return rc
    try:
        return run_vitepress(Path(args.output), "dev")
    except NodeToolchainError as err:
        print(err)
        return 1


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.directory)
    conf = target / "conf.py"
    index = target / "index.md"
    existing = [path for path in (conf, index) if path.exists()]
    if existing:
        for path in existing:
            print(f"{path} already exists; refusing to overwrite.")
        return 1
    target.mkdir(parents=True, exist_ok=True)
    conf.write_text(_CONF_TEMPLATE, encoding="utf-8")
    index.write_text(_INDEX_TEMPLATE, encoding="utf-8")
    print(f"initialized {target}/. Next: sphinx-vitepress dev {target}")
    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    from sphinx_vitepress.deploy import run_deploy
    from sphinx_vitepress.nodejs import NodeToolchainError

    version = None if args.dev else args.release
    try:
        return run_deploy(
            args.source,
            Path(args.deploy_dir),
            version=version,
            repo_base=args.repo_base,
            keep=args.keep,
            devurl=args.devurl,
        )
    except NodeToolchainError as err:
        print(err)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sphinx-vitepress",
        description="Render Sphinx documentation with VitePress.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    p_build = subparsers.add_parser("build", help="build markdown, then run `vitepress build`")
    p_build.add_argument("source", help="Sphinx source directory (contains conf.py)")
    p_build.add_argument("output", nargs="?", default=_DEFAULT_OUTPUT, help="output directory")
    p_build.add_argument(
        "--no-build",
        action="store_true",
        help="stop after markdown + config generation (no Node required)",
    )
    p_build.set_defaults(func=cmd_build)

    p_dev = subparsers.add_parser("dev", help="build markdown, then run `vitepress dev`")
    p_dev.add_argument("source", help="Sphinx source directory (contains conf.py)")
    p_dev.add_argument("output", nargs="?", default=_DEFAULT_OUTPUT, help="output directory")
    p_dev.set_defaults(func=cmd_dev)

    p_init = subparsers.add_parser("init", help="scaffold a minimal docs source directory")
    p_init.add_argument("directory", nargs="?", default="docs", help="target directory")
    p_init.set_defaults(func=cmd_init)

    p_deploy = subparsers.add_parser(
        "deploy",
        help="build a versioned deploy tree (one folder per version, versions.js, root redirect)",
    )
    p_deploy.add_argument("source", help="Sphinx source directory (contains conf.py)")
    p_deploy.add_argument(
        "--deploy-dir",
        required=True,
        help="target tree (e.g. a checkout of the gh-pages branch)",
    )
    which = p_deploy.add_mutually_exclusive_group(required=True)
    which.add_argument("--release", metavar="vX.Y.Z", help="deploy a release version")
    which.add_argument("--dev", action="store_true", help="deploy the dev version")
    p_deploy.add_argument(
        "--repo-base",
        default="/",
        help="site root above the version folders, e.g. /my-repo/ for GitHub project pages",
    )
    p_deploy.add_argument(
        "--keep",
        choices=["breaking", "minor", "patch"],
        default="breaking",
        help="which alias folders a release updates (default: breaking -> vX + stable)",
    )
    p_deploy.add_argument("--devurl", default="dev", help="folder name for dev builds")
    p_deploy.set_defaults(func=cmd_deploy)

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
