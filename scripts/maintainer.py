#!/usr/bin/env python3
"""Contributor utilities for managing DuckDB extensions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = REPO_ROOT / "templates" / "duckdb_extension_{@cookiecutter.extension_name@}"
EXTENSIONS_ROOT = REPO_ROOT / "extensions"
WORKFLOWS_ROOT = REPO_ROOT / ".github" / "workflows"


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
    click.echo("  - rebuild and test the extensions before publishing")


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
    click.echo("  - commit the new files and open a PR (remember the package checklist)")


if __name__ == "__main__":
    cli()
