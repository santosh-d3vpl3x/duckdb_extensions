import gzip
import os
import pathlib
import shutil
from typing import Any
import duckdb
import requests
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]):
        duckdb_version = duckdb.sql("PRAGMA version;").fetchone()[0]
        if version == "standard" and self.target_name == "wheel":
            duckdb_arch = pathlib.Path(self.directory).name
        else:
            duckdb_arch = duckdb.sql("PRAGMA platform;").fetchone()[0]

        root_name = self.metadata.name.replace("-", "_")
        download_dir = Path("src") / root_name / "extensions"

        self.download_extensions(duckdb_arch, duckdb_version, download_dir)
        CustomBuildHook.add_tag(build_data, duckdb_arch)
        CustomBuildHook.include_files(self, build_data, duckdb_arch, duckdb_version, download_dir)

    def include_files(self, build_data, duckdb_arch, duckdb_version, download_dir):
        file_path = download_dir / duckdb_version / duckdb_arch
        alias = self.metadata.name.replace("-", "_").replace("duckdb_extension_", "")
        for file in file_path.glob(f"{alias}.duckdb_extension"):
            root_name = self.metadata.name.replace("-", "_")
            build_data["force_include"][file] = f"{root_name}/extensions/{duckdb_version}/{file.name}"

    @staticmethod
    def add_tag(build_data, duckdb_arch):
        if duckdb_arch == "linux_amd64_gcc4":
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

    def download_extensions(self, duckdb_arch, duckdb_version, download_dir):
        """Downloads the extension from the DuckDB repo."""
        download_dir.mkdir(parents=True, exist_ok=True)  # Ensure the download directory exists
        base_url = f"https://extensions.duckdb.org/{duckdb_version}"
        extension_name = self.metadata.config["tool"]["extension_builder"]["extension_name"]
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
        block_size = 65536
        with gzip.open(gz_file_path, "rb") as s_file, open(extension_file_path, "wb") as d_file:
            shutil.copyfileobj(s_file, d_file, block_size)
        os.remove(gz_file_path)
        print(f"Downloaded {alias} to {extension_file_path}")
