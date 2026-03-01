"""Shared constants for checksum verification."""

import re
from pathlib import Path

CHECKSUMS_MANIFEST_SCHEMA_VERSION = 1
EXTENSION_NAME_PATTERN = re.compile(r"^[a-z0-9_]+$")
SUPPORTED_ARCHITECTURES = frozenset({
    "linux_amd64",
    "linux_arm64",
    "osx_arm64",
    "osx_amd64",
    "windows_amd64",
})
# Ordered tuple for CLI defaults and iteration
DEFAULT_ARCHITECTURES = (
    "linux_amd64",
    "linux_arm64",
    "osx_amd64",
    "osx_arm64",
    "windows_amd64",
)
CHECKSUMS_MANIFEST_FILENAME = "extension_checksums.json"


def get_checksums_manifest_path(repo_root: Path | None = None) -> Path:
    """Return path to extension_checksums.json relative to repo root."""
    if repo_root is None:
        repo_root = Path(__file__).parent
    return repo_root / CHECKSUMS_MANIFEST_FILENAME
