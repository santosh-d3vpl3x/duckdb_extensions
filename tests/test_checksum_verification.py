import pytest

import add_extension_files as aef


def test_validate_download_inputs_accepts_supported_values():
    aef._validate_download_inputs("linux_amd64", "httpfs")


def test_validate_download_inputs_rejects_unsupported_architecture():
    with pytest.raises(ValueError, match="Unsupported architecture"):
        aef._validate_download_inputs("linux_ppc64le", "httpfs")


def test_validate_download_inputs_rejects_invalid_extension_name():
    with pytest.raises(ValueError, match="Invalid extension name"):
        aef._validate_download_inputs("linux_amd64", "httpfs;rm -rf /")


def test_allow_unverified_enabled_for_local(monkeypatch):
    monkeypatch.setenv(aef.ALLOW_UNVERIFIED_ENV, "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    assert aef._allow_unverified_downloads() is True


def test_allow_unverified_blocked_in_github_actions(monkeypatch):
    monkeypatch.setenv(aef.ALLOW_UNVERIFIED_ENV, "1")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(RuntimeError, match="blocked in GitHub Actions"):
        aef._allow_unverified_downloads()


def test_verify_download_checksum_passes_when_checksum_matches():
    checksums = {"v1.4.4": {"httpfs": {"linux_amd64": "a" * 64}}}
    aef._verify_download_checksum(
        checksums=checksums,
        duckdb_version="v1.4.4",
        extension_name="httpfs",
        duckdb_arch="linux_amd64",
        actual_sha256="a" * 64,
        allow_unverified=False,
    )


def test_verify_download_checksum_raises_on_missing_entry():
    checksums = {"v1.4.4": {"httpfs": {}}}
    with pytest.raises(RuntimeError, match="Missing checksum entry"):
        aef._verify_download_checksum(
            checksums=checksums,
            duckdb_version="v1.4.4",
            extension_name="httpfs",
            duckdb_arch="linux_amd64",
            actual_sha256="a" * 64,
            allow_unverified=False,
        )


def test_verify_download_checksum_raises_on_mismatch():
    checksums = {"v1.4.4": {"httpfs": {"linux_amd64": "b" * 64}}}
    with pytest.raises(RuntimeError, match="Checksum mismatch"):
        aef._verify_download_checksum(
            checksums=checksums,
            duckdb_version="v1.4.4",
            extension_name="httpfs",
            duckdb_arch="linux_amd64",
            actual_sha256="a" * 64,
            allow_unverified=False,
        )


def test_verify_download_checksum_allows_mismatch_with_breakglass(capsys):
    checksums = {"v1.4.4": {"httpfs": {"linux_amd64": "b" * 64}}}
    aef._verify_download_checksum(
        checksums=checksums,
        duckdb_version="v1.4.4",
        extension_name="httpfs",
        duckdb_arch="linux_amd64",
        actual_sha256="a" * 64,
        allow_unverified=True,
    )
    captured = capsys.readouterr()
    assert "WARNING" in captured.out
