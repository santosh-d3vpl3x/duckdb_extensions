import importlib
import logging
import pathlib
from typing import Optional
from packaging import version

import duckdb
from duckdb import DuckDBPyConnection

try:
    # Python < 3.9
    import importlib_resources as ilr
except ImportError:
    import importlib.resources as ilr


def _get_compatible_version_dir(module_path: pathlib.Path, duckdb_version: str) -> pathlib.Path:
    """Find the latest compatible extension version directory."""
    extensions_dir = module_path / "extensions"
    
    if not extensions_dir.exists():
        return extensions_dir / duckdb_version
    
    compatible_versions = []
    for version_dir in extensions_dir.iterdir():
        if version_dir.is_dir():
            dir_version = version_dir.name
            parts = dir_version.split('.')
            if len(parts) == 4 and dir_version.startswith(duckdb_version):
                try:
                    version.parse(dir_version)
                    compatible_versions.append(dir_version)
                except version.InvalidVersion as e:
                    logging.warning(f"Skipping invalid version directory '{dir_version}': {e}")
    
    if compatible_versions:
        latest = max(compatible_versions, key=lambda v: version.parse(v))
        return extensions_dir / latest
    
    return extensions_dir / duckdb_version


def import_extension(name: str, force_install: bool = False, con: Optional[DuckDBPyConnection] = None):
    """Import local extension `name` into DuckDB connection `con`.
    If `con` is None, import into the default connection.
    """
    if con is None:
        con = duckdb.default_connection()

    quack_module = importlib.import_module(f"duckdb_extension_{name}")
    module_path = pathlib.Path(str(ilr.files(quack_module)))

    version_row = con.sql("PRAGMA version;").fetchone()
    if version_row is None:
        raise RuntimeError("Failed to retrieve DuckDB version information from the connection.")
    duckdb_version = version_row[0]

    extension_dir = _get_compatible_version_dir(module_path, duckdb_version)
    extension_file = extension_dir / f"{name}.duckdb_extension"

    con.sql(f"{'FORCE ' if force_install else ''} INSTALL '{extension_file}'")
