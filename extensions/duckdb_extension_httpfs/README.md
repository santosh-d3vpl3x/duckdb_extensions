# 🦆DuckDB HTTPFS extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-httpfs.svg)](https://pypi.org/project/duckdb-extension-httpfs)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-httpfs.svg)](https://pypi.org/project/duckdb-extension-httpfs)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-httpfs
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("httpfs")
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

`duckdb-extension-httpfs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
