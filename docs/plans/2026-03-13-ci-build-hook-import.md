# CI Build Hook Import Refactor Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the repo-root Hatch custom hook script with a packaged build-hook module plus a thin wrapper so extension builds no longer depend on repo-root imports.

**Architecture:** Move checksum verification and build-hook logic into `build_tools/hatch_duckdb_extension_build_tools/src/duckdb_extension_build_tools/`. Keep Hatch integration via a tiny wrapper script at `build_tools/hatch_duckdb_extension_build_tools/build_hook.py`, and point every extension package plus the template at that wrapper.

**Tech Stack:** Python, Hatchling, uv, pytest

---

### Task 1: Preserve red/green coverage

**Files:**
- Modify: `tests/test_checksum_verification.py`

**Steps:**
- Point the existing checksum tests at the packaged hook module.
- Add a regression test that proves the packaged module imports without the repo root on `sys.path`.
- Add a regression test that manifest lookup walks parent directories from an extension root.

### Task 2: Introduce the packaged hook

**Files:**
- Create: `build_tools/hatch_duckdb_extension_build_tools/pyproject.toml`
- Create: `build_tools/hatch_duckdb_extension_build_tools/build_hook.py`
- Create: `build_tools/hatch_duckdb_extension_build_tools/src/duckdb_extension_build_tools/__init__.py`
- Create: `build_tools/hatch_duckdb_extension_build_tools/src/duckdb_extension_build_tools/hooks.py`
- Create: `build_tools/hatch_duckdb_extension_build_tools/src/duckdb_extension_build_tools/plugin.py`

**Steps:**
- Move checksum helpers and the build hook implementation into `plugin.py`.
- Keep the Hatch custom-hook wrapper tiny and explicit.
- Make manifest lookup robust from nested extension package roots.

### Task 3: Repoint extension configs

**Files:**
- Modify: `extensions/*/pyproject.toml`
- Modify: `templates/duckdb_extension_{@cookiecutter.extension_name@}/pyproject.toml`
- Delete: `add_extension_files.py`

**Steps:**
- Switch every extension and the template from the repo-root hook path to the packaged wrapper path.
- Keep build requirements compatible with current Hatch behavior.
- Remove the obsolete root script once no references remain.

### Task 4: Verify on main and PR state

**Files:**
- Verify: `tests/test_checksum_verification.py`
- Verify: `extensions/duckdb_extension_postgres/pyproject.toml`

**Steps:**
- Run `uv run pytest tests/test_checksum_verification.py -v`.
- Run `hatch build -c -t wheel osx_arm64` for `duckdb_extension_postgres` on the refactored branch.
- Rebase or cherry-pick onto the PR branch and rerun the same build there to confirm the PR’s `v1.5.0` checksum data now gets past the former import failure.
