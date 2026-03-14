# 🦆DuckDB odbc extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-odbc.svg)](https://pypi.org/project/duckdb-extension-odbc)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-odbc.svg)](https://pypi.org/project/duckdb-extension-odbc)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-odbc
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("odbc")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='odbc_scanner' or 
                list_contains(aliases, 'odbc')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-odbc` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
