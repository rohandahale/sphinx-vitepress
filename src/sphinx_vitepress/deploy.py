"""Assemble a versioned deploy tree (the DocumenterVitepress model).

Each base gets its own full VitePress build (asset URLs embed ``base``, so
folders cannot be copies of one another). The markdown workdir is reused
across bases, so ``npm install`` runs at most once per deploy.

Pushing the resulting tree to gh-pages is left to CI (see
.github/workflows/docs.yml for the reference workflow).
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from sphinx_vitepress.nodejs import run_vitepress
from sphinx_vitepress.versions import (
    collect_versions,
    determine_bases,
    write_root_redirect,
    write_siteinfo,
    write_versions_js,
)


def _release_key(name: str) -> tuple[int, ...] | None:
    try:
        return tuple(int(part) for part in name.removeprefix("v").split("."))
    except ValueError:
        return None


def _newer_release_deployed(deploy_dir: Path, version: str, *, devurl: str) -> str | None:
    """An already-deployed release folder newer than ``version``, if any."""
    this = _release_key(version)
    if this is None:
        return None
    for name in collect_versions(deploy_dir, devurl=devurl):
        other = _release_key(name)
        if other is not None and other > this[: len(other)]:
            return name
    return None


def run_deploy(
    source: str,
    deploy_dir: Path,
    *,
    version: str | None,
    repo_base: str = "/",
    keep: str = "breaking",
    devurl: str = "dev",
) -> int:
    """Build ``source`` into ``deploy_dir/<base>`` for every deploy base,
    then refresh ``versions.js`` and the root redirect. Returns an exit code.
    """
    from sphinx.cmd.build import build_main

    if not repo_base.startswith("/") or not repo_base.endswith("/"):
        print(f"--repo-base must start and end with '/', got {repo_base!r}")
        return 2

    deploy_dir.mkdir(parents=True, exist_ok=True)
    try:
        bases = determine_bases(version, keep=keep, devurl=devurl)
    except ValueError as err:
        print(err)
        return 2

    # Releasing an older line must not point `stable` back at it.
    if version is not None and "stable" in bases:
        newer = _newer_release_deployed(deploy_dir, version, devurl=devurl)
        if newer is not None:
            bases = [base for base in bases if base != "stable"]
            print(f"keeping stable at {newer} (newer than {version})")
    workdir = Path(tempfile.mkdtemp(prefix="sphinx-vitepress-deploy-"))
    markdown_dir = workdir / "markdown"

    try:
        for base in bases:
            rc = build_main(
                [
                    "-b",
                    "vitepress",
                    "-q",
                    "-E",
                    str(source),
                    str(markdown_dir),
                    "-D",
                    f"vitepress_base={repo_base}{base}/",
                    "-D",
                    f"vitepress_deploy_root={repo_base}",
                ]
            )
            if rc != 0:
                return rc

            # Build beside the live folder and swap only on success, so a
            # failed build never leaves a published version deleted.
            destination = deploy_dir / base
            staging = workdir / f"staged-{base}"
            code = run_vitepress(markdown_dir, "build", extra=["--outDir", str(staging.resolve())])
            if code != 0:
                return code
            write_siteinfo(staging, base)
            if destination.exists():
                shutil.rmtree(destination)
            shutil.move(str(staging), str(destination))
            print(f"deployed base {base}/")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    versions = collect_versions(deploy_dir, devurl=devurl)
    write_versions_js(deploy_dir, versions)
    if "stable" in versions:
        landing = "stable"
    elif devurl in versions:
        landing = devurl
    else:
        landing = versions[0] if versions else devurl
    write_root_redirect(deploy_dir, landing)
    print(f"deploy tree ready: {deploy_dir} (versions: {', '.join(versions)})")
    return 0
