#!/usr/bin/env python3
"""Contributor utilities for managing DuckDB extensions."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "templates" / "duckdb_extension_{@cookiecutter.extension_name@}"
EXTENSIONS_ROOT = REPO_ROOT / "extensions"
WORKFLOWS_ROOT = REPO_ROOT / ".github" / "workflows"
THIRD_PARTY_LICENSES_PATH = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
CHECKSUMS_MANIFEST_PATH = REPO_ROOT / "extension_checksums.json"
CHECKSUMS_MANIFEST_SCHEMA_VERSION = 1
DEFAULT_ARCHITECTURES = ("osx_arm64", "linux_amd64", "linux_arm64", "osx_amd64", "windows_amd64")
EXTENSION_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")
KNOWN_THIRD_PARTY_EXTENSIONS = {"motherduck"}
MOTHERDUCK_TERMS_URL = "https://motherduck.com/terms-of-service/"


@dataclass
class FileChange:
    action: str
    path: Path


def apply_placeholders(text: str, alias: str) -> str:
    alias_hyphen = alias.replace("_", "-")
    replacements = {
        '{@cookiecutter.extension_name | replace("_","-")@}': alias_hyphen,
        '{@cookiecutter.extension_name@}': alias,
    }
    for needle, substitution in replacements.items():
        text = text.replace(needle, substitution)
    return text


def apply_placeholders_to_parts(parts: Sequence[str], alias: str) -> Path:
    rendered = [apply_placeholders(part, alias) for part in parts]
    return Path(*rendered)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def get_current_version() -> str:
    version_file = REPO_ROOT / "_version.py"
    match = re.search(r'__version__\s*=\s*"([^"]+)"', read_text(version_file))
    if not match:
        raise click.ClickException("Unable to determine current version from _version.py")
    return match.group(1)


def replace_pattern(path: Path, pattern: str, replacement: str, dry_run: bool) -> bool:
    text = read_text(path)
    new_text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE)
    if not count:
        return False
    if not dry_run:
        write_text(path, new_text)
    return True


def iter_extension_pyprojects() -> Iterable[Path]:
    for pyproject in sorted(EXTENSIONS_ROOT.glob("duckdb_extension_*/pyproject.toml")):
        yield pyproject


def iter_extension_aliases() -> Iterable[str]:
    for pyproject in iter_extension_pyprojects():
        yield pyproject.parent.name.removeprefix("duckdb_extension_")


def normalize_duckdb_version(version: str) -> str:
    normalized = version.strip()
    if not normalized:
        raise click.ClickException("DuckDB version cannot be empty.")
    return normalized if normalized.startswith("v") else f"v{normalized}"


def parse_csv_items(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def get_extension_download_name(pyproject_path: Path) -> str:
    match = re.search(r'^extension_name\s*=\s*"([^"]+)"', read_text(pyproject_path), flags=re.MULTILINE)
    if not match:
        raise click.ClickException(f"Unable to find tool.extension_builder.extension_name in {pyproject_path.relative_to(REPO_ROOT)}")
    extension_name = match.group(1).strip()
    if not EXTENSION_NAME_PATTERN.fullmatch(extension_name):
        raise click.ClickException(
            f"Invalid extension_name {extension_name!r} in {pyproject_path.relative_to(REPO_ROOT)}; "
            f"must match {EXTENSION_NAME_PATTERN.pattern!r}."
        )
    return extension_name


def get_alias_to_download_name_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pyproject in iter_extension_pyprojects():
        alias = pyproject.parent.name.removeprefix("duckdb_extension_")
        mapping[alias] = get_extension_download_name(pyproject)
    return mapping


def load_checksums_manifest() -> dict:
    if not CHECKSUMS_MANIFEST_PATH.exists():
        return {"schema_version": CHECKSUMS_MANIFEST_SCHEMA_VERSION, "checksums": {}}
    manifest = json.loads(read_text(CHECKSUMS_MANIFEST_PATH))
    schema_version = manifest.get("schema_version")
    if schema_version != CHECKSUMS_MANIFEST_SCHEMA_VERSION:
        raise click.ClickException(
            f"Unsupported checksums manifest schema version {schema_version!r}. "
            f"Expected {CHECKSUMS_MANIFEST_SCHEMA_VERSION}."
        )
    if not isinstance(manifest.get("checksums"), dict):
        raise click.ClickException(f"{CHECKSUMS_MANIFEST_PATH.relative_to(REPO_ROOT)} is missing a valid `checksums` object.")
    return manifest


def write_checksums_manifest(manifest: dict) -> None:
    content = json.dumps(manifest, indent=2, sort_keys=True)
    write_text(CHECKSUMS_MANIFEST_PATH, f"{content}\n")


def compute_extension_sha256(duckdb_version: str, extension_name: str, architecture: str, timeout: int) -> str:
    url = f"https://extensions.duckdb.org/{duckdb_version}/{architecture}/{extension_name}.duckdb_extension.gz"
    request = urllib.request.Request(url, headers={"User-Agent": "duckdb-extensions-checksum-updater/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        compressed_bytes = response.read()
    extension_bytes = gzip.decompress(compressed_bytes)
    return hashlib.sha256(extension_bytes).hexdigest()


def collect_checksum_coverage_issues(
    manifest: dict,
    duckdb_version: str,
    extension_names: Sequence[str],
    architectures: Sequence[str],
) -> list[str]:
    issues: list[str] = []
    checksums = manifest.get("checksums", {})
    version_checksums = checksums.get(duckdb_version, {})
    if not version_checksums:
        issues.append(f"No checksum entries found for DuckDB version {duckdb_version}.")
        return issues

    for extension_name in extension_names:
        extension_entry = version_checksums.get(extension_name)
        if not isinstance(extension_entry, dict) or not extension_entry:
            issues.append(f"Missing checksum map for extension {extension_name!r} at version {duckdb_version}.")
            continue
        found_selected_architecture = False
        for architecture in architectures:
            digest = extension_entry.get(architecture)
            if digest is None:
                continue
            found_selected_architecture = True
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                issues.append(
                    f"Invalid checksum for {duckdb_version}/{extension_name}/{architecture} "
                    f"in {CHECKSUMS_MANIFEST_PATH.relative_to(REPO_ROOT)}."
                )
        if not found_selected_architecture:
            issues.append(
                f"No checksum entries for selected architectures for {duckdb_version}/{extension_name}. "
                "Run update-checksums with a supported architecture list."
            )
    return issues


def collect_licensing_issues() -> list[str]:
    issues: list[str] = []

    if not THIRD_PARTY_LICENSES_PATH.exists():
        return [f"Missing required file: {THIRD_PARTY_LICENSES_PATH.relative_to(REPO_ROOT)}"]

    registry_text = read_text(THIRD_PARTY_LICENSES_PATH)
    root_readme_text = read_text(REPO_ROOT / "README.md")
    contributing_text = read_text(REPO_ROOT / "CONTRIBUTING.md")

    for alias in iter_extension_aliases():
        registry_marker = f"| {alias} |"
        if registry_marker not in registry_text:
            issues.append(f"Missing {registry_marker} entry in {THIRD_PARTY_LICENSES_PATH.relative_to(REPO_ROOT)}")

    if "THIRD_PARTY_LICENSES.md" not in root_readme_text:
        issues.append("README.md must reference THIRD_PARTY_LICENSES.md")

    if "verify-licensing" not in contributing_text:
        issues.append("CONTRIBUTING.md must include verify-licensing guidance")

    for alias in sorted(KNOWN_THIRD_PARTY_EXTENSIONS):
        extension_root = EXTENSIONS_ROOT / f"duckdb_extension_{alias}"
        readme_path = extension_root / "README.md"
        pyproject_path = extension_root / "pyproject.toml"

        if not readme_path.exists():
            issues.append(f"Missing README for third-party extension: {readme_path.relative_to(REPO_ROOT)}")
        else:
            readme_text = read_text(readme_path)
            if "THIRD_PARTY_LICENSES.md" not in readme_text:
                issues.append(f"{readme_path.relative_to(REPO_ROOT)} must link THIRD_PARTY_LICENSES.md")
            if alias == "motherduck" and MOTHERDUCK_TERMS_URL not in readme_text:
                issues.append(f"{readme_path.relative_to(REPO_ROOT)} must reference {MOTHERDUCK_TERMS_URL}")

        if not pyproject_path.exists():
            issues.append(f"Missing pyproject for third-party extension: {pyproject_path.relative_to(REPO_ROOT)}")
        else:
            pyproject_text = read_text(pyproject_path)
            if "THIRD_PARTY_LICENSES.md" not in pyproject_text:
                issues.append(f"{pyproject_path.relative_to(REPO_ROOT)} must reference THIRD_PARTY_LICENSES.md in license metadata")

    return issues


def update_readme_extensions(alias: str, dry_run: bool) -> bool:
    readme_path = REPO_ROOT / "README.md"
    lines = read_text(readme_path).splitlines()
    try:
        section_index = lines.index("## Available extensions")
    except ValueError:
        raise click.ClickException("README.md does not contain '## Available extensions' section")

    start = section_index + 1
    while start < len(lines) and not lines[start].startswith("- ["):
        start += 1
    end = start
    while end < len(lines) and lines[end].startswith("- ["):
        end += 1

    bullet = f"- [duckdb_extension_{alias}](extensions/duckdb_extension_{alias})"
    current = lines[start:end]
    if bullet in current:
        return False

    updated = sorted(current + [bullet])
    new_lines = lines[:start] + updated + lines[end:]
    if not dry_run:
        write_text(readme_path, "\n".join(new_lines) + "\n")
    return True


def render_template(alias: str, dry_run: bool) -> list[FileChange]:
    if not TEMPLATE_ROOT.exists():
        raise click.ClickException("Template directory is missing; expected at templates/duckdb_extension_{@cookiecutter.extension_name@}")

    target_root = EXTENSIONS_ROOT / f"duckdb_extension_{alias}"
    if target_root.exists():
        raise click.ClickException(f"Extension directory already exists: {target_root}")

    rendered_changes: list[FileChange] = []

    for item in sorted(TEMPLATE_ROOT.rglob("*")):
        rel_path = item.relative_to(TEMPLATE_ROOT)
        if item.is_dir():
            continue
        if rel_path.name == "LICENSE.txt":
            continue

        rendered_rel = apply_placeholders_to_parts(rel_path.parts, alias)

        if rendered_rel.name.startswith("publish-") and rendered_rel.suffix == ".yml" and rendered_rel.parent == Path():
            dest_path = WORKFLOWS_ROOT / rendered_rel.name
        else:
            dest_path = (EXTENSIONS_ROOT / f"duckdb_extension_{alias}") / rendered_rel

        content = apply_placeholders(read_text(item), alias)

        exists_before = dest_path.exists()
        if not dry_run:
            write_text(dest_path, content)
        rendered_changes.append(FileChange("create" if not exists_before else "update", dest_path))

    return rendered_changes


def validate_alias(alias: str) -> str:
    normalized = alias.strip()
    if not re.fullmatch(r"[a-z0-9_]+", normalized):
        raise click.ClickException("Extension alias must be lowercase alphanumeric with optional underscores")
    return normalized


@click.group()
def cli() -> None:
    """CLI helpers for repository maintainers."""


@cli.command("bump-version")
@click.argument("new_version")
@click.option("--dry-run", is_flag=True, help="Show the changes without writing files.")
def bump_version(new_version: str, dry_run: bool) -> None:
    """Update all version pins to NEW_VERSION."""
    current_version = get_current_version()
    if new_version == current_version:
        raise click.ClickException(f"Version is already {new_version}")

    click.echo(f"Bumping DuckDB version: {current_version} -> {new_version}")

    changes: list[FileChange] = []

    # _version.py
    if replace_pattern(REPO_ROOT / "_version.py", r'(__version__\s*=\s*")([^"]+)(")', rf'\g<1>{new_version}\3', dry_run):
        changes.append(FileChange("update", REPO_ROOT / "_version.py"))

    # Root pyproject
    if replace_pattern(REPO_ROOT / "pyproject.toml", r'duckdb==[^",\s]+', f"duckdb=={new_version}", dry_run):
        changes.append(FileChange("update", REPO_ROOT / "pyproject.toml"))

    # Template pyproject
    template_pyproject = TEMPLATE_ROOT / "pyproject.toml"
    if replace_pattern(template_pyproject, r'duckdb==[^",\s]+', f"duckdb=={new_version}", dry_run):
        changes.append(FileChange("update", template_pyproject))

    # Extension pyprojects
    for pyproject in iter_extension_pyprojects():
        if replace_pattern(pyproject, r'duckdb==[^",\s]+', f"duckdb=={new_version}", dry_run):
            changes.append(FileChange("update", pyproject))

    # README compatibility blurb
    if replace_pattern(REPO_ROOT / "README.md", r'Compatible with `duckdb==[^`]+`', f"Compatible with `duckdb=={new_version}`", dry_run):
        changes.append(FileChange("update", REPO_ROOT / "README.md"))

    if not changes:
        click.echo("No changes were necessary.")
    else:
        for change in changes:
            click.echo(f"{'[dry-run]' if dry_run else 'updated'} {change.path.relative_to(REPO_ROOT)}")

    click.echo()
    click.echo("Next steps:")
    click.echo("  - run `uv lock --upgrade-package duckdb` to refresh uv.lock")
    click.echo("  - run `python scripts/maintainer.py update-checksums --duckdb-version "
               f"{normalize_duckdb_version(new_version)}`")
    click.echo("  - run `python scripts/maintainer.py verify-checksums --duckdb-version "
               f"{normalize_duckdb_version(new_version)}`")
    click.echo("  - rebuild and test the extensions before publishing")


@cli.command("update-checksums")
@click.option(
    "--duckdb-version",
    default=None,
    help="DuckDB version to update (e.g. v1.4.4 or 1.4.4). Defaults to current project version.",
)
@click.option(
    "--extensions",
    default="all",
    help="Comma-separated extension aliases (or extension names). Default: all extension workspaces.",
)
@click.option(
    "--architectures",
    default=",".join(DEFAULT_ARCHITECTURES),
    help="Comma-separated architectures to include.",
)
@click.option("--timeout", default=30, type=int, show_default=True, help="Download timeout in seconds.")
@click.option("--dry-run", is_flag=True, help="Compute and print updates without writing files.")
def update_checksums_cmd(
    duckdb_version: str | None,
    extensions: str,
    architectures: str,
    timeout: int,
    dry_run: bool,
) -> None:
    """Download extension binaries and refresh extension_checksums.json."""
    version = normalize_duckdb_version(duckdb_version or get_current_version())
    selected_architectures = parse_csv_items(architectures)
    if not selected_architectures:
        raise click.ClickException("At least one architecture is required.")

    alias_to_name = get_alias_to_download_name_map()
    known_download_names = set(alias_to_name.values())
    if extensions.strip().lower() == "all":
        selected_extension_names = sorted(known_download_names)
    else:
        selected_extension_names = []
        for item in parse_csv_items(extensions):
            if item in alias_to_name:
                selected_extension_names.append(alias_to_name[item])
            elif item in known_download_names:
                selected_extension_names.append(item)
            else:
                raise click.ClickException(f"Unknown extension alias/name: {item}")
        selected_extension_names = sorted(set(selected_extension_names))

    manifest = load_checksums_manifest()
    checksums = manifest.setdefault("checksums", {})
    version_checksums = checksums.setdefault(version, {})
    updates = 0
    missing = 0

    click.echo(
        f"Refreshing checksums for DuckDB {version}: "
        f"{len(selected_extension_names)} extensions x {len(selected_architectures)} architectures"
    )
    for extension_name in selected_extension_names:
        extension_checksums = version_checksums.setdefault(extension_name, {})
        if not isinstance(extension_checksums, dict):
            raise click.ClickException(
                f"Invalid checksum map for {version}/{extension_name} in {CHECKSUMS_MANIFEST_PATH.relative_to(REPO_ROOT)}."
            )
        for architecture in selected_architectures:
            try:
                digest = compute_extension_sha256(version, extension_name, architecture, timeout=timeout)
            except urllib.error.HTTPError as error:
                if error.code != 404:
                    raise click.ClickException(
                        f"Failed downloading {version}/{extension_name}/{architecture}: HTTP {error.code}"
                    ) from error
                if architecture in extension_checksums:
                    del extension_checksums[architecture]
                    updates += 1
                missing += 1
                click.echo(f"  {'missing':9} {version}/{extension_name}/{architecture} (upstream 404)")
                continue
            previous = extension_checksums.get(architecture)
            changed = previous != digest
            extension_checksums[architecture] = digest
            status = "updated" if changed else "unchanged"
            click.echo(f"  {status:9} {version}/{extension_name}/{architecture} -> {digest}")
            if changed:
                updates += 1

    if dry_run:
        click.echo(f"\nDry run: {updates} checksum entries would change; {missing} upstream artifacts unavailable.")
        return

    manifest["schema_version"] = CHECKSUMS_MANIFEST_SCHEMA_VERSION
    write_checksums_manifest(manifest)
    click.echo(
        f"\nWrote {CHECKSUMS_MANIFEST_PATH.relative_to(REPO_ROOT)} "
        f"({updates} updated entries, {missing} upstream artifacts unavailable)."
    )


@cli.command("verify-checksums")
@click.option(
    "--duckdb-version",
    default=None,
    help="DuckDB version to verify (e.g. v1.4.4 or 1.4.4). Defaults to current project version.",
)
@click.option(
    "--extensions",
    default="all",
    help="Comma-separated extension aliases (or extension names). Default: all extension workspaces.",
)
@click.option(
    "--architectures",
    default=",".join(DEFAULT_ARCHITECTURES),
    help="Comma-separated architectures to verify.",
)
def verify_checksums_cmd(duckdb_version: str | None, extensions: str, architectures: str) -> None:
    """Verify extension_checksums.json coverage for selected version/extensions/architectures."""
    version = normalize_duckdb_version(duckdb_version or get_current_version())
    selected_architectures = parse_csv_items(architectures)
    if not selected_architectures:
        raise click.ClickException("At least one architecture is required.")

    alias_to_name = get_alias_to_download_name_map()
    known_download_names = set(alias_to_name.values())
    if extensions.strip().lower() == "all":
        selected_extension_names = sorted(known_download_names)
    else:
        selected_extension_names = []
        for item in parse_csv_items(extensions):
            if item in alias_to_name:
                selected_extension_names.append(alias_to_name[item])
            elif item in known_download_names:
                selected_extension_names.append(item)
            else:
                raise click.ClickException(f"Unknown extension alias/name: {item}")
        selected_extension_names = sorted(set(selected_extension_names))

    manifest = load_checksums_manifest()
    issues = collect_checksum_coverage_issues(
        manifest=manifest,
        duckdb_version=version,
        extension_names=selected_extension_names,
        architectures=selected_architectures,
    )
    if issues:
        click.echo("Checksum coverage checks failed:")
        for issue in issues:
            click.echo(f"  - {issue}")
        raise click.ClickException("Fix checksum issues and run verify-checksums again.")
    click.echo("Checksum coverage checks passed.")


@cli.command("add-extension")
@click.argument("alias")
@click.option("--dry-run", is_flag=True, help="Show planned file operations without writing.")
def add_extension(alias: str, dry_run: bool) -> None:
    """Scaffold a new extension workspace using the repo template."""
    alias = validate_alias(alias)

    if not TEMPLATE_ROOT.exists():
        raise click.ClickException("Template directory is missing; expected at templates/duckdb_extension_{@cookiecutter.extension_name@}")

    click.echo(f"Preparing extension scaffold for '{alias}'")

    changes = render_template(alias, dry_run=dry_run)

    if update_readme_extensions(alias, dry_run=dry_run):
        changes.append(FileChange("update", REPO_ROOT / "README.md"))

    if not changes:
        click.echo("Everything already up to date; nothing to do.")
        return

    for change in changes:
        prefix = "[dry-run]" if dry_run else change.action
        click.echo(f"{prefix:>9} {change.path.relative_to(REPO_ROOT)}")

    click.echo()
    if dry_run:
        click.echo("Dry run complete. Re-run without --dry-run to write files.")
        return

    click.echo("Scaffold created. Follow up with:")
    click.echo(f"  - inspect extensions/duckdb_extension_{alias}/pyproject.toml")
    click.echo(f"  - run `EXTENSION_NAME={alias} uv run pytest test_artifact.py`")
    click.echo("  - run `python scripts/maintainer.py update-checksums --extensions "
               f"{alias} --duckdb-version {normalize_duckdb_version(get_current_version())}`")
    click.echo("  - run `python scripts/maintainer.py verify-checksums --extensions "
               f"{alias} --duckdb-version {normalize_duckdb_version(get_current_version())}`")
    click.echo("  - update THIRD_PARTY_LICENSES.md and run `python scripts/maintainer.py verify-licensing`")
    click.echo("  - commit the new files and open a PR (remember the package checklist)")


@cli.command("verify-licensing")
def verify_licensing_cmd() -> None:
    """Verify extension licensing provenance metadata and links."""
    issues = collect_licensing_issues()
    if issues:
        click.echo("Licensing checks failed:")
        for issue in issues:
            click.echo(f"  - {issue}")
        raise click.ClickException("Fix the licensing issues above and run verify-licensing again.")
    click.echo("Licensing checks passed.")


if __name__ == "__main__":
    cli()
