# 🦆DuckDB icu extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-icu.svg)](https://pypi.org/project/duckdb-extension-icu)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-icu.svg)](https://pypi.org/project/duckdb-extension-icu)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-icu
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("icu")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='icu' or 
                list_contains(aliases, 'icu')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-icu` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
