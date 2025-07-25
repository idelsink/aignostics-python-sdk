"""Tests for fs utilities."""

from pathlib import Path
from unittest.mock import patch

import pytest

from aignostics.utils import get_logger
from aignostics.utils._fs import (
    get_user_data_directory,
    open_user_data_directory,
    sanitize_path,
    sanitize_path_component,
)

log = get_logger(__name__)


def test_string_input_returns_string() -> None:
    """Test that string input returns string output."""
    result = sanitize_path("test/path")
    assert isinstance(result, str)
    assert result == "test/path"


def test_path_input_returns_path() -> None:
    """Test that Path input returns Path output."""
    input_path = Path("test/path")
    result = sanitize_path(input_path)
    assert isinstance(result, Path)
    assert str(result) == str(Path("test/path"))


def test_colon_replacement_on_all_platforms() -> None:
    """Test that colons are replaced on all platforms."""
    with patch("platform.system", return_value="Linux"):
        result = sanitize_path("test:path:with:colons")
        assert result == "test_path_with_colons"


def test_windows_colon_replacement_enabled() -> None:
    """Test colon replacement on Windows when enabled."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("test:path:with:colons")
        assert result == "test_path_with_colons"
    with patch("platform.system", return_value="Linux"):
        result = sanitize_path("test:path:with:colons")
        assert result == "test_path_with_colons"


def test_windows_drive_letter_preserved() -> None:
    """Test that Windows drive letters are preserved when replacing colons."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("C:/test:path")
        assert result == "C:/test_path"


def test_windows_drive_letter_with_multiple_colons() -> None:
    """Test drive letter preservation with multiple colons."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("D:/folder:name:with:colons")
        assert result == "D:/folder_name_with_colons"


def test_windows_no_drive_letter_all_colons_replaced() -> None:
    """Test that all colons are replaced when no drive letter is present."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("folder:name:with:colons")
        assert result == "folder_name_with_colons"


def test_windows_single_char_with_colon_is_drive() -> None:
    """Test that single character with colon IS treated as drive letter."""
    with patch("platform.system", return_value="Windows"):
        # "a:test" has colon in position 1 and 'a' is alphabetic, so it IS treated as a drive letter
        # Only the part after the drive letter should have colons replaced
        result = sanitize_path("a:test")
        assert result == "a:test"  # Drive letter preserved, no additional colons to replace


def test_windows_numeric_with_colon_not_drive() -> None:
    """Test that numeric character with colon is not treated as drive letter."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("1:test")
        assert result == "1_test"  # All colons replaced since '1' is not alphabetic
        result = sanitize_path("1:/test")
        assert result == "1_/test"


def test_windows_reserved_path_raises_error() -> None:
    """Test that reserved Windows paths raise ValueError."""
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
        pytest.raises(ValueError, match="The path 'CON' is reserved on Windows"),
    ):
        sanitize_path("CON")


def test_windows_non_reserved_path_succeeds() -> None:
    """Test that non-reserved Windows paths succeed."""
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=False),
    ):
        result = sanitize_path("valid_path")
        assert result == "valid_path"


def test_windows_reserved_path_with_path_object() -> None:
    """Test that reserved Windows paths raise ValueError with Path input."""
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
        pytest.raises(ValueError, match="The path 'PRN' is reserved on Windows"),
    ):
        sanitize_path(Path("PRN"))


def test_windows_reserved_path_after_colon_replacement() -> None:
    """Test reserved path check happens after colon replacement."""
    with (
        patch("platform.system", return_value="Windows"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
        pytest.raises(ValueError, match="The path 'test_AUX' is reserved on Windows"),
    ):
        sanitize_path("test:AUX")


def test_non_windows_reserved_check_skipped() -> None:
    """Test that reserved path check is skipped on non-Windows systems."""
    with (
        patch("platform.system", return_value="Linux"),
        patch("pathlib.PureWindowsPath.is_reserved", return_value=True),
    ):
        # This should not raise an error even if PureWindowsPath.is_reserved returns True
        result = sanitize_path("CON")
        assert result == "CON"


def test_windows_empty_string() -> None:
    """Test handling of empty string on Windows."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("")
        assert not result


def test_windows_path_object_preserves_type() -> None:
    """Test that Path object input returns Path object with colon replacement."""
    with patch("platform.system", return_value="Windows"):
        input_path = Path("test:path")
        result = sanitize_path(input_path)
        assert isinstance(result, Path)
        assert str(result) == "test_path"


def test_windows_complex_path_with_drive() -> None:
    """Test complex Windows path with drive letter and multiple colons."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("C:/Users/test:user/Documents/file:name.txt")
        assert result == "C:/Users/test_user/Documents/file_name.txt"


# Tests for sanitize_path_component function
def test_sanitize_path_component_all_platforms() -> None:
    """Test that sanitize_path_component replaces colons on all platforms."""
    with patch("platform.system", return_value="Linux"):
        result = sanitize_path_component("test:component:with:colons")
        assert result == "test_component_with_colons"


def test_sanitize_path_component_windows_replaces_all_colons() -> None:
    """Test that sanitize_path_component replaces all colons on Windows."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("test:component:with:colons")
        assert result == "test_component_with_colons"


def test_sanitize_path_component_windows_drive_like_pattern() -> None:
    """Test that sanitize_path_component replaces colons even for drive-like patterns."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("a:whatever")
        assert result == "a_whatever"
        result = sanitize_path_component("C:filename")
        assert result == "C_filename"


def test_sanitize_path_component_windows_empty_string() -> None:
    """Test that sanitize_path_component handles empty string."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("")
        assert not result


def test_sanitize_path_component_windows_no_colons() -> None:
    """Test that sanitize_path_component returns unchanged when no colons."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("normal_filename.txt")
        assert result == "normal_filename.txt"


def test_sanitize_path_component_multiple_consecutive_colons() -> None:
    """Test that sanitize_path_component handles multiple consecutive colons."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path_component("file:::name")
        assert result == "file___name"


# Tests for integration between sanitize_path and sanitize_path_component
def test_sanitize_path_uses_sanitize_path_component_for_drive_path() -> None:
    """Test that sanitize_path uses sanitize_path_component for the non-drive part."""
    with patch("platform.system", return_value="Windows"):
        # Drive letter should be preserved, but rest should be sanitized using sanitize_path_component
        result = sanitize_path("C:/folder:name:with:colons")
        assert result == "C:/folder_name_with_colons"


def test_sanitize_path_uses_sanitize_path_component_for_non_drive_path() -> None:
    """Test that sanitize_path uses sanitize_path_component for paths without drive letters."""
    with patch("platform.system", return_value="Windows"):
        result = sanitize_path("folder:name:with:colons")
        assert result == "folder_name_with_colons"


# Tests for get_user_data_directory function
def test_get_user_data_directory_without_scope(tmp_path) -> None:
    """Test get_user_data_directory returns correct path without scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory()

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_user_data_directory_with_scope(tmp_path) -> None:
    """Test get_user_data_directory returns correct path with scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("models")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "models")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_user_data_directory_with_nested_scope(tmp_path) -> None:
    """Test get_user_data_directory returns correct path with nested scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("cache/models")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "cache" / "models")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_user_data_directory_read_only_environment_no_mkdir(tmp_path) -> None:
    """Test get_user_data_directory doesn't create directory in read-only environment."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", True),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("cache")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "cache")
        mock_mkdir.assert_not_called()


def test_get_user_data_directory_empty_scope(tmp_path) -> None:
    """Test get_user_data_directory handles empty scope string."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory("")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_user_data_directory_none_scope(tmp_path) -> None:
    """Test get_user_data_directory handles None scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = get_user_data_directory(None)

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# Tests for open_user_data_directory function
def test_open_user_data_directory_without_scope(tmp_path) -> None:
    """Test open_user_data_directory opens correct directory without scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory()

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project"))


def test_open_user_data_directory_with_scope(tmp_path) -> None:
    """Test open_user_data_directory opens correct directory with scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory("logs")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "logs")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project" / "logs"))


def test_open_user_data_directory_with_nested_scope(tmp_path) -> None:
    """Test open_user_data_directory opens correct directory with nested scope."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory("cache/models")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "cache" / "models")
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project" / "cache" / "models"))


def test_open_user_data_directory_read_only_environment(tmp_path) -> None:
    """Test open_user_data_directory works in read-only environment."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", True),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")

        result = open_user_data_directory("data")

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project" / "data")
        mock_mkdir.assert_not_called()  # Should not create directory in read-only environment
        mock_show_in_file_manager.assert_called_once_with(str(tmp_path / "test_project" / "data"))


def test_open_user_data_directory_show_in_file_manager_exception(tmp_path) -> None:
    """Test open_user_data_directory handles show_in_file_manager exceptions gracefully."""
    with (
        patch("aignostics.utils._fs.appdirs.user_data_dir") as mock_user_data_dir,
        patch("aignostics.utils._fs.__project_name__", "test_project"),
        patch("aignostics.utils._fs.__is_running_in_read_only_environment__", False),
        patch("pathlib.Path.mkdir") as _mock_mkdir,
        patch("aignostics.utils._fs.show_in_file_manager") as mock_show_in_file_manager,
    ):
        mock_user_data_dir.return_value = str(tmp_path / "test_project")
        mock_show_in_file_manager.side_effect = Exception("File manager not available")

        # The function should still return the path even if file manager fails
        result = open_user_data_directory()

        mock_user_data_dir.assert_called_once_with("test_project")
        assert isinstance(result, Path)
        assert str(result) == str(tmp_path / "test_project")
