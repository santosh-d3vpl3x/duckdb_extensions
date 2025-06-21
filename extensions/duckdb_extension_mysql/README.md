# 🦆DuckDB mysql extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-mysql.svg)](https://pypi.org/project/duckdb-extension-mysql)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-mysql.svg)](https://pypi.org/project/duckdb-extension-mysql)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-mysql
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("mysql")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='mysql' or 
                list_contains(aliases, 'mysql')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-mysql` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
