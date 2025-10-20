# 🦆DuckDB ducklake extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-ducklake.svg)](https://pypi.org/project/duckdb-extension-ducklake)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-ducklake.svg)](https://pypi.org/project/duckdb-extension-ducklake)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-ducklake
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("ducklake")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='ducklake' or 
                list_contains(aliases, 'ducklake')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-ducklake` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
