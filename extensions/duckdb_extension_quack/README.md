# 🦆DuckDB quack extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-quack.svg)](https://pypi.org/project/duckdb-extension-quack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-quack.svg)](https://pypi.org/project/duckdb-extension-quack)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-quack
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("quack")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='quack' or 
                list_contains(aliases, 'quack')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-quack` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
