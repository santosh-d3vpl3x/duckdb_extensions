# 🦆DuckDB HTTPFS extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-delta.svg)](https://pypi.org/project/duckdb-extension-delta)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-delta.svg)](https://pypi.org/project/duckdb-extension-delta)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
First install `duckdb-extensions`.
```console
pip install duckdb-extensions duckdb-extension-delta
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("delta")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='delta'""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-delta` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.