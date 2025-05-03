# pip installable DuckDB extensions
pip installable duckdb core extensions so you don't have to leave your python ecosystem behind.

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extensions.svg)](https://pypi.org/project/duckdb-extensions)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extensions.svg)](https://pypi.org/project/duckdb-extensions)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Available extensions
- [duckdb_extension_arrow](extensions/duckdb_extension_arrow)
- [duckdb_extension_autocomplete](extensions/duckdb_extension_autocomplete)
- [duckdb_extension_aws](extensions/duckdb_extension_aws)
- [duckdb_extension_azure](extensions/duckdb_extension_azure)
- [duckdb_extension_delta](extensions/duckdb_extension_delta)
- [duckdb_extension_excel](extensions/duckdb_extension_excel)
- [duckdb_extension_fts](extensions/duckdb_extension_fts)
- [duckdb_extension_httpfs](extensions/duckdb_extension_httpfs)
- [duckdb_extension_iceberg](extensions/duckdb_extension_iceberg)
- [duckdb_extension_inet](extensions/duckdb_extension_inet)
- [duckdb_extension_json](extensions/duckdb_extension_json)
- [duckdb_extension_motherduck](extensions/duckdb_extension_motherduck)
- [duckdb_extension_mysql](extensions/duckdb_extension_mysql)
- [duckdb_extension_mysql_scanner](extensions/duckdb_extension_mysql_scanner)
- [duckdb_extension_parquet](extensions/duckdb_extension_parquet)
- [duckdb_extension_postgres](extensions/duckdb_extension_postgres)
- [duckdb_extension_postgres_scanner](extensions/duckdb_extension_postgres_scanner)
- [duckdb_extension_spatial](extensions/duckdb_extension_spatial)
- [duckdb_extension_sqlite](extensions/duckdb_extension_sqlite)
- [duckdb_extension_sqlite3](extensions/duckdb_extension_sqlite3)
- [duckdb_extension_sqlite_scanner](extensions/duckdb_extension_sqlite_scanner)
- [duckdb_extension_tpcds](extensions/duckdb_extension_tpcds)
- [duckdb_extension_tpch](extensions/duckdb_extension_tpch)
- [duckdb_extension_vss](extensions/duckdb_extension_vss)

**The architectures supported:**
- `linux_amd64_gcc4`
- `linux_arm64`
- `osx_arm64`
- `osx_amd64`
- `windows_amd64`

Compatible with `duckdb==1.2.1`

## Installation
First install `duckdb-extensions`.
```console
pip install duckdb-extensions
```
Then one of the extensions.
```console
pip install duckdb-extension-httpfs
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("httpfs")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='httpfs'""")
    .fetchone()[0]
)
```

## License

`duckdb-extensions` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
