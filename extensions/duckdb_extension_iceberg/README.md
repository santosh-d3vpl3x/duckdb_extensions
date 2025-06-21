# 🦆DuckDB iceberg extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-iceberg.svg)](https://pypi.org/project/duckdb-extension-iceberg)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-iceberg.svg)](https://pypi.org/project/duckdb-extension-iceberg)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-iceberg
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("iceberg")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='iceberg' or 
                list_contains(aliases, 'iceberg')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-iceberg` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
