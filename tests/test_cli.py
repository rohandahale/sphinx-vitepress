from __future__ import annotations

from pathlib import Path

import pytest

from sphinx_vitepress import __version__
from sphinx_vitepress.cli import main

ROOTS = Path(__file__).parent / "roots"


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "build" in capsys.readouterr().out


def test_build_no_build_generates_complete_project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "site"
    rc = main(["build", str(ROOTS / "test-basic"), str(out), "--no-build"])
    assert rc == 0
    assert (out / "index.md").exists()
    assert (out / ".vitepress" / "config.mts").exists()
    assert (out / "package.json").exists()
    assert "VitePress config written" in capsys.readouterr().out


def test_init_scaffolds_and_refuses_overwrite(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    assert main(["init", str(docs)]) == 0
    assert (docs / "conf.py").exists()
    assert (docs / "index.md").exists()
    assert main(["init", str(docs)]) == 1  # refuses to clobber


def test_init_never_destroys_an_existing_index(tmp_path: Path) -> None:
    """An index.md with no conf.py beside it was silently overwritten."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Mine\n", encoding="utf-8")

    assert main(["init", str(docs)]) == 1
    assert (docs / "index.md").read_text(encoding="utf-8") == "# Mine\n"
    assert not (docs / "conf.py").exists(), "and nothing else is written either"


def test_init_result_builds(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    assert main(["init", str(docs)]) == 0
    out = tmp_path / "site"
    assert main(["build", str(docs), str(out), "--no-build"]) == 0
    assert (out / ".vitepress" / "config.mts").exists()


def test_deploy_requires_arguments() -> None:
    with pytest.raises(SystemExit):
        main(["deploy"])  # source, --deploy-dir, and --release/--dev are required


def test_deploy_validates_repo_base(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        ["deploy", "unused-src", "--deploy-dir", str(tmp_path), "--dev", "--repo-base", "repo"]
    )
    assert rc == 2
    assert "start and end with '/'" in capsys.readouterr().out
