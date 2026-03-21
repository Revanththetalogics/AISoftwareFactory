"""
Tests for utility modules.
"""

from datetime import datetime

from backend.utils.formatters import format_bytes, format_datetime, format_duration
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

    def test_format_bytes(self):
        """Test bytes formatting."""
        assert format_bytes(512) == "512.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"


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
