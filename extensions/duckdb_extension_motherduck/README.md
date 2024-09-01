# 🦆DuckDB motherduck extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-motherduck.svg)](https://pypi.org/project/duckdb-extension-motherduck)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-motherduck.svg)](https://pypi.org/project/duckdb-extension-motherduck)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-motherduck
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("motherduck")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='motherduck' or 
                list_contains(aliases, 'motherduck')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-motherduck` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
