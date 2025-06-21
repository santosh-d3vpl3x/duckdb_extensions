import os

import duckdb

from duckdb_extensions import import_extension


def test_extensions():
    extension = os.environ.get("EXTENSION_NAME")
    import_extension(extension)

    assert (
        duckdb.sql(f"""SELECT count(*)
                FROM duckdb_extensions() where
                (extension_name = '{extension}' or  list_contains(aliases, '{extension}'))
                AND installed=true""").fetchone()[0]
        == 1
    )
