# 🦆DuckDB vss extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-vss.svg)](https://pypi.org/project/duckdb-extension-vss)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-vss.svg)](https://pypi.org/project/duckdb-extension-vss)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-vss
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("vss")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='vss' or 
                list_contains(aliases, 'vss')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-vss` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
