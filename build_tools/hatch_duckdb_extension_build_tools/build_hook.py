import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from duckdb_extension_build_tools.plugin import DuckDBExtensionBuildHook


class CustomBuildHook(DuckDBExtensionBuildHook):
    """Thin wrapper so Hatch's custom hook loader can find a single subclass."""


def get_build_hook():
    return CustomBuildHook
