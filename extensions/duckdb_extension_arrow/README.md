# 🦆DuckDB arrow extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-arrow.svg)](https://pypi.org/project/duckdb-extension-arrow)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-arrow.svg)](https://pypi.org/project/duckdb-extension-arrow)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-arrow
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("arrow")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='arrow' or 
                list_contains(aliases, 'arrow')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-arrow` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
