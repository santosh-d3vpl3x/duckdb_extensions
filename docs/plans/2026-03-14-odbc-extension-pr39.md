# ODBC Symmetry Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add both `odbc` and `odbc_scanner` DuckDB 1.5.0 wrapper packages to this repository using the maintainer workflow, then verify both wrappers build correctly.

**Architecture:** Use `scripts/maintainer.py add-extension` to scaffold both wrappers. Keep both wrappers pointed at the same upstream artifact name, `odbc_scanner`, so we preserve repository naming symmetry without inventing a second DuckDB binary. Verify with wheel builds, checksum sync, and licensing validation.

**Tech Stack:** Python, uv, Hatchling, pytest, GitHub Actions workflows

---

### Task 1: Capture the red state for both wrappers

**Files:**
- Verify: `test_artifact.py`

**Steps:**
- Run `EXTENSION_NAME=odbc uv run --with pytest python -m pytest test_artifact.py -q`.
- Confirm the failure is `ModuleNotFoundError: No module named 'duckdb_extension_odbc'`.
- Run `EXTENSION_NAME=odbc_scanner uv run --with pytest python -m pytest test_artifact.py -q`.
- Confirm the failure is `ModuleNotFoundError: No module named 'duckdb_extension_odbc_scanner'`.

### Task 2: Scaffold both ODBC wrappers with maintainer tooling

**Files:**
- Create: `extensions/duckdb_extension_odbc/`
- Create: `extensions/duckdb_extension_odbc_scanner/`
- Create: `.github/workflows/publish-odbc-to-pypi.yml`
- Create: `.github/workflows/publish-odbc_scanner-to-pypi.yml`
- Modify: `README.md`

**Steps:**
- Run `python scripts/maintainer.py add-extension odbc`.
- Run `python scripts/maintainer.py add-extension odbc_scanner`.
- Review both generated `pyproject.toml` files and READMEs for correct aliasing and package metadata.
- Point both wrappers at `extension_name = "odbc_scanner"`.

### Task 3: Add registry metadata and workspace lock coverage

**Files:**
- Modify: `THIRD_PARTY_LICENSES.md`
- Modify: `uv.lock`
- Modify: `extension_checksums.json`

**Steps:**
- Add the `odbc` and `odbc_scanner` provenance rows to `THIRD_PARTY_LICENSES.md`.
- Refresh checksums for the shared upstream artifact name `odbc_scanner`.
- Refresh the lockfile so the new workspace member is included.

### Task 4: Build and verify both ODBC wrappers

**Files:**
- Verify: `extensions/duckdb_extension_odbc/pyproject.toml`
- Verify: `extensions/duckdb_extension_odbc_scanner/pyproject.toml`
- Verify: `test_artifact.py`

**Steps:**
- Build the wheel from `extensions/duckdb_extension_odbc/` to download and bundle the binary for the local architecture.
- Build the wheel from `extensions/duckdb_extension_odbc_scanner/` to confirm the second wrapper resolves the same upstream artifact.
- Re-sync the workspace as needed so the new package is importable from the worktree.
- Run `EXTENSION_NAME=odbc uv run --with pytest python -m pytest test_artifact.py -q`.
- Run `EXTENSION_NAME=odbc_scanner uv run --with pytest python -m pytest test_artifact.py -q`.
- Run `python scripts/maintainer.py verify-licensing`.

### Task 5: Prepare the branch for push

**Files:**
- Verify: `git status`

**Steps:**
- Review the diff for only the intended ODBC additions and any required generated files.
- Commit the branch changes with a focused message.
- Push `codex/pr39-odbc` to `origin`.
