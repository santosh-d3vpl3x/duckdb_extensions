# ODBC Naming Symmetry Design

**Context**

DuckDB 1.5.0 exposes a single installable extension entry for ODBC:

- canonical extension name: `odbc_scanner`
- alias: `odbc`

Local runtime verification with `duckdb_extensions()` shows one row:

- `extension_name = 'odbc_scanner'`
- `aliases = ['odbc']`

This repository already publishes paired wrapper packages for similar alias/canonical-name cases:

- `duckdb_extension_mysql` and `duckdb_extension_mysql_scanner`
- `duckdb_extension_postgres` and `duckdb_extension_postgres_scanner`
- `duckdb_extension_sqlite` and `duckdb_extension_sqlite_scanner`

**Decision**

Add both Python wrapper packages for ODBC:

- `duckdb_extension_odbc`
- `duckdb_extension_odbc_scanner`

Both wrappers will target the same upstream DuckDB extension artifact name:

- `tool.extension_builder.extension_name = "odbc_scanner"`

**Why This Approach**

This preserves naming symmetry with the repository’s existing package model while still matching DuckDB’s upstream naming rules. Users who think in DuckDB aliases can install `duckdb-extension-odbc`, while users who expect canonical extension names can install `duckdb-extension-odbc-scanner`.

**Package Behavior**

- `duckdb_extension_odbc` is the alias-facing package.
- `duckdb_extension_odbc_scanner` is the canonical-name package.
- Both packages bundle the same upstream `odbc_scanner` binary.
- `extension_checksums.json` should only gain entries for `odbc_scanner`, since that is the actual downloaded artifact.

**Docs and Metadata**

- `README.md` should list both wrapper packages.
- `THIRD_PARTY_LICENSES.md` should include both `odbc` and `odbc_scanner` rows, mirroring the published wrapper names.
- Both extension READMEs should explain their install/import usage using their respective package names and runtime import names.

**Testing**

- Verify local wheel builds for both wrappers.
- Verify licensing metadata with `python scripts/maintainer.py verify-licensing`.
- Verify checksum coverage remains valid after adding the second wrapper.

**Risks**

- The two wrappers can drift if one package’s metadata is updated without the other.
- Local runtime smoke tests can be affected by ODBC shared-library availability on the machine.
- The current importer/build layout may require wheel-based verification rather than editable-install verification.
