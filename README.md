# duckdb_extensions

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extensions-parquet.svg)](https://pypi.org/project/duckdb-extensions-parquet)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extensions-parquet.svg)](https://pypi.org/project/duckdb-extensions-parquet)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Available extensions
- duckdb-extension-httpfs
- duckdb-extension-spatial
- duckdb-extension-parquet

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
