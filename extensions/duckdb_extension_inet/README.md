# 🦆DuckDB inet extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-inet.svg)](https://pypi.org/project/duckdb-extension-inet)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-inet.svg)](https://pypi.org/project/duckdb-extension-inet)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-inet
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("inet")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='inet' or 
                list_contains(aliases, 'inet')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-inet` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
