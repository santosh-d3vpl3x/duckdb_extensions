# 🦆DuckDB aws extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-aws.svg)](https://pypi.org/project/duckdb-extension-aws)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-aws.svg)](https://pypi.org/project/duckdb-extension-aws)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-aws
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("aws")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='aws' or 
                list_contains(aliases, 'aws')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-aws` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
