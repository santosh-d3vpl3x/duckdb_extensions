import os

import duckdb

from duckdb_extensions import extension_importer


def test_extensions():
    extension = os.environ.get("EXTENSION_NAME")
    extension_importer.import_extension(extension)

    assert (
        duckdb.sql(f"""SELECT count(*)
                FROM duckdb_extensions() where extension_name = '{extension}' 
                AND installed=true""").fetchone()[0]
        == 1
    )
