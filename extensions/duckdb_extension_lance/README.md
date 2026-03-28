# 🦆DuckDB lance extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-lance.svg)](https://pypi.org/project/duckdb-extension-lance)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-lance.svg)](https://pypi.org/project/duckdb-extension-lance)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-lance
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("lance")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='lance' or 
                list_contains(aliases, 'lance')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-lance` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
Bundled Lance extension binaries are upstream artifacts and follow the `lance-duckdb` [Apache-2.0 license](https://github.com/lance-format/lance-duckdb/blob/main/LICENSE).
