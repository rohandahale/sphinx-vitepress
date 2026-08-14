"""Locate and drive the Node toolchain.

Only the CLI touches Node. The Sphinx builder itself always finishes with
markdown + config on disk, so docs can be generated on machines without Node
and built elsewhere.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class NodeToolchainError(RuntimeError):
    """A required Node tool is missing from PATH."""


def _require(tool: str) -> str:
    path = shutil.which(tool)  # resolves npm.cmd/npx.cmd on Windows
    if path is None:
        raise NodeToolchainError(
            f"'{tool}' was not found on PATH. Install Node.js >= 20 (https://nodejs.org), "
            "or pass --no-build to stop after markdown generation."
        )
    return path


def ensure_node_modules(site: Path) -> None:
    """Install the site's Node dependencies if they are missing or stale.

    The install is repeated when ``package.json`` changes, so upgrading
    sphinx-vitepress (which may pin a newer VitePress) does not keep
    building an existing output directory against the old dependencies.
    """
    stamp = site / "node_modules" / ".sphinx-vitepress-package.json"
    package = site / "package.json"
    current = package.read_text(encoding="utf-8") if package.is_file() else ""
    if (site / "node_modules").is_dir():
        try:
            if stamp.read_text(encoding="utf-8") == current:
                return
        except OSError:
            pass  # no stamp: an older layout, so reinstall once
    npm = _require("npm")
    try:
        subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=site, check=True)
    except subprocess.CalledProcessError as err:
        raise NodeToolchainError(
            f"`npm install` failed in {site} (exit status {err.returncode}). "
            "Check the output above; a network or registry problem is the usual cause."
        ) from err
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(current, encoding="utf-8")


def run_vitepress(site: Path, command: str, extra: list[str] | None = None) -> int:
    """Run ``vitepress <command>`` (build/dev) in ``site``; returns the exit code."""
    ensure_node_modules(site)
    npx = _require("npx")
    argv = [npx, "--no-install", "vitepress", command, ".", *(extra or [])]
    proc = subprocess.run(argv, cwd=site, check=False)
    return proc.returncode
