# DuckDB extensions on pypi

[![PyPI - Version](https://img.shields.io/pypi/v/duckdb-extensions.svg)](https://pypi.org/project/duckdb-extensions)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/duckdb-extensions.svg)](https://pypi.org/project/duckdb-extensions)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Available extensions
- `duckdb-extension-httpfs`
- `duckdb-extension-spatial`
- `duckdb-extension-parquet`
- `duckdb-extension-delta`
- `duckdb-extension-postgres` or `duckdb-extension-postgres-scanner`

**The architectures supported:**
- `linux_amd64_gcc4`
- `osx_arm64`
- `osx_amd64`
- `windows_amd64`

Compatible with `duckdb==1.0.0`

## Installation
First install `duckdb-extensions`.
```console
pip install duckdb-extensions
```
Then one of the extensions.
```console
pip install duckdb-extension-httpfs
```
You are ready to install the extension for duckdb.
```python
from duckdb_extensions import extension_importer
extension_importer.import_extension("httpfs")
```

Verify that the extension is installed.
```python
import duckdb

print(
    duckdb.sql("""SELECT installed
                FROM duckdb_extensions() where extension_name='httpfs'""")
    .fetchone()[0]
)
```

## License

`duckdb-extensions` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
