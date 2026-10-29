# DuckDB 2.0.0 upgrade investigation

Tracking issue: https://github.com/santosh-d3vpl3x/duckdb_extensions/issues/60

Upstream sources checked on 2026-10-28:

- https://pypi.org/pypi/duckdb/2.0.0/json confirms release 2.0.0 (uploaded October 21) and Python >=3.11.0.
- https://duckdb.org/docs/stable/core_extensions/overview redirects to https://duckdb.org/docs/2.0/core_extensions/overview.html.
- Compared that table with https://duckdb.org/docs/1.5/core_extensions/overview.html: additions are `legacy_parser` and `sirius`; no names were removed.

## Extension coverage

Before this change: 29 of the 31 documented canonical names, with 34 package names including five aliases. Added `legacy_parser`, bringing coverage to 30/31 canonical names and 35 extension packages. The extra package names are aliases: `mysql_scanner`, `odbc_scanner`, `postgres_scanner`, `sqlite_scanner`, and `sqlite3`.

`sirius` is documented as “coming soon”. Its v2.0.0/linux_amd64 artifact returns HTTP 404, so it is not scaffolded or advertised as available. Revisit when upstream publishes artifacts. `jemalloc` is absent from both documentation tables.

Checksum refresh downloaded and hashed the uncompressed extension binaries across all five supported architectures, retaining fail-closed build verification. The 29 existing canonical names produced 141 available artifacts and four HTTP 404s. `legacy_parser` adds five verified artifacts.

Unavailable upstream combinations:

| Extension | Platform |
| --- | --- |
| lance | osx_amd64 |
| ui | osx_amd64 |
| vortex | osx_amd64 |
| vortex | windows_amd64 |

The workflows now exclude these combinations (lance and vortex/Windows were already excluded). No checksums were invented for missing binaries.

## Compatibility findings

DuckDB 2.0.0 drops Python 3.9/3.10 support. Root, extension, and scaffold metadata now require Python 3.11+, and the lockfile is refreshed.

DuckDB relations no longer implement `fetchone()`. The initial extension builds failed at the build hook's version lookup. The build hook and examples now use `fetchall()[0]`; the importer uses connection `execute(...).fetchone()` so its existing empty-result check remains valid. Artifact tests use the updated relation API.

## Local validation

Builds use the existing Hatchling backend and checksum verification, with DuckDB 2.0.0 on Python 3.12/Linux x86-64. Wheels bundle upstream binaries; this repository does not compile DuckDB itself. Other architectures have verified download checksums but cannot be executed on this host.

Reproduce locally:

```bash
UV_CACHE_DIR=/tmp/duckdb-uv-cache uv lock --upgrade-package duckdb
python scripts/maintainer.py sync-checksums --verify
python scripts/maintainer.py verify-licensing
python -m pytest tests -q
# In each extension directory, with the build dependencies and DuckDB 2.0.0 installed:
python -m hatchling build -t wheel -d linux_amd64
# Install the resulting wheel, then run from the repository root:
EXTENSION_NAME=httpfs python -m pytest test_artifact.py -q
```

Validation results:

- 36/36 wheels built successfully (root plus 35 extensions), with verified binary checksums.
- Installed the locally built wheels without fetching extension packages from PyPI.
- 35/35 extension artifact tests passed, using a writable temporary DuckDB extension directory.
- 32/32 unit tests passed against DuckDB 2.0.0.
- Loaded `httpfs`, `json`, `parquet`, `tpch`, and `legacy_parser`; generated TPC-H data at scale 0.01 and checked a JSON query successfully.
- Checksum coverage, licensing verification, and `git diff --check` passed.
- Wheel SHA-256 hashes: [duckdb-2.0.0-wheel-sha256.txt](duckdb-2.0.0-wheel-sha256.txt). Wheels remain in `dist/` and each extension's `linux_amd64/` directory (ignored by Git).

Artifact tests verify local installation, not connectivity to external services such as MotherDuck, S3, or database servers. Runtime execution on ARM, macOS, and Windows remains for CI or native hosts.
