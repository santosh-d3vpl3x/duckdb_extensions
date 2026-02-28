# 🦆DuckDB unity_catalog extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-unity_catalog.svg)](https://pypi.org/project/duckdb-extension-unity_catalog)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-unity_catalog.svg)](https://pypi.org/project/duckdb-extension-unity_catalog)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
```console
pip install duckdb-extensions duckdb-extension-unity-catalog
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import import_extension
import_extension("unity_catalog")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where 
                extension_name='unity_catalog' or 
                list_contains(aliases, 'unity_catalog')""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-{@cookiecutter.extension_name | replace("_","-") @}` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
