# 🦆DuckDB encodings extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-encodings.svg)](https://pypi.org/project/duckdb-extension-encodings)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-encodings.svg)](https://pypi.org/project/duckdb-extension-encodings)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-encodings
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("encodings")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='encodings' or 
                list_contains(aliases, 'encodings')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-encodings` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
