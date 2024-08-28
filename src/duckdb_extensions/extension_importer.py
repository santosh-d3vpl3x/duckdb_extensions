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
    duckdb_arch = duckdb.sql("PRAGMA platform;").fetchone()[0]
    extension_dir = module_path / "extensions" / duckdb_version / duckdb_arch
    extension_file_gz = extension_dir / f"{name}.duckdb_extension.gz"
    extension_file = extension_dir / f"{name}.duckdb_extension"

    block_size = 65536
    with gzip.open(extension_file_gz, "rb") as s_file, open(extension_file, "wb") as d_file:
        shutil.copyfileobj(s_file, d_file, block_size)

    duckdb.sql(f"INSTALL '{extension_file}'")
