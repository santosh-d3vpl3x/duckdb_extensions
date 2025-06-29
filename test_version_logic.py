import tempfile
import pathlib

from src.duckdb_extensions.extension_importer import _get_compatible_version_dir


def test_exact_version_fallback():
    """Test fallback to exact version when no date-based versions exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.3").mkdir()
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3"


def test_no_matching_date_versions():
    """Test fallback to exact when no matching date-based versions exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.2.20240101").mkdir()  # Different base
        (extensions_dir / "1.1.4.20240101").mkdir()  # Different base
        (extensions_dir / "1.1.3").mkdir()           # Exact match
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3"


def test_extensions_dir_not_exists():
    """Test behavior when extensions directory doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == temp_path / "extensions" / "1.1.3"


def test_invalid_date_versions_ignored():
    """Test that invalid date-based versions are ignored."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.3.20240101").mkdir()  # Valid date
        (extensions_dir / "1.1.3.abc").mkdir()       # Invalid - non-numeric
        (extensions_dir / "1.1.3.20240523").mkdir()  # Valid date (latest)
        (extensions_dir / "1.1.3").mkdir()           # Exact match
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3.20240523"


def test_files_ignored_only_directories():
    """Test that files are ignored, only directories are considered."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.3.20240101").mkdir()
        (extensions_dir / "1.1.3.20240523").touch()  # File, should be ignored
        (extensions_dir / "1.1.3.20240315").mkdir()
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3.20240315"


def test_date_based_version_selection():
    """Test selection of latest date-based version (stub package style)."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.3.20240101").mkdir()  # Jan 1, 2024
        (extensions_dir / "1.1.3.20240523").mkdir()  # May 23, 2024 (latest)
        (extensions_dir / "1.1.3.20240315").mkdir()  # Mar 15, 2024
        (extensions_dir / "1.1.3.20231201").mkdir()  # Dec 1, 2023 (oldest)
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3.20240523"


def test_date_priority_over_exact():
    """Test that date-based versions are preferred over exact match."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.3").mkdir()                # Exact match
        (extensions_dir / "1.1.3.20240101").mkdir()       # Older date
        (extensions_dir / "1.1.3.20240523").mkdir()       # Latest date
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3.20240523"


def test_cross_year_date_comparison():
    """Test proper date comparison across years."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        extensions_dir = temp_path / "extensions"
        extensions_dir.mkdir()
        
        (extensions_dir / "1.1.3.20231215").mkdir()  # Dec 15, 2023
        (extensions_dir / "1.1.3.20240105").mkdir()  # Jan 5, 2024 (latest)
        (extensions_dir / "1.1.3.20230901").mkdir()  # Sep 1, 2023
        
        result = _get_compatible_version_dir(temp_path, "1.1.3")
        assert result == extensions_dir / "1.1.3.20240105"