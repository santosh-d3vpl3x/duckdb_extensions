# 🦆DuckDB vortex extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-vortex.svg)](https://pypi.org/project/duckdb-extension-vortex)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-vortex.svg)](https://pypi.org/project/duckdb-extension-vortex)

-----

> **Note:** This extension is only available on **Linux** and **macOS**. Windows is not supported.

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-vortex
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("vortex")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='vortex' or 
                list_contains(aliases, 'vortex')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-vortex` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
