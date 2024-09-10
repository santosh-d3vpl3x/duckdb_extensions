import gzip
import importlib
import pathlib
import shutil

import duckdb

try:
    # Python < 3.9
    import importlib_resources as ilr
except ImportError:
    import importlib.resources as ilr


def import_extension(name: str):
    quack_module = importlib.import_module(f"duckdb_extension_{name}")
    module_path = pathlib.Path(str(ilr.files(quack_module)))

    duckdb_version = duckdb.sql("PRAGMA version;").fetchone()[0]

    extension_dir = module_path / "extensions" / duckdb_version
    extension_file = extension_dir / f"{name}.duckdb_extension"

    duckdb.sql(f"INSTALL '{extension_file}'")
