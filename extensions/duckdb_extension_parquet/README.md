# 🦆DuckDB parquet extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-parquet.svg)](https://pypi.org/project/duckdb-extension-parquet)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-parquet.svg)](https://pypi.org/project/duckdb-extension-parquet)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
First install `duckdb-extensions`.
```console
pip install duckdb-extensions duckdb-extension-parquet
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("parquet")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='parquet'""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-parquet` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
