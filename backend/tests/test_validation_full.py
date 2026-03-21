"""
Comprehensive tests for validation utilities.

Covers uncovered lines in backend/utils/validation.py:
- Lines 81-86 (validate_email_format)
- Lines 115-116 (validate_url_format exceptions)
- Lines 173-183 (validate_url_safe DNS resolution edge cases)
- Lines 187-188 (validate_url_safe final exception)
- Line 238 (SecureProjectCreate name validation)
- Line 251 (SecureProjectCreate requirements validation)
- Line 267 (SecureDeploymentRequest project_id validation)
- Lines 275-279 (SecureDeploymentRequest config validation)
"""

from unittest.mock import patch

import pytest

from backend.core.exceptions import ValidationError
from backend.utils.validation import (
    VALIDATION_PATTERNS,
    SecureDeploymentRequest,
    SecureProjectCreate,
    batch_validate_fields,
    is_ip_in_blocked_range,
    sanitize_input,
    validate_email_format,
    validate_pattern,
    validate_url_format,
    validate_url_safe,
)


class TestSanitizeInput:
    """Tests for sanitize_input function."""

    def test_sanitize_valid_string(self):
        """Test sanitizing valid string."""
        result = sanitize_input("Hello World")
        assert result == "Hello World"

    def test_sanitize_with_dangerous_chars(self):
        """Test sanitizing string with dangerous characters."""
        result = sanitize_input("Hello <script>alert('xss')</script>")
        assert "<" not in result
        assert ">" not in result
        assert "'" not in result

    def test_sanitize_with_directory_traversal(self):
        """Test sanitizing string with directory traversal."""
        result = sanitize_input("../../../etc/passwd")
        assert "../" not in result

    def test_sanitize_exceeds_max_length(self):
        """Test sanitizing string exceeding max length."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input("a" * 2000, max_length=1000)
        assert "maximum length" in str(exc_info.value)

    def test_sanitize_non_string(self):
        """Test sanitizing non-string input."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input(12345)
        assert "must be a string" in str(exc_info.value)


class TestValidateEmailFormat:
    """Tests for validate_email_format function - covers lines 81-86.

    Note: The implementation was fixed to use email-validator directly
    for proper email validation in Pydantic v2.
    """

    def test_valid_email(self):
        """Test email validation with valid email."""
        result = validate_email_format("test@example.com")
        assert result is True

    def test_valid_email_with_subdomain(self):
        """Test email with subdomain."""
        result = validate_email_format("user@mail.example.com")
        assert result is True

    def test_invalid_email_no_at(self):
        """Test invalid email without @ symbol."""
        assert validate_email_format("testexample.com") is False

    def test_invalid_email_no_domain(self):
        """Test invalid email without domain."""
        assert validate_email_format("test@") is False

    def test_invalid_email_no_user(self):
        """Test invalid email without user part."""
        assert validate_email_format("@example.com") is False

    def test_invalid_email_empty(self):
        """Test empty string as email."""
        assert validate_email_format("") is False

    def test_invalid_email_special_chars(self):
        """Test invalid email with special characters."""
        assert validate_email_format("te st@example.com") is False

    def test_invalid_email_format_exception_path(self):
        """Test email validation exception path (covers lines 85-86)."""
        # Invalid email should return False without raising exception
        result = validate_email_format("not-an-email")
        assert result is False


class TestValidateUrlFormat:
    """Tests for validate_url_format function - covers lines 115-116."""

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert validate_url_format("http://example.com") is True

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert validate_url_format("https://example.com/path") is True

    def test_invalid_ftp_url(self):
        """Test invalid FTP URL."""
        assert validate_url_format("ftp://example.com") is False

    def test_localhost_url(self):
        """Test localhost URL is rejected."""
        assert validate_url_format("http://localhost/path") is False

    def test_loopback_url(self):
        """Test loopback address URL is rejected."""
        assert validate_url_format("http://127.0.0.1/path") is False

    def test_ipv6_loopback(self):
        """Test IPv6 loopback is rejected."""
        assert validate_url_format("http://[::1]/path") is False

    def test_private_ip_class_a(self):
        """Test private Class A IP is rejected."""
        assert validate_url_format("http://10.0.0.1/path") is False

    def test_private_ip_class_b(self):
        """Test private Class B IP is rejected."""
        assert validate_url_format("http://172.16.0.1/path") is False

    def test_private_ip_class_c(self):
        """Test private Class C IP is rejected."""
        assert validate_url_format("http://192.168.1.1/path") is False

    def test_invalid_url_format_exception(self):
        """Test URL format exception path (covers lines 115-116)."""
        # Malformed URL should return False
        result = validate_url_format("not-a-valid-url")
        assert result is False

    def test_url_with_invalid_scheme(self):
        """Test URL with invalid scheme."""
        assert validate_url_format("file:///etc/passwd") is False


class TestValidateUrlSafe:
    """Tests for validate_url_safe function - covers lines 173-188."""

    def test_safe_public_url(self):
        """Test safe public URL."""
        with patch('socket.getaddrinfo') as mock_dns:
            mock_dns.return_value = [(2, 1, 6, '', ('93.184.216.34', 0))]
            result = validate_url_safe("https://example.com")
            assert result is True

    def test_blocked_private_ip(self):
        """Test blocked private IP."""
        with patch('socket.getaddrinfo') as mock_dns:
            mock_dns.return_value = [(2, 1, 6, '', ('10.0.0.1', 0))]
            result = validate_url_safe("https://internal.example.com")
            assert result is False

    def test_blocked_loopback(self):
        """Test blocked loopback IP."""
        with patch('socket.getaddrinfo') as mock_dns:
            mock_dns.return_value = [(2, 1, 6, '', ('127.0.0.1', 0))]
            result = validate_url_safe("https://localhost.example.com")
            assert result is False

    def test_localhost_hostname(self):
        """Test localhost hostname is blocked."""
        result = validate_url_safe("http://localhost/path")
        assert result is False

    def test_localhost_localdomain(self):
        """Test localhost.localdomain is blocked."""
        result = validate_url_safe("http://localhost.localdomain/path")
        assert result is False

    def test_invalid_scheme(self):
        """Test invalid URL scheme."""
        result = validate_url_safe("ftp://example.com")
        assert result is False

    def test_no_hostname(self):
        """Test URL without hostname."""
        result = validate_url_safe("http:///path")
        assert result is False

    def test_dns_resolution_failure(self):
        """Test DNS resolution failure (covers lines 177-180)."""
        import socket
        with patch('socket.getaddrinfo') as mock_dns:
            mock_dns.side_effect = socket.gaierror("DNS resolution failed")
            # DNS failure should still allow URL to pass (validation at connection time)
            result = validate_url_safe("https://nonexistent.example.com")
            assert result is True

    def test_dns_timeout(self):
        """Test DNS timeout (covers lines 181-183)."""
        import socket
        with patch('socket.getaddrinfo') as mock_dns:
            mock_dns.side_effect = socket.timeout("DNS timeout")
            # DNS timeout should still allow URL to pass
            result = validate_url_safe("https://slow.example.com")
            assert result is True

    def test_invalid_ip_format_in_resolution(self):
        """Test invalid IP format during resolution (covers lines 173-175)."""
        with patch('socket.getaddrinfo') as mock_dns:
            # Return invalid IP format that can't be parsed
            mock_dns.return_value = [(2, 1, 6, '', ('not-an-ip', 0))]
            # Should handle gracefully
            result = validate_url_safe("https://weird.example.com")
            assert result is True

    def test_general_exception(self):
        """Test general exception handling (covers lines 187-188)."""
        # Test with a malformed URL that could cause parsing issues
        # The function catches all exceptions and returns False
        # Test an edge case that exercises the exception path
        result = validate_url_safe(None)  # Passing None should trigger exception
        assert result is False

    def test_multiple_ips_some_blocked(self):
        """Test URL resolving to multiple IPs with some blocked."""
        with patch('socket.getaddrinfo') as mock_dns:
            # One public, one private IP
            mock_dns.return_value = [
                (2, 1, 6, '', ('93.184.216.34', 0)),
                (2, 1, 6, '', ('10.0.0.1', 0)),  # Private
            ]
            result = validate_url_safe("https://dual.example.com")
            assert result is False


class TestIsIpInBlockedRange:
    """Tests for is_ip_in_blocked_range function."""

    def test_public_ip_not_blocked(self):
        """Test public IP is not blocked."""
        assert is_ip_in_blocked_range("8.8.8.8") is False
        assert is_ip_in_blocked_range("93.184.216.34") is False

    def test_private_class_a_blocked(self):
        """Test private Class A is blocked."""
        assert is_ip_in_blocked_range("10.0.0.1") is True
        assert is_ip_in_blocked_range("10.255.255.255") is True

    def test_private_class_b_blocked(self):
        """Test private Class B is blocked."""
        assert is_ip_in_blocked_range("172.16.0.1") is True
        assert is_ip_in_blocked_range("172.31.255.255") is True

    def test_private_class_c_blocked(self):
        """Test private Class C is blocked."""
        assert is_ip_in_blocked_range("192.168.0.1") is True
        assert is_ip_in_blocked_range("192.168.255.255") is True

    def test_loopback_blocked(self):
        """Test loopback is blocked."""
        assert is_ip_in_blocked_range("127.0.0.1") is True

    def test_link_local_blocked(self):
        """Test link-local is blocked."""
        assert is_ip_in_blocked_range("169.254.1.1") is True

    def test_invalid_ip_not_blocked(self):
        """Test invalid IP returns False."""
        assert is_ip_in_blocked_range("not-an-ip") is False

    def test_ipv6_loopback_blocked(self):
        """Test IPv6 loopback is blocked."""
        assert is_ip_in_blocked_range("::1") is True

    def test_ipv6_unique_local_blocked(self):
        """Test IPv6 unique local is blocked."""
        assert is_ip_in_blocked_range("fc00::1") is True


class TestSecureProjectCreate:
    """Tests for SecureProjectCreate model - covers lines 238, 251."""

    def test_valid_project(self):
        """Test valid project creation."""
        project = SecureProjectCreate(
            name="My Project",
            description="A test project",
            requirements="Build something cool"
        )
        assert project.name == "My Project"

    def test_name_with_dangerous_chars(self):
        """Test name validation removes dangerous characters."""
        # Note: The validator sanitizes and then validates pattern
        project = SecureProjectCreate(
            name="My_Project-1.0",
            description="Test"
        )
        assert project.name == "My_Project-1.0"

    def test_name_invalid_characters(self):
        """Test name with invalid characters (covers line 238)."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SecureProjectCreate(
                name="My@Project!",  # @ and ! are invalid after sanitization
                description="Test"
            )

    def test_description_sanitized(self):
        """Test description is sanitized."""
        project = SecureProjectCreate(
            name="My Project",
            description="A test project with <script>evil</script>"
        )
        # Dangerous characters should be removed
        assert "<" not in project.description
        assert ">" not in project.description

    def test_requirements_sanitized(self):
        """Test requirements are sanitized (covers line 251)."""
        project = SecureProjectCreate(
            name="My Project",
            description="A test project",
            requirements="Build something; DROP TABLE users;"
        )
        # Semicolon should be removed
        assert ";" not in project.requirements

    def test_requirements_none(self):
        """Test requirements can be None."""
        project = SecureProjectCreate(
            name="My Project",
            description="A test project",
            requirements=None
        )
        assert project.requirements is None


class TestSecureDeploymentRequest:
    """Tests for SecureDeploymentRequest model - covers lines 267, 275-279."""

    def test_valid_deployment(self):
        """Test valid deployment request."""
        deployment = SecureDeploymentRequest(
            project_id="my-project-123",
            environment="dev",
            version="1.0.0"
        )
        assert deployment.project_id == "my-project-123"

    def test_invalid_project_id_format(self):
        """Test invalid project ID format (covers line 267)."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SecureDeploymentRequest(
                project_id="my@project!invalid",  # Invalid characters
                environment="dev",
                version="1.0.0"
            )

    def test_valid_environments(self):
        """Test all valid environments."""
        for env in ["dev", "staging", "production"]:
            deployment = SecureDeploymentRequest(
                project_id="project-123",
                environment=env,
                version="1.0.0"
            )
            assert deployment.environment == env

    def test_invalid_environment(self):
        """Test invalid environment."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SecureDeploymentRequest(
                project_id="project-123",
                environment="invalid",
                version="1.0.0"
            )

    def test_valid_versions(self):
        """Test valid version formats."""
        valid_versions = ["1.0.0", "10.20.30", "1.0.0-alpha", "1.0.0-beta1"]
        for version in valid_versions:
            deployment = SecureDeploymentRequest(
                project_id="project-123",
                environment="dev",
                version=version
            )
            assert deployment.version == version

    def test_invalid_version(self):
        """Test invalid version format."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            SecureDeploymentRequest(
                project_id="project-123",
                environment="dev",
                version="invalid-version"
            )

    def test_config_with_sensitive_key_password(self):
        """Test config with sensitive key 'password' (covers lines 275-279)."""
        with pytest.raises(Exception) as exc_info:  # Pydantic ValidationError
            SecureDeploymentRequest(
                project_id="project-123",
                environment="dev",
                version="1.0.0",
                config={"password": "secret123"}
            )
        assert "sensitive" in str(exc_info.value).lower()

    def test_config_with_sensitive_key_secret(self):
        """Test config with sensitive key containing 'secret'."""
        with pytest.raises(Exception) as exc_info:
            SecureDeploymentRequest(
                project_id="project-123",
                environment="dev",
                version="1.0.0",
                config={"db_secret": "myvalue"}
            )
        assert "sensitive" in str(exc_info.value).lower()

    def test_config_with_sensitive_key_token(self):
        """Test config with sensitive key containing 'token'."""
        with pytest.raises(Exception) as exc_info:
            SecureDeploymentRequest(
                project_id="project-123",
                environment="dev",
                version="1.0.0",
                config={"auth_token": "mytoken"}
            )
        assert "sensitive" in str(exc_info.value).lower()

    def test_config_with_sensitive_key_api_key(self):
        """Test config with sensitive key containing 'api_key'."""
        with pytest.raises(Exception) as exc_info:
            SecureDeploymentRequest(
                project_id="project-123",
                environment="dev",
                version="1.0.0",
                config={"my_api_key": "key123"}
            )
        assert "sensitive" in str(exc_info.value).lower()

    def test_config_with_non_sensitive_keys(self):
        """Test config with non-sensitive keys is allowed."""
        deployment = SecureDeploymentRequest(
            project_id="project-123",
            environment="dev",
            version="1.0.0",
            config={
                "debug": True,
                "max_workers": 4,
                "log_level": "INFO"
            }
        )
        assert deployment.config["debug"] is True

    def test_config_none(self):
        """Test config can be None."""
        deployment = SecureDeploymentRequest(
            project_id="project-123",
            environment="dev",
            version="1.0.0",
            config=None
        )
        assert deployment.config is None


class TestValidatePattern:
    """Tests for validate_pattern function."""

    def test_valid_project_name(self):
        """Test valid project name pattern."""
        assert validate_pattern("My Project 1.0", "project_name") is True

    def test_invalid_project_name(self):
        """Test invalid project name pattern."""
        assert validate_pattern("My@Project!", "project_name") is False

    def test_valid_version(self):
        """Test valid version pattern."""
        assert validate_pattern("1.0.0", "version") is True
        assert validate_pattern("1.0.0-alpha", "version") is True

    def test_invalid_version(self):
        """Test invalid version pattern."""
        assert validate_pattern("1.0", "version") is False

    def test_valid_identifier(self):
        """Test valid identifier pattern."""
        assert validate_pattern("my-project-123", "identifier") is True

    def test_invalid_identifier(self):
        """Test invalid identifier pattern."""
        assert validate_pattern("my project", "identifier") is False

    def test_valid_environment(self):
        """Test valid environment pattern."""
        assert validate_pattern("dev", "environment") is True
        assert validate_pattern("staging", "environment") is True
        assert validate_pattern("production", "environment") is True

    def test_invalid_environment(self):
        """Test invalid environment pattern."""
        assert validate_pattern("test", "environment") is False

    def test_nonexistent_pattern(self):
        """Test with non-existent pattern name."""
        assert validate_pattern("anything", "nonexistent_pattern") is False


class TestBatchValidateFields:
    """Tests for batch_validate_fields function."""

    def test_all_valid(self):
        """Test all fields valid."""
        data = {
            "project_name": "My Project",
            "version": "1.0.0",
            "environment": "dev"
        }
        validations = {
            "project_name": "project_name",
            "version": "version",
            "environment": "environment"
        }

        errors = batch_validate_fields(data, validations)
        assert errors == []

    def test_some_invalid(self):
        """Test some fields invalid."""
        data = {
            "project_name": "My@Invalid!",
            "version": "not-a-version",
            "environment": "dev"
        }
        validations = {
            "project_name": "project_name",
            "version": "version",
            "environment": "environment"
        }

        errors = batch_validate_fields(data, validations)
        assert len(errors) == 2
        assert any("project_name" in e for e in errors)
        assert any("version" in e for e in errors)

    def test_missing_field(self):
        """Test missing field is skipped."""
        data = {
            "project_name": "My Project"
        }
        validations = {
            "project_name": "project_name",
            "version": "version"  # Not in data
        }

        errors = batch_validate_fields(data, validations)
        assert errors == []

    def test_non_string_field(self):
        """Test non-string field is skipped."""
        data = {
            "project_name": "My Project",
            "count": 123  # Not a string
        }
        validations = {
            "project_name": "project_name",
            "count": "identifier"
        }

        errors = batch_validate_fields(data, validations)
        assert errors == []

    def test_empty_data(self):
        """Test with empty data."""
        errors = batch_validate_fields({}, {"field": "pattern"})
        assert errors == []

    def test_empty_validations(self):
        """Test with empty validations."""
        errors = batch_validate_fields({"field": "value"}, {})
        assert errors == []


class TestValidationPatterns:
    """Tests for VALIDATION_PATTERNS dictionary."""

    def test_patterns_exist(self):
        """Test all expected patterns exist."""
        expected_patterns = [
            'project_name',
            'version',
            'identifier',
            'environment',
            'email'
        ]
        for pattern_name in expected_patterns:
            assert pattern_name in VALIDATION_PATTERNS
