# 🦆DuckDB sqlite_scanner extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-sqlite_scanner.svg)](https://pypi.org/project/duckdb-extension-sqlite_scanner)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-sqlite_scanner.svg)](https://pypi.org/project/duckdb-extension-sqlite_scanner)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-sqlite-scanner
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("sqlite_scanner")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='sqlite_scanner' or 
                list_contains(aliases, 'sqlite_scanner')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-sqlite-scanner` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
