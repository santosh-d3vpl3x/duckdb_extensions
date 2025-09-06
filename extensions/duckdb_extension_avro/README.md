# 🦆DuckDB avro extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-avro.svg)](https://pypi.org/project/duckdb-extension-avro)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-avro.svg)](https://pypi.org/project/duckdb-extension-avro)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-avro
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("avro")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='avro' or 
                list_contains(aliases, 'avro')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-avro` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
