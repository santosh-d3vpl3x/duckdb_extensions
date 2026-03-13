import importlib
import gzip
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_TOOLS_SRC = REPO_ROOT / "build_tools" / "hatch_duckdb_extension_build_tools" / "src"
if str(BUILD_TOOLS_SRC) not in sys.path:
    sys.path.insert(0, str(BUILD_TOOLS_SRC))

from duckdb_extension_build_tools import plugin as aef


# --- Tests for _is_truthy ---


def test_is_truthy_with_one():
    assert aef._is_truthy("1") is True


def test_is_truthy_with_true_mixed_case():
    assert aef._is_truthy("True") is True
    assert aef._is_truthy("TRUE") is True
    assert aef._is_truthy("true") is True


def test_is_truthy_with_yes():
    assert aef._is_truthy("yes") is True
    assert aef._is_truthy("YES") is True


def test_is_truthy_with_on():
    assert aef._is_truthy("on") is True
    assert aef._is_truthy("ON") is True


def test_is_truthy_with_whitespace():
    assert aef._is_truthy("  1  ") is True
    assert aef._is_truthy("  true  ") is True


def test_is_truthy_returns_false_for_other_values():
    assert aef._is_truthy("0") is False
    assert aef._is_truthy("false") is False
    assert aef._is_truthy("no") is False
    assert aef._is_truthy("off") is False
    assert aef._is_truthy("random") is False


def test_is_truthy_returns_false_for_none():
    assert aef._is_truthy(None) is False


def test_is_truthy_returns_false_for_empty_string():
    assert aef._is_truthy("") is False
    assert aef._is_truthy("   ") is False


# --- Tests for _load_checksums_manifest ---


def test_load_checksums_manifest_raises_when_file_missing(tmp_path):
    missing_path = tmp_path / "nonexistent.json"
    with pytest.raises(RuntimeError, match="Checksums manifest not found"):
        aef._load_checksums_manifest(missing_path)


def test_load_checksums_manifest_raises_on_invalid_schema_version(tmp_path):
    manifest_path = tmp_path / "checksums.json"
    manifest_path.write_text(json.dumps({"schema_version": 999, "checksums": {}}))
    with pytest.raises(RuntimeError, match="Unsupported checksums manifest schema version"):
        aef._load_checksums_manifest(manifest_path)


def test_load_checksums_manifest_raises_when_checksums_missing(tmp_path):
    manifest_path = tmp_path / "checksums.json"
    manifest_path.write_text(json.dumps({"schema_version": 1}))
    with pytest.raises(RuntimeError, match="missing `checksums` object"):
        aef._load_checksums_manifest(manifest_path)


def test_load_checksums_manifest_raises_when_checksums_not_dict(tmp_path):
    manifest_path = tmp_path / "checksums.json"
    manifest_path.write_text(json.dumps({"schema_version": 1, "checksums": "invalid"}))
    with pytest.raises(RuntimeError, match="missing `checksums` object"):
        aef._load_checksums_manifest(manifest_path)


def test_load_checksums_manifest_returns_checksums_on_valid_file(tmp_path):
    manifest_path = tmp_path / "checksums.json"
    expected_checksums = {"v1.0.0": {"ext": {"linux_amd64": "abc123"}}}
    manifest_path.write_text(json.dumps({"schema_version": 1, "checksums": expected_checksums}))
    result = aef._load_checksums_manifest(manifest_path)
    assert result == expected_checksums


def test_get_checksums_manifest_path_searches_parent_directories(tmp_path):
    repo_root = tmp_path / "repo"
    extension_root = repo_root / "extensions" / "duckdb_extension_httpfs"
    extension_root.mkdir(parents=True)
    manifest_path = repo_root / "extension_checksums.json"
    manifest_path.write_text(json.dumps({"schema_version": 1, "checksums": {}}))

    result = aef.get_checksums_manifest_path(extension_root)

    assert result == manifest_path


# --- Tests for _extract_gzip_to_file_with_sha256 ---


def test_extract_gzip_to_file_with_sha256_extracts_and_hashes(tmp_path):
    # Create test content and compress it
    test_content = b"Hello, DuckDB extension world!"
    gz_path = tmp_path / "test.gz"
    output_path = tmp_path / "test.out"

    with gzip.open(gz_path, "wb") as f:
        f.write(test_content)

    # Extract and get hash
    result_hash = aef._extract_gzip_to_file_with_sha256(gz_path, output_path)

    # Verify extraction
    assert output_path.read_bytes() == test_content

    # Verify hash
    import hashlib
    expected_hash = hashlib.sha256(test_content).hexdigest()
    assert result_hash == expected_hash


def test_extract_gzip_to_file_with_sha256_handles_large_content(tmp_path):
    # Test with content larger than the block size (65536)
    test_content = b"x" * 100000
    gz_path = tmp_path / "large.gz"
    output_path = tmp_path / "large.out"

    with gzip.open(gz_path, "wb") as f:
        f.write(test_content)

    result_hash = aef._extract_gzip_to_file_with_sha256(gz_path, output_path)

    assert output_path.read_bytes() == test_content
    import hashlib
    assert result_hash == hashlib.sha256(test_content).hexdigest()


# --- Tests for _validate_download_inputs ---


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


def test_verify_download_checksum_includes_sync_hint_on_missing():
    checksums = {"v1.4.4": {"httpfs": {}}}
    with pytest.raises(RuntimeError, match="sync-checksums"):
        aef._verify_download_checksum(
            checksums=checksums,
            duckdb_version="v1.4.4",
            extension_name="httpfs",
            duckdb_arch="linux_amd64",
            actual_sha256="a" * 64,
            allow_unverified=False,
        )


def test_verify_download_checksum_includes_sync_hint_on_mismatch():
    checksums = {"v1.4.4": {"httpfs": {"linux_amd64": "b" * 64}}}
    with pytest.raises(RuntimeError, match="sync-checksums"):
        aef._verify_download_checksum(
            checksums=checksums,
            duckdb_version="v1.4.4",
            extension_name="httpfs",
            duckdb_arch="linux_amd64",
            actual_sha256="a" * 64,
            allow_unverified=False,
        )


def test_build_hook_package_imports_without_repo_root_on_sys_path(monkeypatch):
    filtered_sys_path = [
        entry for entry in sys.path
        if Path(entry or ".").resolve() not in {REPO_ROOT, BUILD_TOOLS_SRC}
    ]
    monkeypatch.setattr(sys, "path", [str(BUILD_TOOLS_SRC), *filtered_sys_path])
    monkeypatch.delitem(sys.modules, "duckdb_extension_build_tools", raising=False)
    monkeypatch.delitem(sys.modules, "duckdb_extension_build_tools.plugin", raising=False)

    module = importlib.import_module("duckdb_extension_build_tools.plugin")

    assert module.DuckDBExtensionBuildHook.PLUGIN_NAME == "duckdb_extension"
    assert module.get_checksums_manifest_path("/tmp/project") == Path("/tmp/project").resolve() / "extension_checksums.json"
