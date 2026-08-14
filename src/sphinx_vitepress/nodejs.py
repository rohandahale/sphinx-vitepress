"""Locate and drive the Node toolchain.

Only the CLI touches Node — the Sphinx builder itself always finishes with
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
    """Run ``npm install`` in ``site`` unless node_modules already exists."""
    if (site / "node_modules").is_dir():
        return
    npm = _require("npm")
    subprocess.run([npm, "install", "--no-audit", "--no-fund"], cwd=site, check=True)


def run_vitepress(site: Path, command: str) -> int:
    """Run ``vitepress <command>`` (build/dev) in ``site``; returns the exit code."""
    ensure_node_modules(site)
    npx = _require("npx")
    proc = subprocess.run([npx, "--no-install", "vitepress", command, "."], cwd=site, check=False)
    return proc.returncode
