import pathlib
from pprint import pprint
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
        for file in file_path.glob("*.duckdb_extension.gz"):
            root_name = self.metadata.name.replace("-", "_")
            build_data["force_include"][file] = f"{root_name}/extensions/{duckdb_version}/{duckdb_arch}/{file.name}"

    @staticmethod
    def add_tag(build_data, duckdb_arch):
        if duckdb_arch == "linux_amd64":
            build_data["tag"] = "py3-none-manylinux2014_x86_64"
        elif duckdb_arch == "osx_arm64":
            build_data["tag"] = "py3-none-macosx_11_0_arm64"
        else:
            raise Exception("Not supported platform")

    def download_extensions(self, duckdb_arch, duckdb_version, download_dir):
        """Downloads the extension from the DuckDB repo."""
        download_dir.mkdir(parents=True, exist_ok=True)  # Ensure the download directory exists
        base_url = f"https://extensions.duckdb.org/{duckdb_version}"
        extension_name = self.metadata.config["tool"]["extension_builder"]["extension_name"]
        url = f"{base_url}/{duckdb_arch}/{extension_name}.duckdb_extension.gz"
        response = requests.get(url)
        if response.status_code == 200:
            arch_dir = download_dir / duckdb_version / duckdb_arch
            arch_dir.mkdir(parents=True, exist_ok=True)
            file_path = arch_dir / (extension_name + ".duckdb_extension.gz")
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Downloaded {extension_name}.duckdb_extension to {file_path}")
        else:
            print(f"Failed to download {extension_name} from {url}. Status code: {response.status_code}")