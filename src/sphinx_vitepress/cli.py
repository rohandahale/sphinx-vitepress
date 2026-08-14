"""Command-line interface skeleton.

The subcommands are stubs until their milestones land (see DESIGN.md §F):
``init``/``dev``/``build`` arrive in M2, ``deploy`` in M4. Markdown output
already works today through the standard Sphinx entry point:
``sphinx-build -b vitepress <sourcedir> <outdir>``.
"""

from __future__ import annotations

import argparse

from sphinx_vitepress import __version__

_PLANNED = {
    "init": "scaffold a VitePress-ready docs project (lands in M2)",
    "dev": "build markdown and serve it with `vitepress dev` (lands in M2)",
    "build": "build markdown and run `vitepress build` (lands in M2)",
    "deploy": "assemble a versioned gh-pages tree (lands in M4)",
}

_FALLBACK = "Until then, build markdown with: sphinx-build -b vitepress <sourcedir> <outdir>"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sphinx-vitepress",
        description="Render Sphinx documentation with VitePress.",
        epilog=_FALLBACK,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    for name, help_text in _PLANNED.items():
        subparsers.add_parser(name, help=f"{help_text} — not implemented yet")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2

    print(f"sphinx-vitepress {args.command}: not implemented yet — {_PLANNED[args.command]}.")
    print(_FALLBACK)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
