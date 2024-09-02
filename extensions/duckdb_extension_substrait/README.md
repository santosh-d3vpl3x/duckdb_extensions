# 🦆DuckDB substrait extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-substrait.svg)](https://pypi.org/project/duckdb-extension-substrait)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-substrait.svg)](https://pypi.org/project/duckdb-extension-substrait)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-substrait
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("substrait")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='substrait' or 
                list_contains(aliases, 'substrait')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-substrait` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.