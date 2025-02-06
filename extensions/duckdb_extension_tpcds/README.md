# 🦆DuckDB tpcds extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-tpcds.svg)](https://pypi.org/project/duckdb-extension-tpcds)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-tpcds.svg)](https://pypi.org/project/duckdb-extension-tpcds)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-tpcds
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("tpcds")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='tpcds' or 
                list_contains(aliases, 'tpcds')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-tpcds` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
