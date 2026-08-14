"""Deploy assembles a published tree, so its failure modes destroy data.

`run_vitepress` is stubbed out here: these tests are about the tree
assembly around the VitePress build, not the build itself, which the
opt-in smoke test covers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sphinx_vitepress import deploy
from sphinx_vitepress.versions import determine_bases

ROOTS = Path(__file__).parent / "roots"
SOURCE = ROOTS / "test-basic"


def _stub_build(monkeypatch: pytest.MonkeyPatch, *, fail_on: str | None = None) -> None:
    """Stand in for VitePress: write an index.html into --outDir."""

    def fake(site: Path, command: str, extra: list[str] | None = None) -> int:
        assert extra and extra[0] == "--outDir"
        out = Path(extra[1])
        if fail_on and fail_on in out.name:
            return 1
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text("built\n", encoding="utf-8")
        return 0

    monkeypatch.setattr(deploy, "run_vitepress", fake)


def test_dev_deploy_preserves_existing_versions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_build(monkeypatch)
    (tmp_path / "v0.9").mkdir()
    (tmp_path / "v0.9" / "siteinfo.js").write_text('var DOCS_CURRENT_VERSION = "v0.9";\n')
    (tmp_path / "v0.9" / "index.html").write_text("old release\n", encoding="utf-8")

    assert deploy.run_deploy(str(SOURCE), tmp_path, version=None, repo_base="/p/") == 0

    assert (tmp_path / "v0.9" / "index.html").read_text() == "old release\n"
    assert (tmp_path / "dev" / "index.html").exists()
    assert (tmp_path / "versions.js").read_text() == 'var DOC_VERSIONS = ["dev", "v0.9"];\n'
    # No stable yet, so the root lands on dev.
    assert "url=dev/" in (tmp_path / "index.html").read_text(encoding="utf-8")


def test_a_failed_build_leaves_the_published_version_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_build(monkeypatch)
    assert deploy.run_deploy(str(SOURCE), tmp_path, version="v1.0.0", repo_base="/p/") == 0
    live = tmp_path / "stable" / "index.html"
    live.write_text("the published site\n", encoding="utf-8")

    # Now the stable build breaks; the live folder must survive untouched,
    # and versions.js must still describe the tree that is actually there.
    _stub_build(monkeypatch, fail_on="stable")
    assert deploy.run_deploy(str(SOURCE), tmp_path, version="v1.0.1", repo_base="/p/") != 0
    assert live.read_text(encoding="utf-8") == "the published site\n"
    assert "stable" in (tmp_path / "versions.js").read_text(encoding="utf-8")


def test_a_backport_does_not_move_stable_backwards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _stub_build(monkeypatch)
    assert deploy.run_deploy(str(SOURCE), tmp_path, version="v2.0.0", repo_base="/p/") == 0
    (tmp_path / "stable" / "index.html").write_text("v2 content\n", encoding="utf-8")

    assert deploy.run_deploy(str(SOURCE), tmp_path, version="v1.9.9", repo_base="/p/") == 0

    assert (tmp_path / "v1" / "index.html").exists(), "the old line is still published"
    assert (tmp_path / "stable" / "index.html").read_text() == "v2 content\n"


@pytest.mark.parametrize("devurl", ["/tmp/escape", "../escape", "a/b", "..", ""])
def test_devurl_must_be_a_plain_folder_name(devurl: str) -> None:
    with pytest.raises(ValueError, match="devurl"):
        determine_bases(None, devurl=devurl)


def test_deploy_reports_a_bad_devurl_instead_of_deleting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_build(monkeypatch)
    victim = tmp_path / "victim"
    victim.mkdir()
    (victim / "data.txt").write_text("precious\n", encoding="utf-8")

    rc = deploy.run_deploy(
        str(SOURCE), tmp_path / "site", version=None, repo_base="/p/", devurl=str(victim)
    )
    assert rc == 2
    assert "devurl" in capsys.readouterr().out
    assert (victim / "data.txt").read_text() == "precious\n"
