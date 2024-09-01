# 🦆DuckDB HTTPFS extension as python package

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extension-{@cookiecutter.extension_name@}.svg)](https://pypi.org/project/duckdb-extension-{@cookiecutter.extension_name@})
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extension-{@cookiecutter.extension_name@}.svg)](https://pypi.org/project/duckdb-extension-{@cookiecutter.extension_name@})

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)


## Installation
First install `duckdb-extensions`.
```console
pip install duckdb-extensions duckdb-extension-{@cookiecutter.extension_name@}
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("{@cookiecutter.extension_name@}")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='{@cookiecutter.extension_name@}'""")
    .fetchone()[0]
)
```

## License

`duckdb-extension-{@cookiecutter.extension_name@}` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
