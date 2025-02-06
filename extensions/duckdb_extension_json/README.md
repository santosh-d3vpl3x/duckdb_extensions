# 🦆DuckDB json extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-json.svg)](https://pypi.org/project/duckdb-extension-json)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-json.svg)](https://pypi.org/project/duckdb-extension-json)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-json
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("json")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='json' or 
                list_contains(aliases, 'json')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-json` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
