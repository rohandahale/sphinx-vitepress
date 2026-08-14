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
    bases = determine_bases(version, keep=keep, devurl=devurl)
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

            destination = deploy_dir / base
            if destination.exists():
                shutil.rmtree(destination)
            code = run_vitepress(
                markdown_dir, "build", extra=["--outDir", str(destination.resolve())]
            )
            if code != 0:
                return code
            write_siteinfo(destination, base)
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
