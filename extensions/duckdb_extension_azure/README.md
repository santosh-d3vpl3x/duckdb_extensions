# 🦆DuckDB azure extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-azure.svg)](https://pypi.org/project/duckdb-extension-azure)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-azure.svg)](https://pypi.org/project/duckdb-extension-azure)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-azure
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("azure")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='azure' or 
                list_contains(aliases, 'azure')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-azure` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
