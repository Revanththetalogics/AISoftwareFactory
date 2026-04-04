"""
Tests for security utilities in backend/utils/security.py.

Tests cover:
- sanitize_file_path(): directory traversal prevention
- sanitize_filename(): filename sanitization
- is_safe_path(): path safety checks
- hash_password() / verify_password(): password hashing
"""

import os

import pytest

from backend.core.exceptions import ValidationError
from backend.utils.security import (
    hash_password,
    is_safe_path,
    sanitize_file_path,
    sanitize_filename,
    verify_password,
)


class TestSanitizeFilePath:
    """Tests for sanitize_file_path() function."""

    def test_valid_relative_path(self, tmp_path):
        """Test valid relative path stays within base directory."""
        base_dir = str(tmp_path)
        result = sanitize_file_path("subdir/file.txt", base_dir)

        assert result.startswith(base_dir)
        assert "subdir" in result
        assert "file.txt" in result

    def test_valid_nested_path(self, tmp_path):
        """Test valid nested path stays within base directory."""
        base_dir = str(tmp_path)
        result = sanitize_file_path("a/b/c/file.txt", base_dir)

        assert result.startswith(base_dir)
        assert result.endswith("file.txt")

    def test_simple_filename(self, tmp_path):
        """Test simple filename without path separators."""
        base_dir = str(tmp_path)
        result = sanitize_file_path("file.txt", base_dir)

        expected = os.path.join(base_dir, "file.txt")
        assert os.path.normpath(result) == os.path.normpath(expected)

    def test_traversal_attempt_blocked(self, tmp_path):
        """Test directory traversal with ../ is blocked."""
        base_dir = str(tmp_path)

        with pytest.raises(ValidationError) as exc_info:
            sanitize_file_path("../etc/passwd", base_dir)

        assert "traversal" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_multiple_traversal_blocked(self, tmp_path):
        """Test multiple traversal attempts are blocked."""
        base_dir = str(tmp_path)

        with pytest.raises(ValidationError):
            sanitize_file_path("../../../../../../etc/passwd", base_dir)

    def test_traversal_in_middle_blocked(self, tmp_path):
        """Test traversal in middle of path is blocked."""
        base_dir = str(tmp_path)

        with pytest.raises(ValidationError):
            sanitize_file_path("valid/../../../etc/passwd", base_dir)

    def test_backslash_traversal_blocked(self, tmp_path):
        """Test Windows-style backslash traversal is blocked."""
        base_dir = str(tmp_path)

        with pytest.raises(ValidationError):
            sanitize_file_path("..\\..\\etc\\passwd", base_dir)

    def test_empty_path_raises_error(self, tmp_path):
        """Test empty path raises ValidationError."""
        base_dir = str(tmp_path)

        with pytest.raises(ValidationError) as exc_info:
            sanitize_file_path("", base_dir)

        assert "empty" in str(exc_info.value).lower()

    def test_empty_base_dir_raises_error(self, tmp_path):
        """Test empty base directory raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_file_path("file.txt", "")

        assert "empty" in str(exc_info.value).lower()

    def test_none_path_raises_error(self, tmp_path):
        """Test None path raises ValidationError."""
        base_dir = str(tmp_path)

        with pytest.raises(ValidationError):
            sanitize_file_path(None, base_dir)

    def test_absolute_path_within_base(self, tmp_path):
        """Test absolute path within base directory is handled."""
        base_dir = str(tmp_path)
        abs_path = os.path.join(base_dir, "subdir", "file.txt")

        # When joining absolute path with base, os.path.join uses the absolute path
        # The function should detect this and validate it
        result = sanitize_file_path(abs_path, base_dir)
        assert result.startswith(base_dir)


class TestSanitizeFilename:
    """Tests for sanitize_filename() function."""

    def test_valid_filename(self):
        """Test valid filename passes through."""
        result = sanitize_filename("my_file.txt")
        assert result == "my_file.txt"

    def test_valid_filename_with_numbers(self):
        """Test filename with numbers."""
        result = sanitize_filename("file123.txt")
        assert result == "file123.txt"

    def test_filename_with_spaces(self):
        """Test filename with spaces is preserved."""
        result = sanitize_filename("my file.txt")
        assert "my file.txt" == result or "my file" in result

    def test_filename_with_special_chars_sanitized(self):
        """Test special characters are replaced."""
        result = sanitize_filename('file<>:"|?*.txt')

        # Should not contain dangerous characters
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_path_separators_replaced(self):
        """Test path separators are replaced."""
        result = sanitize_filename("path/to/file.txt")
        assert "/" not in result

        result = sanitize_filename("path\\to\\file.txt")
        assert "\\" not in result

    def test_traversal_in_filename_sanitized(self):
        """Test traversal sequences in filename are sanitized."""
        result = sanitize_filename("../../../etc/passwd")

        # Should not be able to traverse
        assert ".." not in result or "/" not in result

    def test_null_byte_removed(self):
        """Test null bytes are removed."""
        result = sanitize_filename("file\x00.txt")
        assert "\x00" not in result

    def test_leading_dots_stripped(self):
        """Test leading dots are stripped."""
        result = sanitize_filename("...file.txt")
        # Leading dots should be stripped
        assert not result.startswith(".")

    def test_trailing_dots_stripped(self):
        """Test trailing dots are stripped."""
        result = sanitize_filename("file.txt...")
        assert not result.endswith("...")

    def test_leading_spaces_stripped(self):
        """Test leading spaces are stripped."""
        result = sanitize_filename("   file.txt")
        assert not result.startswith(" ")

    def test_empty_filename_raises_error(self):
        """Test empty filename raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_filename("")

        assert "empty" in str(exc_info.value).lower()

    def test_only_dots_raises_error(self):
        """Test filename with only dots and spaces raises error."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_filename("...")

        assert "invalid" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_max_length_truncation(self):
        """Test filename is truncated to max length."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name, max_length=255)

        assert len(result) <= 255

    def test_max_length_preserves_extension(self):
        """Test truncation preserves file extension."""
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name, max_length=255)

        assert result.endswith(".txt")

    def test_custom_max_length(self):
        """Test custom max length is respected."""
        filename = "a" * 100 + ".txt"
        result = sanitize_filename(filename, max_length=50)

        assert len(result) <= 50

    def test_consecutive_underscores_collapsed(self):
        """Test consecutive underscores are collapsed."""
        result = sanitize_filename("file____name.txt")
        assert "____" not in result


class TestIsSafePath:
    """Tests for is_safe_path() function."""

    def test_safe_path_returns_true(self, tmp_path):
        """Test safe path returns True."""
        base_dir = str(tmp_path)
        result = is_safe_path("subdir/file.txt", base_dir)

        assert result is True

    def test_simple_filename_is_safe(self, tmp_path):
        """Test simple filename is safe."""
        base_dir = str(tmp_path)
        result = is_safe_path("file.txt", base_dir)

        assert result is True

    def test_traversal_returns_false(self, tmp_path):
        """Test traversal path returns False."""
        base_dir = str(tmp_path)
        result = is_safe_path("../etc/passwd", base_dir)

        assert result is False

    def test_multiple_traversal_returns_false(self, tmp_path):
        """Test multiple traversal returns False."""
        base_dir = str(tmp_path)
        result = is_safe_path("../../../../etc/passwd", base_dir)

        assert result is False

    def test_empty_path_returns_false(self, tmp_path):
        """Test empty path returns False."""
        base_dir = str(tmp_path)
        result = is_safe_path("", base_dir)

        assert result is False

    def test_empty_base_returns_false(self):
        """Test empty base directory returns False."""
        result = is_safe_path("file.txt", "")

        assert result is False

    def test_nested_safe_path(self, tmp_path):
        """Test deeply nested safe path."""
        base_dir = str(tmp_path)
        result = is_safe_path("a/b/c/d/e/file.txt", base_dir)

        assert result is True


class TestPasswordHashing:
    """Tests for hash_password() and verify_password() functions."""

    def test_hash_password_produces_hash(self):
        """Test password hashing produces a hash."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password

    def test_hash_password_produces_bcrypt_format(self):
        """Test hash is in bcrypt format."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        # bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith("$2")
        assert len(hashed) >= 50

    def test_hash_password_different_salts(self):
        """Test same password produces different hashes (due to salt)."""
        password = "mysecretpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verifying correct password returns True."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password returns False."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        result = verify_password("wrongpassword", hashed)

        assert result is False

    def test_verify_password_case_sensitive(self):
        """Test password verification is case sensitive."""
        password = "MyPassword"
        hashed = hash_password(password)

        assert verify_password("MyPassword", hashed) is True
        assert verify_password("mypassword", hashed) is False
        assert verify_password("MYPASSWORD", hashed) is False

    def test_hash_empty_password(self):
        """Test hashing empty password works."""
        password = ""
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password("", hashed) is True

    def test_hash_unicode_password(self):
        """Test hashing unicode password works."""
        password = "密码🔐"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_hash_long_password(self):
        """Test hashing very long password (bcrypt has 72 byte limit)."""
        # Create a password longer than 72 bytes
        password = "a" * 100
        hashed = hash_password(password)

        # Should still verify correctly
        assert verify_password(password, hashed) is True

    def test_verify_with_special_characters(self):
        """Test password with special characters."""
        password = "p@$$w0rd!#%^&*()_+-=[]{}|;':\",./<>?"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True


class TestSanitizeFilePathDifferentDrives:
    """Tests for sanitize_file_path with different drives (covers line 98)."""

    def test_different_drives_raises_error(self):
        """Test paths on different drives raise ValidationError (covers lines 96-101)."""
        import platform

        if platform.system() != "Windows":
            pytest.skip("This test is Windows-specific")

        # On Windows, paths on different drives should raise ValueError -> ValidationError
        with pytest.raises(ValidationError) as exc_info:
            sanitize_file_path("D:\\some\\file.txt", "C:\\base\\dir")

        assert "invalid" in str(exc_info.value).lower() or "path" in str(exc_info.value).lower()

    def test_commonpath_value_error(self):
        """Test that ValueError from commonpath is caught (covers lines 96-101)."""
        from unittest.mock import patch

        with patch("os.path.commonpath") as mock_commonpath:
            mock_commonpath.side_effect = ValueError("Paths on different drives")

            with pytest.raises(ValidationError) as exc_info:
                sanitize_file_path("file.txt", "/base/dir")

            assert "invalid" in str(exc_info.value).lower() or "path" in str(exc_info.value).lower()


class TestSanitizeFilenameExtensionTruncation:
    """Tests for sanitize_filename extension handling (covers line 155)."""

    def test_truncation_without_extension_preservation(self):
        """Test filename truncation when extension is too long (covers line 155)."""
        # Create a filename with a very long 'extension' (more than 10 chars)
        long_extension = "a" * 200 + ".verylongextensionover10chars"
        result = sanitize_filename(long_extension, max_length=50)

        # Should truncate without preserving the extension since it's > 10 chars
        assert len(result) <= 50

    def test_truncation_no_extension(self):
        """Test filename truncation when there's no extension."""
        # Filename without any extension
        long_name = "a" * 300
        result = sanitize_filename(long_name, max_length=100)

        assert len(result) <= 100
        assert "." not in result

    def test_truncation_preserves_short_extension(self):
        """Test that short extensions are preserved during truncation."""
        # Long name with short extension
        long_name = "a" * 300 + ".py"
        result = sanitize_filename(long_name, max_length=50)

        assert len(result) <= 50
        assert result.endswith(".py")
