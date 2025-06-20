import importlib
import pathlib
from typing import Optional

import duckdb
from duckdb import DuckDBPyConnection

try:
    # Python < 3.9
    import importlib_resources as ilr
except ImportError:
    import importlib.resources as ilr


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

    extension_dir = module_path / "extensions" / duckdb_version
    extension_file = extension_dir / f"{name}.duckdb_extension"

    con.sql(f"{'FORCE ' if force_install else ''} INSTALL '{extension_file}'")
