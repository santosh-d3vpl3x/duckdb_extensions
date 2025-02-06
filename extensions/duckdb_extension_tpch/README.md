# 🦆DuckDB tpch extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-tpch.svg)](https://pypi.org/project/duckdb-extension-tpch)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-tpch.svg)](https://pypi.org/project/duckdb-extension-tpch)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-tpch
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("tpch")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='tpch' or 
                list_contains(aliases, 'tpch')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-tpch` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
