"""
Tests for utility modules.
"""

from datetime import datetime

from backend.utils.formatters import format_bytes, format_datetime, format_duration, truncate_string
from backend.utils.id_generator import generate_id, generate_timestamp_id, generate_uuid
from backend.utils.security import hash_password, verify_password
from backend.utils.validators import validate_email, validate_project_name, validate_url


class TestIdGenerator:
    """Tests for ID generator utilities."""

    def test_generate_uuid(self):
        """Test UUID generation."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()

        assert isinstance(uuid1, str)
        assert len(uuid1) == 36  # Standard UUID length
        assert uuid1 != uuid2  # Should be unique

    def test_generate_id_without_prefix(self):
        """Test ID generation without prefix."""
        id1 = generate_id()

        assert isinstance(id1, str)
        assert len(id1) == 12  # 12 hex characters

    def test_generate_id_with_prefix(self):
        """Test ID generation with prefix."""
        id1 = generate_id("project")

        assert id1.startswith("project-")
        assert len(id1) == 20  # "project-" + 12 chars

    def test_generate_timestamp_id(self):
        """Test timestamp ID generation."""
        id1 = generate_timestamp_id("task")

        assert id1.startswith("task-")
        # Format: task-YYYYMMDDHHMMSS-xxxxxxxx (variable length)
        assert len(id1) >= 28

    def test_generate_timestamp_id_without_prefix(self):
        """Test timestamp ID generation without prefix (covers line 52)."""
        id1 = generate_timestamp_id()

        # Format: YYYYMMDDHHMMSS-xxxxxxxx (without prefix)
        assert "-" in id1
        assert not id1.startswith("-")  # Should not start with hyphen
        parts = id1.split("-")
        assert len(parts) == 2  # timestamp-uuid
        assert len(parts[0]) == 14  # YYYYMMDDHHMMSS


class TestValidators:
    """Tests for validation utilities."""

    def test_validate_email_valid(self):
        """Test valid email validation."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.co.uk") is True

    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
        assert validate_email("") is False

    def test_validate_url_valid(self):
        """Test valid URL validation."""
        assert validate_url("http://example.com") is True
        assert validate_url("https://example.com/path") is True

    def test_validate_url_invalid(self):
        """Test invalid URL validation."""
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is False

    def test_validate_url_non_string(self):
        """Test URL validation with non-string input (covers line 51)."""
        assert validate_url(None) is False
        assert validate_url(123) is False
        assert validate_url([]) is False

    def test_validate_url_empty(self):
        """Test URL validation with empty string (covers line 51)."""
        assert validate_url("") is False

    def test_validate_project_name_valid(self):
        """Test valid project name."""
        is_valid, error = validate_project_name("My Project")
        assert is_valid is True
        assert error is None

    def test_validate_project_name_too_short(self):
        """Test project name too short."""
        is_valid, error = validate_project_name("ab")
        assert is_valid is False
        assert "at least 3 characters" in error

    def test_validate_project_name_empty(self):
        """Test empty project name."""
        is_valid, error = validate_project_name("")
        assert is_valid is False
        assert "required" in error

    def test_validate_project_name_too_long(self):
        """Test project name that exceeds max length (covers line 70)."""
        long_name = "a" * 101  # Over 100 characters
        is_valid, error = validate_project_name(long_name)

        assert is_valid is False
        assert "less than 100" in error


class TestFormatters:
    """Tests for formatting utilities."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime(dt)

        assert isinstance(result, str)
        assert "2024-01-15" in result

    def test_format_datetime_none(self):
        """Test formatting None datetime."""
        result = format_datetime(None)
        assert result is None

    def test_format_duration_seconds(self):
        """Test duration formatting in seconds."""
        assert format_duration(45) == "45.0s"

    def test_format_duration_minutes(self):
        """Test duration formatting in minutes."""
        assert format_duration(120) == "2.0m"

    def test_format_duration_hours(self):
        """Test duration formatting in hours."""
        assert format_duration(7200) == "2.0h"

    def test_format_duration_days(self):
        """Test duration formatting in days (covers lines 45-46)."""
        # 86400 seconds = 1 day
        assert format_duration(86400) == "1.0d"
        assert format_duration(172800) == "2.0d"
        assert format_duration(86400 * 7) == "7.0d"

    def test_format_bytes(self):
        """Test bytes formatting."""
        assert format_bytes(512) == "512.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"

    def test_format_bytes_gb(self):
        """Test bytes formatting for GB."""
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"

    def test_format_bytes_tb(self):
        """Test bytes formatting for TB."""
        assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_format_bytes_pb(self):
        """Test bytes formatting for PB (covers line 63)."""
        # This covers the final return statement for PB
        pb_bytes = 1024 * 1024 * 1024 * 1024 * 1024  # 1 PB
        assert format_bytes(pb_bytes) == "1.0 PB"
        # Test larger PB values
        assert format_bytes(pb_bytes * 2) == "2.0 PB"

    def test_truncate_string_short(self):
        """Test truncate_string when text is shorter than max_length (covers line 78)."""
        text = "Hello, World!"
        result = truncate_string(text, max_length=100)
        assert result == text

    def test_truncate_string_exact_length(self):
        """Test truncate_string when text equals max_length (covers line 78)."""
        text = "Hello"
        result = truncate_string(text, max_length=5)
        assert result == text

    def test_truncate_string_long(self):
        """Test truncate_string when text exceeds max_length (covers lines 79-80)."""
        text = "This is a very long string that needs to be truncated"
        result = truncate_string(text, max_length=20)
        assert len(result) == 20
        assert result.endswith("...")
        assert result == "This is a very lo..."

    def test_truncate_string_custom_suffix(self):
        """Test truncate_string with custom suffix (covers lines 78-80)."""
        text = "Hello, World! How are you?"
        result = truncate_string(text, max_length=15, suffix=">>")
        assert len(result) == 15
        assert result.endswith(">>")
        assert result == "Hello, World!>>"

    def test_truncate_string_empty_suffix(self):
        """Test truncate_string with empty suffix."""
        text = "Hello, World!"
        result = truncate_string(text, max_length=5, suffix="")
        assert result == "Hello"


class TestSecurity:
    """Tests for security utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "secret123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "secret123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "secret123"
        hashed = hash_password(password)

        assert verify_password("wrongpass", hashed) is False
