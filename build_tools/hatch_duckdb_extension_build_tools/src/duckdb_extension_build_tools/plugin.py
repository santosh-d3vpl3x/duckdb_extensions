import gzip
import hashlib
import json
import os
import pathlib
import re
import shutil
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

CHECKSUMS_MANIFEST_SCHEMA_VERSION = 1
CHECKSUMS_MANIFEST_FILENAME = "extension_checksums.json"
EXTENSION_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")
DUCKDB_PIN_PATTERN = re.compile(r"^duckdb\s*==\s*(v?[A-Za-z0-9_.+-]+)$", re.IGNORECASE)
SUPPORTED_ARCHITECTURES = frozenset({
    "linux_amd64",
    "linux_arm64",
    "osx_arm64",
    "osx_amd64",
    "windows_amd64",
})
ALLOW_UNVERIFIED_ENV = "DUCKDB_EXTENSIONS_ALLOW_UNVERIFIED"
TRUTHY_VALUES = {"1", "true", "yes", "on"}


def get_checksums_manifest_path(project_root: str | Path) -> Path:
    project_root = Path(project_root).resolve()
    for candidate_root in (project_root, *project_root.parents):
        manifest_path = candidate_root / CHECKSUMS_MANIFEST_FILENAME
        if manifest_path.exists():
            return manifest_path
    return project_root / CHECKSUMS_MANIFEST_FILENAME


def _is_truthy(value: str | None) -> bool:
    return bool(value and value.strip().lower() in TRUTHY_VALUES)


def _allow_unverified_downloads() -> bool:
    allow_unverified = _is_truthy(os.environ.get(ALLOW_UNVERIFIED_ENV))
    if allow_unverified and _is_truthy(os.environ.get("GITHUB_ACTIONS")):
        raise RuntimeError(
            f"{ALLOW_UNVERIFIED_ENV}=1 is blocked in GitHub Actions. "
            "Release builds must use verified checksums."
        )
    return allow_unverified


def _validate_download_inputs(duckdb_arch: str, extension_name: str) -> None:
    if duckdb_arch not in SUPPORTED_ARCHITECTURES:
        raise ValueError(f"Unsupported architecture {duckdb_arch!r}. Expected one of {sorted(SUPPORTED_ARCHITECTURES)}.")
    if not EXTENSION_NAME_PATTERN.fullmatch(extension_name):
        raise ValueError(f"Invalid extension name {extension_name!r}. Expected pattern {EXTENSION_NAME_PATTERN.pattern!r}.")


def _get_declared_duckdb_version(metadata_config: dict[str, Any], fallback_version: str) -> str:
    project = metadata_config.get("project", {})
    dependencies = project.get("dependencies", [])
    if isinstance(dependencies, list):
        for dependency in dependencies:
            if not isinstance(dependency, str):
                continue
            match = DUCKDB_PIN_PATTERN.fullmatch(dependency.strip())
            if match:
                version = match.group(1)
                return version if version.startswith("v") else f"v{version}"
    return fallback_version


def _load_checksums_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(
            f"Checksums manifest not found: {path}. "
            "Generate it with `python scripts/maintainer.py sync-checksums`."
        )
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != CHECKSUMS_MANIFEST_SCHEMA_VERSION:
        raise RuntimeError(
            "Unsupported checksums manifest schema version "
            f"{manifest.get('schema_version')!r}; expected {CHECKSUMS_MANIFEST_SCHEMA_VERSION}."
        )
    checksums = manifest.get("checksums")
    if not isinstance(checksums, dict):
        raise RuntimeError("Checksums manifest is missing `checksums` object.")
    return checksums


def _extract_gzip_to_file_with_sha256(gz_file_path: Path, output_path: Path) -> str:
    digest = hashlib.sha256()
    block_size = 65536
    with gzip.open(gz_file_path, "rb") as source_file, open(output_path, "wb") as destination_file:
        while True:
            chunk = source_file.read(block_size)
            if not chunk:
                break
            destination_file.write(chunk)
            digest.update(chunk)
    return digest.hexdigest()


def _verify_download_checksum(
    checksums: dict[str, Any],
    duckdb_version: str,
    extension_name: str,
    duckdb_arch: str,
    actual_sha256: str,
    allow_unverified: bool,
) -> None:
    version_entry = checksums.get(duckdb_version, {})
    extension_entry = version_entry.get(extension_name, {})
    expected_sha256 = extension_entry.get(duckdb_arch)

    sync_hint = "Run `python scripts/maintainer.py sync-checksums --verify` to diagnose."

    if not expected_sha256:
        message = (
            "Missing checksum entry for "
            f"{duckdb_version}/{extension_name}/{duckdb_arch} in {CHECKSUMS_MANIFEST_FILENAME}. "
            f"{sync_hint}"
        )
        if allow_unverified:
            print(f"WARNING: {message} Proceeding because {ALLOW_UNVERIFIED_ENV}=1.")
            return
        raise RuntimeError(message)

    if actual_sha256 != expected_sha256:
        message = (
            "Checksum mismatch for "
            f"{duckdb_version}/{extension_name}/{duckdb_arch}: expected {expected_sha256}, got {actual_sha256}. "
            f"{sync_hint}"
        )
        if allow_unverified:
            print(f"WARNING: {message} Proceeding because {ALLOW_UNVERIFIED_ENV}=1.")
            return
        raise RuntimeError(message)


class DuckDBExtensionBuildHook(BuildHookInterface):
    PLUGIN_NAME = "duckdb_extension"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        import duckdb

        installed_duckdb_version = duckdb.sql("PRAGMA version;").fetchone()[0]
        duckdb_version = _get_declared_duckdb_version(self.metadata.config, installed_duckdb_version)
        if version == "standard" and self.target_name == "wheel":
            duckdb_arch = pathlib.Path(self.directory).name
        else:
            duckdb_arch = duckdb.sql("PRAGMA platform;").fetchone()[0]

        root_name = self.metadata.name.replace("-", "_")
        download_dir = Path(self.root) / "src" / root_name / "extensions"

        self.download_extensions(duckdb_arch, duckdb_version, download_dir)
        self.add_tag(build_data, duckdb_arch)
        self.include_files(build_data, duckdb_arch, duckdb_version, download_dir)

    def include_files(self, build_data: dict[str, Any], duckdb_arch: str, duckdb_version: str, download_dir: Path) -> None:
        file_path = download_dir / duckdb_version / duckdb_arch
        alias = self.metadata.name.replace("-", "_").replace("duckdb_extension_", "")
        for file in file_path.glob(f"{alias}.duckdb_extension"):
            root_name = self.metadata.name.replace("-", "_")
            build_data["force_include"][file] = f"{root_name}/extensions/{duckdb_version}/{file.name}"

    @staticmethod
    def add_tag(build_data: dict[str, Any], duckdb_arch: str) -> None:
        if duckdb_arch == "linux_amd64":
            build_data["tag"] = "py3-none-manylinux2014_x86_64"
        elif duckdb_arch == "linux_arm64":
            build_data["tag"] = "py3-none-manylinux2014_aarch64"
        elif duckdb_arch == "osx_arm64":
            build_data["tag"] = "py3-none-macosx_11_0_arm64"
        elif duckdb_arch == "osx_amd64":
            build_data["tag"] = "py3-none-macosx_11_0_x86_64"
        elif duckdb_arch == "windows_amd64":
            build_data["tag"] = "py3-none-win_amd64"
        else:
            raise Exception("Not supported platform")

    def download_extensions(self, duckdb_arch: str, duckdb_version: str, download_dir: Path) -> None:
        import requests

        extension_name = self.metadata.config["tool"]["extension_builder"]["extension_name"]
        _validate_download_inputs(duckdb_arch, extension_name)
        allow_unverified = _allow_unverified_downloads()
        checksums = _load_checksums_manifest(get_checksums_manifest_path(self.root))

        download_dir.mkdir(parents=True, exist_ok=True)
        base_url = f"https://extensions.duckdb.org/{duckdb_version}"
        alias = self.metadata.name.replace("-", "_").replace("duckdb_extension_", "")
        url = f"{base_url}/{duckdb_arch}/{extension_name}.duckdb_extension.gz"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        arch_dir = download_dir / duckdb_version / duckdb_arch
        arch_dir.mkdir(parents=True, exist_ok=True)
        gz_file_path = arch_dir / f"{alias}.duckdb_extension.gz"
        extension_file_path = arch_dir / f"{alias}.duckdb_extension"

        with open(gz_file_path, "wb") as gz_file:
            gz_file.write(response.content)

        actual_sha256 = _extract_gzip_to_file_with_sha256(gz_file_path, extension_file_path)
        _verify_download_checksum(
            checksums=checksums,
            duckdb_version=duckdb_version,
            extension_name=extension_name,
            duckdb_arch=duckdb_arch,
            actual_sha256=actual_sha256,
            allow_unverified=allow_unverified,
        )
        os.remove(gz_file_path)
        print(f"Downloaded {alias} to {extension_file_path} (sha256={actual_sha256})")
