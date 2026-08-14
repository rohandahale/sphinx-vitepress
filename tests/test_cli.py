from __future__ import annotations

import pytest

from sphinx_vitepress import __version__
from sphinx_vitepress.cli import main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 2
    assert "sphinx-build -b vitepress" in capsys.readouterr().out


def test_stub_command_is_honest(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["build"]) == 2
    assert "not implemented" in capsys.readouterr().out
