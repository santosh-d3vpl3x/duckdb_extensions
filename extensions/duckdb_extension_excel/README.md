# 🦆DuckDB excel extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-excel.svg)](https://pypi.org/project/duckdb-extension-excel)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-excel.svg)](https://pypi.org/project/duckdb-extension-excel)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-excel
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("excel")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='excel' or 
                list_contains(aliases, 'excel')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-excel` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
