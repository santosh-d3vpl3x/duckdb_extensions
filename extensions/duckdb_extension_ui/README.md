# 🦆DuckDB ui extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-ui.svg)](https://pypi.org/project/duckdb-extension-ui)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-ui.svg)](https://pypi.org/project/duckdb-extension-ui)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-ui
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("ui")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='ui' or 
                list_contains(aliases, 'ui')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-ui` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
