"""
Tests for validation utilities in backend/utils/validation.py.

Tests cover:
- validate_url_safe(): SSRF protection with blocked IP ranges
- validate_url_format(): URL format validation
- sanitize_input(): Input sanitization against XSS and injection
- is_ip_in_blocked_range(): IP range blocking
- validate_pattern(): Pattern matching validation
- batch_validate_fields(): Batch field validation
- Pydantic models: SecureProjectCreate, SecureDeploymentRequest
"""

from unittest.mock import patch

import pytest

from backend.core.exceptions import ValidationError
from backend.utils.validation import (
    RateLimitConfig,
    SecureDeploymentRequest,
    SecureProjectCreate,
    batch_validate_fields,
    is_ip_in_blocked_range,
    sanitize_input,
    validate_pattern,
    validate_url_format,
    validate_url_safe,
)


class TestSanitizeInput:
    """Tests for sanitize_input() function."""

    def test_normal_text_passes(self):
        """Test normal text passes through."""
        result = sanitize_input("Hello World")
        assert result == "Hello World"

    def test_text_with_numbers(self):
        """Test text with numbers passes through."""
        result = sanitize_input("Test123 data")
        assert result == "Test123 data"

    def test_xss_script_tag_removed(self):
        """Test XSS script tag is sanitized."""
        result = sanitize_input("<script>alert('xss')</script>")

        assert "<script>" not in result
        assert "</script>" not in result
        assert "<" not in result
        assert ">" not in result

    def test_xss_event_handler_sanitized(self):
        """Test XSS event handler attributes have dangerous chars removed."""
        result = sanitize_input("<img onerror=\"alert('xss')\" src=x>")

        # The function removes <, >, ", ' - these are the dangerous injection vectors
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result
        assert "'" not in result

    def test_sql_injection_sanitized(self):
        """Test SQL injection attempts are sanitized."""
        result = sanitize_input("'; DROP TABLE users; --")

        # Single quotes and semicolons should be removed
        assert "'" not in result
        assert ";" not in result

    def test_sql_union_sanitized(self):
        """Test SQL UNION injection is sanitized."""
        result = sanitize_input("1' UNION SELECT * FROM users --")

        assert "'" not in result

    def test_double_quotes_removed(self):
        """Test double quotes are removed."""
        result = sanitize_input('test "quoted" text')

        assert '"' not in result

    def test_backticks_removed(self):
        """Test backticks are removed."""
        result = sanitize_input("test `command` injection")

        assert "`" not in result

    def test_directory_traversal_removed(self):
        """Test directory traversal sequences are removed."""
        result = sanitize_input("../../../etc/passwd")

        assert "../" not in result

    def test_max_length_enforced(self):
        """Test max length is enforced."""
        long_input = "a" * 2000

        with pytest.raises(ValidationError) as exc_info:
            sanitize_input(long_input, max_length=1000)

        assert "maximum length" in str(exc_info.value).lower()

    def test_custom_max_length(self):
        """Test custom max length is respected."""
        long_input = "a" * 100

        with pytest.raises(ValidationError):
            sanitize_input(long_input, max_length=50)

    def test_non_string_raises_error(self):
        """Test non-string input raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_input(123)

        assert "string" in str(exc_info.value).lower()

    def test_none_input_raises_error(self):
        """Test None input raises ValidationError."""
        with pytest.raises(ValidationError):
            sanitize_input(None)

    def test_whitespace_trimmed(self):
        """Test leading and trailing whitespace is trimmed."""
        result = sanitize_input("  hello world  ")
        assert result == "hello world"

    def test_allowed_punctuation(self):
        """Test allowed punctuation passes through."""
        result = sanitize_input("Hello, World! How are you?")
        # Commas, exclamation marks, question marks should be allowed
        assert "," in result
        assert "!" in result
        assert "?" in result


class TestValidateUrlFormat:
    """Tests for validate_url_format() function."""

    def test_valid_http_url(self):
        """Test valid HTTP URL passes."""
        assert validate_url_format("http://example.com") is True

    def test_valid_https_url(self):
        """Test valid HTTPS URL passes."""
        assert validate_url_format("https://example.com") is True

    def test_valid_url_with_path(self):
        """Test URL with path passes."""
        assert validate_url_format("https://example.com/path/to/resource") is True

    def test_valid_url_with_query(self):
        """Test URL with query string passes."""
        assert validate_url_format("https://example.com?query=value") is True

    def test_localhost_blocked(self):
        """Test localhost is blocked."""
        assert validate_url_format("http://localhost") is False
        assert validate_url_format("http://localhost:8080") is False

    def test_loopback_ip_blocked(self):
        """Test 127.0.0.1 loopback is blocked."""
        assert validate_url_format("http://127.0.0.1") is False
        assert validate_url_format("http://127.0.0.1:8080/path") is False

    def test_ipv6_loopback_blocked(self):
        """Test IPv6 loopback ::1 is blocked."""
        assert validate_url_format("http://[::1]") is False

    def test_private_class_a_blocked(self):
        """Test private Class A (10.x.x.x) is blocked."""
        assert validate_url_format("http://10.0.0.1") is False
        assert validate_url_format("http://10.255.255.255") is False

    def test_private_class_b_blocked(self):
        """Test private Class B (172.16-31.x.x) is blocked."""
        assert validate_url_format("http://172.16.0.1") is False
        assert validate_url_format("http://172.31.255.255") is False

    def test_private_class_c_blocked(self):
        """Test private Class C (192.168.x.x) is blocked."""
        assert validate_url_format("http://192.168.0.1") is False
        assert validate_url_format("http://192.168.1.100") is False

    def test_ftp_scheme_rejected(self):
        """Test FTP scheme is rejected."""
        assert validate_url_format("ftp://example.com") is False

    def test_file_scheme_rejected(self):
        """Test file:// scheme is rejected."""
        assert validate_url_format("file:///etc/passwd") is False

    def test_no_scheme_rejected(self):
        """Test URL without scheme is rejected."""
        assert validate_url_format("example.com") is False

    def test_empty_url_rejected(self):
        """Test empty URL is rejected."""
        assert validate_url_format("") is False

    def test_invalid_url_rejected(self):
        """Test invalid URL is rejected."""
        assert validate_url_format("not a url") is False


class TestValidateUrlSafe:
    """Tests for validate_url_safe() SSRF protection function."""

    def test_valid_external_url(self):
        """Test valid external URL passes."""
        # Note: This may do actual DNS resolution
        assert validate_url_safe("https://www.google.com") is True

    def test_localhost_blocked(self):
        """Test localhost variants are blocked."""
        assert validate_url_safe("http://localhost") is False
        assert validate_url_safe("http://localhost:8080") is False
        assert validate_url_safe("http://localhost.localdomain") is False

    def test_loopback_blocked(self):
        """Test loopback addresses are blocked via DNS."""
        # When 127.0.0.1 is resolved, it should be blocked
        assert validate_url_safe("http://127.0.0.1") is False

    @patch("backend.utils.validation.socket.getaddrinfo")
    def test_dns_resolving_to_private_ip_blocked(self, mock_getaddrinfo):
        """Test URL resolving to private IP is blocked."""
        # Mock DNS to return a private IP
        mock_getaddrinfo.return_value = [(2, 1, 6, "", ("10.0.0.1", 80))]

        result = validate_url_safe("http://internal.example.com")

        assert result is False

    @patch("backend.utils.validation.socket.getaddrinfo")
    def test_dns_resolving_to_localhost_blocked(self, mock_getaddrinfo):
        """Test URL resolving to 127.0.0.1 is blocked."""
        mock_getaddrinfo.return_value = [(2, 1, 6, "", ("127.0.0.1", 80))]

        result = validate_url_safe("http://attacker-controlled.com")

        assert result is False

    @patch("backend.utils.validation.socket.getaddrinfo")
    def test_dns_resolving_to_link_local_blocked(self, mock_getaddrinfo):
        """Test URL resolving to link-local IP (169.254.x.x) is blocked."""
        mock_getaddrinfo.return_value = [
            (2, 1, 6, "", ("169.254.169.254", 80))  # AWS metadata endpoint
        ]

        result = validate_url_safe("http://metadata.example.com")

        assert result is False

    @patch("backend.utils.validation.socket.getaddrinfo")
    def test_dns_resolving_to_ipv6_loopback_blocked(self, mock_getaddrinfo):
        """Test URL resolving to IPv6 loopback is blocked."""
        mock_getaddrinfo.return_value = [(10, 1, 6, "", ("::1", 80, 0, 0))]

        result = validate_url_safe("http://ipv6-loopback.example.com")

        assert result is False

    def test_no_scheme_rejected(self):
        """Test URL without scheme is rejected."""
        assert validate_url_safe("example.com") is False

    def test_empty_url_rejected(self):
        """Test empty URL is rejected."""
        assert validate_url_safe("") is False

    def test_missing_hostname_rejected(self):
        """Test URL without hostname is rejected."""
        assert validate_url_safe("http://") is False

    def test_ftp_scheme_rejected(self):
        """Test FTP scheme is rejected."""
        assert validate_url_safe("ftp://example.com") is False


class TestIsIpInBlockedRange:
    """Tests for is_ip_in_blocked_range() function."""

    def test_private_class_a_blocked(self):
        """Test Class A private IPs are blocked."""
        assert is_ip_in_blocked_range("10.0.0.1") is True
        assert is_ip_in_blocked_range("10.255.255.255") is True

    def test_private_class_b_blocked(self):
        """Test Class B private IPs are blocked."""
        assert is_ip_in_blocked_range("172.16.0.1") is True
        assert is_ip_in_blocked_range("172.31.255.255") is True

    def test_private_class_c_blocked(self):
        """Test Class C private IPs are blocked."""
        assert is_ip_in_blocked_range("192.168.0.1") is True
        assert is_ip_in_blocked_range("192.168.255.255") is True

    def test_loopback_blocked(self):
        """Test loopback addresses are blocked."""
        assert is_ip_in_blocked_range("127.0.0.1") is True
        assert is_ip_in_blocked_range("127.255.255.255") is True

    def test_link_local_blocked(self):
        """Test link-local addresses are blocked."""
        assert is_ip_in_blocked_range("169.254.0.1") is True
        assert is_ip_in_blocked_range("169.254.169.254") is True

    def test_ipv6_loopback_blocked(self):
        """Test IPv6 loopback is blocked."""
        assert is_ip_in_blocked_range("::1") is True

    def test_public_ip_not_blocked(self):
        """Test public IPs are not blocked."""
        assert is_ip_in_blocked_range("8.8.8.8") is False
        assert is_ip_in_blocked_range("1.1.1.1") is False
        assert is_ip_in_blocked_range("93.184.216.34") is False  # example.com

    def test_invalid_ip_returns_false(self):
        """Test invalid IP returns False."""
        assert is_ip_in_blocked_range("not-an-ip") is False
        assert is_ip_in_blocked_range("") is False


class TestValidatePattern:
    """Tests for validate_pattern() function."""

    def test_valid_project_name(self):
        """Test valid project names match pattern."""
        assert validate_pattern("MyProject", "project_name") is True
        assert validate_pattern("my-project", "project_name") is True
        assert validate_pattern("project_123", "project_name") is True
        assert validate_pattern("Project 1.0", "project_name") is True

    def test_invalid_project_name(self):
        """Test invalid project names don't match."""
        # Special characters not allowed
        assert validate_pattern("project@name", "project_name") is False

    def test_valid_version(self):
        """Test valid semantic versions match pattern."""
        assert validate_pattern("1.0.0", "version") is True
        assert validate_pattern("2.3.4", "version") is True
        assert validate_pattern("1.0.0-alpha", "version") is True
        assert validate_pattern("10.20.30-beta1", "version") is True

    def test_invalid_version(self):
        """Test invalid versions don't match."""
        assert validate_pattern("1.0", "version") is False
        assert validate_pattern("v1.0.0", "version") is False

    def test_valid_identifier(self):
        """Test valid identifiers match pattern."""
        assert validate_pattern("my-id-123", "identifier") is True
        assert validate_pattern("user_id", "identifier") is True

    def test_valid_environment(self):
        """Test valid environment values match."""
        assert validate_pattern("dev", "environment") is True
        assert validate_pattern("staging", "environment") is True
        assert validate_pattern("production", "environment") is True

    def test_invalid_environment(self):
        """Test invalid environment values don't match."""
        assert validate_pattern("test", "environment") is False
        assert validate_pattern("prod", "environment") is False

    def test_unknown_pattern_returns_false(self):
        """Test unknown pattern name returns False."""
        assert validate_pattern("value", "unknown_pattern") is False


class TestBatchValidateFields:
    """Tests for batch_validate_fields() function."""

    def test_all_valid_fields(self):
        """Test all valid fields return no errors."""
        data = {
            "name": "MyProject",
            "version": "1.0.0",
            "environment": "dev",
        }
        validations = {
            "name": "project_name",
            "version": "version",
            "environment": "environment",
        }

        errors = batch_validate_fields(data, validations)

        assert errors == []

    def test_single_invalid_field(self):
        """Test single invalid field returns error."""
        data = {
            "name": "MyProject",
            "version": "invalid-version",
        }
        validations = {
            "name": "project_name",
            "version": "version",
        }

        errors = batch_validate_fields(data, validations)

        assert len(errors) == 1
        assert "version" in errors[0].lower()

    def test_multiple_invalid_fields(self):
        """Test multiple invalid fields return multiple errors."""
        data = {
            "name": "project@invalid",
            "version": "bad",
            "environment": "invalid-env",
        }
        validations = {
            "name": "project_name",
            "version": "version",
            "environment": "environment",
        }

        errors = batch_validate_fields(data, validations)

        # Should have errors for name, version, and environment
        assert len(errors) >= 2

    def test_missing_field_skipped(self):
        """Test missing fields are skipped."""
        data = {
            "name": "MyProject",
            # version is missing
        }
        validations = {
            "name": "project_name",
            "version": "version",
        }

        errors = batch_validate_fields(data, validations)

        assert errors == []

    def test_non_string_field_skipped(self):
        """Test non-string fields are skipped."""
        data = {
            "name": "MyProject",
            "count": 123,  # Non-string
        }
        validations = {
            "name": "project_name",
            "count": "identifier",
        }

        errors = batch_validate_fields(data, validations)

        # Should not error on non-string field
        assert errors == []


class TestSecureProjectCreate:
    """Tests for SecureProjectCreate Pydantic model."""

    def test_valid_project(self):
        """Test valid project data passes validation."""
        project = SecureProjectCreate(
            name="My Project",
            description="A test project",
        )

        assert project.name == "My Project"
        assert project.description == "A test project"

    def test_project_with_requirements(self):
        """Test project with requirements."""
        project = SecureProjectCreate(
            name="My Project",
            description="A test project",
            requirements="Some requirements",
        )

        assert project.requirements == "Some requirements"

    def test_name_too_short_rejected(self):
        """Test empty name is rejected."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            SecureProjectCreate(
                name="",
                description="Test",
            )

    def test_description_too_short_rejected(self):
        """Test empty description is rejected."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            SecureProjectCreate(
                name="Project",
                description="",
            )


class TestSecureDeploymentRequest:
    """Tests for SecureDeploymentRequest Pydantic model."""

    def test_valid_deployment(self):
        """Test valid deployment request passes."""
        deployment = SecureDeploymentRequest(
            project_id="proj-123",
            environment="production",
            version="1.0.0",
        )

        assert deployment.project_id == "proj-123"
        assert deployment.environment == "production"
        assert deployment.version == "1.0.0"

    def test_valid_environments(self):
        """Test all valid environment values."""
        for env in ["dev", "staging", "production"]:
            deployment = SecureDeploymentRequest(
                project_id="proj-123",
                environment=env,
                version="1.0.0",
            )
            assert deployment.environment == env

    def test_invalid_environment_rejected(self):
        """Test invalid environment is rejected."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            SecureDeploymentRequest(
                project_id="proj-123",
                environment="test",  # Invalid
                version="1.0.0",
            )

    def test_invalid_version_format_rejected(self):
        """Test invalid version format is rejected."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            SecureDeploymentRequest(
                project_id="proj-123",
                environment="dev",
                version="invalid",  # Invalid format
            )

    def test_valid_version_with_suffix(self):
        """Test version with alpha/beta suffix passes."""
        deployment = SecureDeploymentRequest(
            project_id="proj-123",
            environment="dev",
            version="1.0.0-alpha",
        )

        assert deployment.version == "1.0.0-alpha"


class TestRateLimitConfig:
    """Tests for RateLimitConfig Pydantic model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        config = RateLimitConfig()

        assert config.requests_per_minute == 60
        assert config.requests_per_hour == 1000
        assert config.burst_limit == 10

    def test_custom_values(self):
        """Test custom values are accepted."""
        config = RateLimitConfig(
            requests_per_minute=100,
            requests_per_hour=5000,
            burst_limit=50,
        )

        assert config.requests_per_minute == 100
        assert config.requests_per_hour == 5000
        assert config.burst_limit == 50

    def test_min_boundary(self):
        """Test minimum values are accepted."""
        config = RateLimitConfig(
            requests_per_minute=1,
            requests_per_hour=1,
            burst_limit=1,
        )

        assert config.requests_per_minute == 1

    def test_below_min_rejected(self):
        """Test values below minimum are rejected."""
        from pydantic import ValidationError as PydanticValidationError

        with pytest.raises(PydanticValidationError):
            RateLimitConfig(requests_per_minute=0)


class TestValidateEmailFormatException:
    """Tests for validate_email_format exception handling (covers line 84-86)."""

    def test_validate_email_valid_returns_true(self):
        """Test that valid email returns True (covers line 84)."""
        from backend.utils.validation import validate_email_format

        result = validate_email_format("test@example.com")
        assert result is True

        result = validate_email_format("user.name@domain.co.uk")
        assert result is True

    def test_validate_email_invalid_returns_false(self):
        """Test that invalid email returns False via exception (covers lines 85-86)."""
        from backend.utils.validation import validate_email_format

        # These should trigger the exception path and return False
        result = validate_email_format("not-an-email")
        assert result is False

        result = validate_email_format("@missing-local.com")
        assert result is False

        result = validate_email_format("missing-at.com")
        assert result is False


class TestValidateUrlFormatException:
    """Tests for validate_url_format exception handling (covers lines 115-116)."""

    def test_validate_url_format_exception_returns_false(self):
        """Test that exception in URL format validation returns False (covers lines 115-116)."""
        from backend.utils.validation import validate_url_format

        # Mock urlparse to raise an exception
        with patch("backend.utils.validation.urlparse") as mock_urlparse:
            mock_urlparse.side_effect = Exception("Parse error")
            result = validate_url_format("http://example.com")

        assert result is False


class TestValidateUrlSafeException:
    """Tests for validate_url_safe outer exception handling (covers lines 187-188)."""

    def test_validate_url_safe_outer_exception_returns_false(self):
        """Test that outer exception in URL safe validation returns False (covers lines 187-188)."""
        from backend.utils.validation import validate_url_safe

        # Mock urlparse to raise an unexpected exception
        with patch("backend.utils.validation.urlparse") as mock_urlparse:
            mock_urlparse.side_effect = Exception("Unexpected error")
            result = validate_url_safe("http://example.com")

        assert result is False

    @patch("backend.utils.validation.socket.getaddrinfo")
    def test_validate_url_safe_invalid_ip_format_continues(self, mock_getaddrinfo):
        """Test URL safe validation continues when IP format is invalid (covers line 173-175)."""
        # Return an address info with invalid IP format
        mock_getaddrinfo.return_value = [(2, 1, 6, "", ("not-a-valid-ip", 80))]

        result = validate_url_safe("http://external.example.com")

        # Should return True since invalid IP is skipped and no blocked IP found
        assert result is True
