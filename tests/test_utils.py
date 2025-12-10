"""Tests for utility functions."""

from pathlib import Path

from src.utils import resource_path, sanitize_filename


class TestResourcePath:
    """Tests for resource_path function."""

    def test_returns_path_object(self):
        """Should return a Path object."""
        result = resource_path("some/path")
        assert isinstance(result, Path)

    def test_relative_path_is_appended(self):
        """Should append the relative path to base path."""
        result = resource_path("resources/logo.ico")
        assert result.name == "logo.ico"
        assert "resources" in str(result)

    def test_handles_empty_path(self):
        """Should handle empty relative path."""
        result = resource_path("")
        assert isinstance(result, Path)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_valid_filename_unchanged(self):
        """Valid filenames should remain unchanged."""
        assert sanitize_filename("id_rsa") == "id_rsa"
        assert sanitize_filename("my_key_2024") == "my_key_2024"

    def test_removes_invalid_windows_characters(self):
        """Should replace Windows-invalid characters with underscores."""
        assert sanitize_filename("file<name") == "file_name"
        assert sanitize_filename("file>name") == "file_name"
        assert sanitize_filename("file:name") == "file_name"
        assert sanitize_filename('file"name') == "file_name"
        assert sanitize_filename("file/name") == "file_name"
        assert sanitize_filename("file\\name") == "file_name"
        assert sanitize_filename("file|name") == "file_name"
        assert sanitize_filename("file?name") == "file_name"
        assert sanitize_filename("file*name") == "file_name"

    def test_multiple_invalid_characters(self):
        """Should handle multiple invalid characters."""
        assert sanitize_filename("a<b>c:d") == "a_b_c_d"

    def test_strips_whitespace(self):
        """Should strip leading and trailing whitespace."""
        assert sanitize_filename("  filename  ") == "filename"
        assert sanitize_filename("\tfilename\n") == "filename"

    def test_strips_leading_trailing_dots(self):
        """Should strip leading and trailing dots."""
        assert sanitize_filename(".filename") == "filename"
        assert sanitize_filename("filename.") == "filename"
        assert sanitize_filename("...filename...") == "filename"

    def test_empty_string_returns_default(self):
        """Empty string should return default filename."""
        assert sanitize_filename("") == "id_ssh"

    def test_only_invalid_chars_returns_default(self):
        """String with only invalid chars should return default."""
        assert sanitize_filename("<<<>>>") == "id_ssh"

    def test_only_dots_returns_default(self):
        """String with only dots should return default."""
        assert sanitize_filename("...") == "id_ssh"

    def test_preserves_extension_dots(self):
        """Should preserve dots within the filename."""
        assert sanitize_filename("file.name.txt") == "file.name.txt"
