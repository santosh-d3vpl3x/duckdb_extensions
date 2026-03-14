# Contributor Guide

Thanks for helping grow the DuckDB Extensions ecosystem! This guide explains how to set up a development environment, run tests, and extend the project with new DuckDB versions or extension packages.

## Local Environment
- Install dependencies with [uv](https://github.com/astral-sh/uv) (recommended):
  ```bash
  uv sync --verbose
  ```
  `uv` installs the root package and every workspace under `extensions/`.
- If you use `pip`, make sure to install the project in editable mode and include the workspaces you plan to touch:
  ```bash
  pip install -e .
  ```
- Maintainer helpers live in `scripts/maintainer.py`. Run `python scripts/maintainer.py --help` (or add `--dry-run`) before performing repo-wide chores.
- Install the optional maintainer dependencies so the CLI works out of the box:
  ```bash
  uv pip install '.[maintainer]'
  ```

## Tests and Quality Checks
- Unit tests expect the extension under test via the `EXTENSION_NAME` environment variable:
  ```bash
  EXTENSION_NAME=httpfs uv run pytest test_artifact.py
  ```
  Run tests for each extension you modify.
- Building a wheel downloads the extension binaries and is a good smoke test:
  ```bash
  uv tool run hatch build -t wheel
  ```
  Inside an extension workspace you can target a specific architecture, e.g. `uv tool run hatch build -t wheel linux_amd64`.
- Sync checksum metadata for the active DuckDB version:
  ```bash
  python scripts/maintainer.py sync-checksums
  ```
- Verify licensing provenance notes are up to date:
  ```bash
  python scripts/maintainer.py verify-licensing
  ```

## Updating the DuckDB Runtime Version
When DuckDB publishes a new release and you want this repository to match it:

1. Use the maintainer CLI to bump all pins (preview with `--dry-run` if you like):
   ```bash
   python scripts/maintainer.py bump-version <new_version>
   ```
   This updates `_version.py`, every `pyproject.toml`, and the compatibility line in `README.md`.
2. Refresh `uv.lock` so the workspace picks up the new pin:
   ```bash
   uv lock --upgrade-package duckdb
   uv sync
   ```
3. Rebuild the wheels (at least once per architecture you can exercise locally) so the packaged build hook downloads the new binaries.
4. `bump-version` automatically runs checksum sync unless you pass `--skip-checksums` (for offline/emergency workflows). If skipped, run:
   ```bash
   python scripts/maintainer.py sync-checksums --duckdb-version <new_version>
   ```
5. Run the tests with one or more extensions to verify the build:
   ```bash
   EXTENSION_NAME=httpfs uv run pytest test_artifact.py
   ```
6. Double-check any additional docs that mention the old version (`USER_GUIDE.md`, release notes, etc.).

## Adding a New Extension Package
1. Confirm the extension exists on DuckDB’s extension server (`https://extensions.duckdb.org/<duckdb_version>/<arch>/<extension>.duckdb_extension.gz`) and decide on the Python package alias (usually the DuckDB alias).
2. Run the maintainer CLI to scaffold the package (add `--dry-run` to preview):
   ```bash
   python scripts/maintainer.py add-extension <extension_alias>
   ```
   This creates `extensions/duckdb_extension_<extension_alias>/`, adds a README entry, and copies a GitHub Actions workflow to `.github/workflows/`.
3. Review the generated `pyproject.toml`:
   - `dependencies` must pin the current DuckDB version.
   - `[tool.extension_builder].extension_name` must match the DuckDB `INSTALL` name.
4. Update licensing provenance:
   - Add or update the extension row in `THIRD_PARTY_LICENSES.md`.
   - If the extension has non-default upstream licensing/terms, update the extension `README.md` `License` section to clearly distinguish wrapper/package license vs bundled binary terms.
5. Refresh checksum entries for the new extension:
   ```bash
   python scripts/maintainer.py sync-checksums --extensions <extension_alias>
   ```
6. If the new extension needs additional documentation (for example, usage nuances), update `README.md` and `USER_GUIDE.md` accordingly.
7. Build a wheel to download and bundle the binaries:
   ```bash
   cd extensions/duckdb_extension_<extension_alias>
   uv tool run hatch build -t wheel linux_amd64
   ```
8. Run the test suite for the new extension:
   ```bash
   EXTENSION_NAME=<extension_alias> uv run pytest test_artifact.py
   ```
9. If you created new files (wheel artifacts, lockfile updates, workflow), stage them in git before opening the PR.

## Running GitHub Actions Locally

- `act` ( [Docs](https://nektosact.com/) | [GitHub](https://github.com/nektos/act) ) enables you to run GitHub Actions locally via Docker. Example commands:

   - Run a specific workflow: `act push --workflows ".github/workflows/publish-httpfs-to-pypi.yml"`
   - Run just the build-and-test action on a workflow: `act push --workflows ".github/workflows/publish-vortex-to-pypi.yml" --job build-and-test`

## Pull Requests
- Every PR must state which package(s) need to be built or published. Include a checklist near the top of the PR description and tick the ones that apply—for example:
  ```
  Packages to publish:
  - [x] duckdb-extension-httpfs
  - [ ] duckdb-extensions
  ```
- Keep PRs focused and include documentation updates when behaviour changes.
- Ensure tests pass locally for every extension you touched (`EXTENSION_NAME=<name> uv run pytest test_artifact.py`).
- For checksum-managed extension builds, run `python scripts/maintainer.py sync-checksums --verify` after updating version pins and extension metadata.
- For extension packaging changes, run `python scripts/maintainer.py verify-licensing` and include any `THIRD_PARTY_LICENSES.md` updates in the PR.
- For release-related PRs (new DuckDB version or new extension) attach build logs or wheel hashes if you have them; they speed up code review.

## AI Agent Instructions

When asked to check for missing extensions or find new extensions to add:

1. Fetch the official DuckDB extensions list from https://duckdb.org/docs/stable/core_extensions/overview
2. Extract all extension names from the documentation table
3. List current extensions in this repo:
   ```bash
   ls -d extensions/duckdb_extension_* | sed 's/extensions\/duckdb_extension_//'
   ```
4. Compare and report:
   - **Missing:** Extensions in DuckDB docs but not in this repo
   - **Extra:** Extensions in repo but not in docs (these may be aliases like `mysql_scanner` for `mysql`)
   - **Coverage:** Number of supported extensions vs total available

Note: Some extensions like `jemalloc` are platform-specific (Linux only) and may intentionally not be packaged. When adding a new extension, follow the "Adding a New Extension Package" section above.
