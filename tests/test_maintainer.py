import importlib.util
import sys
from pathlib import Path

from click.testing import CliRunner

MAINTAINER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "maintainer.py"
SPEC = importlib.util.spec_from_file_location("maintainer", MAINTAINER_PATH)
assert SPEC and SPEC.loader
maintainer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = maintainer
SPEC.loader.exec_module(maintainer)


def test_bump_version_invokes_checksum_callback(monkeypatch):
    checksum_calls = []

    monkeypatch.setattr(maintainer, "get_current_version", lambda: "1.5.3")
    monkeypatch.setattr(maintainer, "replace_pattern", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        maintainer.sync_checksums_cmd,
        "callback",
        lambda **kwargs: checksum_calls.append(kwargs),
    )

    result = CliRunner().invoke(maintainer.cli, ["bump-version", "1.5.4"])

    assert result.exit_code == 0, result.output
    assert checksum_calls == [
        {
            "duckdb_version": "v1.5.4",
            "extensions": "all",
            "architectures": ",".join(maintainer.DEFAULT_ARCHITECTURES),
            "timeout": 30,
            "dry_run": False,
            "verify": False,
        }
    ]
