# User Guide

## Overview
This repository publishes the official DuckDB extensions as Python wheels so they can be installed directly from PyPI. The top-level package `duckdb-extensions` exposes a helper, `duckdb_extensions.import_extension`, that downloads the right binary for your DuckDB build and loads it into the current connection. Individual extension wheels (`duckdb-extension-httpfs`, `duckdb-extension-postgres`, …) bundle the compiled `.duckdb_extension` artifacts that DuckDB normally serves via `INSTALL`.

## Prerequisites
- Python 3.9 or newer
- `pip`, `uv`, or another PEP 517 compatible installer

The published wheels already include the compiled DuckDB extension files, so no extra network access is required beyond downloading the packages themselves.

## Installation
Install the core helper package once:

```bash
pip install duckdb-extensions
# or
uv pip install duckdb-extensions
```

Then install the specific extension wheel(s) you want. Every published package lives under the `duckdb-extension-<name>` namespace:

```bash
pip install duckdb-extension-httpfs
pip install duckdb-extension-spatial
```

Available wheels are listed in `README.md` and correspond to the directories under `extensions/`.

## Loading Extensions at Runtime
Import the helper and request the extension by its DuckDB alias. By default the helper operates on DuckDB’s default connection, but you can pass your own connection or force a reinstall if needed.

```python
from duckdb_extensions import import_extension
import_extension("httpfs")

# Use a custom connection
import duckdb
con = duckdb.connect(database=":memory:")
import_extension("httpfs", con=con)
```

`import_extension` determines the running DuckDB version via `PRAGMA version` and loads the matching prebuilt binary from the installed wheel. To reinstall a previously downloaded extension (for example after upgrading DuckDB in the same environment) use `import_extension("httpfs", force_install=True)`.

Verify that an extension is ready with:

```python
import duckdb

duckdb.sql("""
    SELECT installed
    FROM duckdb_extensions()
    WHERE extension_name = 'httpfs' OR list_contains(aliases, 'httpfs')
""").fetchone()
```

## Managing Multiple Extensions
Install each extension wheel you need; the helper will find them automatically. Wheels are architecture tagged during build, so you can keep the same Python environment across macOS, Linux, and Windows as long as matching wheels were published.

## Need to Extend the Project?
If you want to publish a new DuckDB version, add an extension package, or contribute fixes, follow the step-by-step instructions in `CONTRIBUTING.md`. That guide covers version bumps, cookiecutter scaffolding, CI workflows, and PR expectations.
