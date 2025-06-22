# 🦆DuckDB sqlite extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-sqlite.svg)](https://pypi.org/project/duckdb-extension-sqlite)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-sqlite.svg)](https://pypi.org/project/duckdb-extension-sqlite)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-sqlite
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("sqlite")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='sqlite' or 
                list_contains(aliases, 'sqlite')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-sqlite` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
