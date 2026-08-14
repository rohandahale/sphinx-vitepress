from __future__ import annotations

from pathlib import Path

import pytest

from sphinx_vitepress.versions import (
    collect_versions,
    determine_bases,
    write_root_redirect,
    write_siteinfo,
    write_versions_js,
)


def test_dev_build_gets_devurl() -> None:
    assert determine_bases(None) == ["dev"]
    assert determine_bases(None, devurl="latest") == ["latest"]


def test_breaking_keep_is_major_line_plus_stable() -> None:
    assert determine_bases("v1.2.3") == ["v1", "stable"]
    assert determine_bases("2.0.0") == ["v2", "stable"]


def test_zero_major_uses_minor_as_breaking_line() -> None:
    assert determine_bases("v0.3.2") == ["v0.3", "stable"]
    assert determine_bases("v0.3.2", keep="minor") == ["v0.3", "stable"]
    assert determine_bases("v0.3.2", keep="patch") == ["v0.3.2", "v0.3", "stable"]


def test_minor_and_patch_keep_policies() -> None:
    assert determine_bases("v1.2.3", keep="minor") == ["v1.2", "v1", "stable"]
    assert determine_bases("v1.2.3", keep="patch") == ["v1.2.3", "v1.2", "v1", "stable"]


def test_bad_inputs_raise() -> None:
    with pytest.raises(ValueError):
        determine_bases("not-a-version")
    with pytest.raises(ValueError):
        determine_bases("v1.2.3", keep="everything")


def _fake_base(deploy_dir: Path, name: str) -> None:
    base = deploy_dir / name
    base.mkdir(parents=True)
    write_siteinfo(base, name)


def test_version_index_assembly(tmp_path: Path) -> None:
    for name in ["v0.9", "stable", "dev", "v1", "v1.2"]:
        _fake_base(tmp_path, name)
    (tmp_path / "not-a-version").mkdir()  # no siteinfo.js -> ignored

    versions = collect_versions(tmp_path)
    assert versions == ["stable", "dev", "v1.2", "v1", "v0.9"]

    write_versions_js(tmp_path, versions)
    assert (tmp_path / "versions.js").read_text(encoding="utf-8") == (
        'var DOC_VERSIONS = ["stable", "dev", "v1.2", "v1", "v0.9"];\n'
    )

    write_root_redirect(tmp_path, "stable")
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "url=stable/" in index

    assert (tmp_path / "v1" / "siteinfo.js").read_text(encoding="utf-8") == (
        'var DOCS_CURRENT_VERSION = "v1";\n'
    )
