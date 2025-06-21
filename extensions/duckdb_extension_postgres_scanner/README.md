# 🦆DuckDB postgres_scanner extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-postgres_scanner.svg)](https://pypi.org/project/duckdb-extension-postgres_scanner)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-postgres_scanner.svg)](https://pypi.org/project/duckdb-extension-postgres_scanner)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-postgres_scanner
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("postgres_scanner")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='postgres_scanner'""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-postgres_scanner` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
