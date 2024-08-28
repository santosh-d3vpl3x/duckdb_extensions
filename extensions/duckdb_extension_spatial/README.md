# 🦆DuckDB spatial extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extensions-spatial.svg)](https://pypi.org/project/duckdb-extensions-spatial)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extensions-spatial.svg)](https://pypi.org/project/duckdb-extensions-spatial)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
First install `duckdb-extensions`.
```console
pip install duckdb-extensions duckdb-extension-spatial
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("spatial")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='spatial'""")
    .fetchone()[0]
)
```

## License

`duckdb-extensions-spatial` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
