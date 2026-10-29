# 🦆DuckDB legacy_parser extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-legacy_parser.svg)](https://pypi.org/project/duckdb-extension-legacy_parser)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-legacy_parser.svg)](https://pypi.org/project/duckdb-extension-legacy_parser)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-legacy-parser
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("legacy_parser")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='legacy_parser' or 
                list_contains(aliases, 'legacy_parser')""")
    .fetchall()[0][0]
)
```

## License

`duckdb-extension-legacy-parser` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
