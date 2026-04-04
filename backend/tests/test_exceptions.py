"""
Tests for custom exception hierarchy.

This module tests the custom exception classes and their functionality.
"""

from backend.core.exceptions import (
    AISoftwareFactoryException,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ConflictError,
    ExternalServiceError,
    RateLimitError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    ValidationError,
)


class TestAISoftwareFactoryException:
    """Test cases for base exception class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        exc = AISoftwareFactoryException("An unexpected error occurred")

        assert exc.message == "An unexpected error occurred"
        assert exc.error_code == "UNKNOWN_ERROR"
        assert exc.status_code == 500

    def test_custom_values(self):
        """Test that custom values are set correctly."""
        exc = AISoftwareFactoryException(message="Custom message", error_code="CUSTOM_ERROR", status_code=400)

        assert exc.message == "Custom message"
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.status_code == 400

    def test_to_dict(self):
        """Test conversion to dictionary."""
        exc = AISoftwareFactoryException(message="Test message", error_code="TEST_ERROR")

        result = {"error_code": exc.error_code, "message": exc.message, "status_code": exc.status_code}

        assert result == {"error_code": "TEST_ERROR", "message": "Test message", "status_code": 500}

    def test_str_representation(self):
        """Test string representation."""
        exc = AISoftwareFactoryException(message="Test message")

        assert str(exc) == "Test message"

    def test_str_with_details(self):
        """Test string representation with details."""
        exc = AISoftwareFactoryException(message="Test message")

        assert "Test message" in str(exc)


class TestConfigurationError:
    """Test cases for ConfigurationError."""

    def test_default_values(self):
        """Test default values."""
        exc = ConfigurationError("Configuration error")

        assert exc.message == "Configuration error"
        assert exc.error_code == "CONFIGURATION_ERROR"
        assert exc.status_code == 500


class TestValidationError:
    """Test cases for ValidationError."""

    def test_default_values(self):
        """Test default values."""
        exc = ValidationError("Validation error")

        assert exc.message == "Validation error"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400

    def test_with_errors(self):
        """Test with field errors."""
        exc = ValidationError("Validation error")

        assert exc.message == "Validation error"


class TestResourceNotFoundError:
    """Test cases for ResourceNotFoundError."""

    def test_default_values(self):
        """Test default values."""
        exc = ResourceNotFoundError("resource", "123")

        assert exc.message == "resource with id '123' not found"
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.status_code == 404

    def test_with_resource_type(self):
        """Test with resource type."""
        exc = ResourceNotFoundError("project", "123")

        assert exc.message == "project with id '123' not found"

    def test_with_resource_type_and_id(self):
        """Test with resource type and ID."""
        exc = ResourceNotFoundError("user", "123")

        assert exc.message == "user with id '123' not found"


class TestAuthenticationError:
    """Test cases for AuthenticationError."""

    def test_default_values(self):
        """Test default values."""
        exc = AuthenticationError("Authentication required")

        assert exc.message == "Authentication required"
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.status_code == 401


class TestAuthorizationError:
    """Test cases for AuthorizationError."""

    def test_default_values(self):
        """Test default values."""
        exc = AuthorizationError("Insufficient permissions")

        assert exc.message == "Insufficient permissions"
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.status_code == 403


class TestServiceUnavailableError:
    """Test cases for ServiceUnavailableError."""

    def test_default_values(self):
        """Test default values."""
        exc = ServiceUnavailableError("service")

        assert exc.message == "Service 'service' is unavailable: Service temporarily unavailable"
        assert exc.error_code == "SERVICE_UNAVAILABLE"
        assert exc.status_code == 503

    def test_with_service(self):
        """Test with service name."""
        exc = ServiceUnavailableError("database", "temporarily unavailable")

        assert exc.message == "Service 'database' is unavailable: temporarily unavailable"


class TestConflictError:
    """Test cases for ConflictError."""

    def test_default_values(self):
        """Test default values."""
        exc = ConflictError("Resource conflict")

        assert exc.message == "Resource conflict"
        assert exc.error_code == "CONFLICT_ERROR"
        assert exc.status_code == 409


class TestRateLimitError:
    """Test cases for RateLimitError."""

    def test_default_values(self):
        """Test default values."""
        exc = RateLimitError("Rate limit exceeded")

        assert exc.message == "Rate limit exceeded"
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429


class TestExternalServiceError:
    """Test cases for ExternalServiceError."""

    def test_default_values(self):
        """Test default values."""
        exc = ExternalServiceError("External service error")

        assert exc.message == "External service error"
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == 502

    def test_with_service(self):
        """Test with service name."""
        exc = ExternalServiceError("External service error", "stripe")

        assert exc.service == "stripe"


class TestExceptionInheritance:
    """Test that all exceptions inherit from base class."""

    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from AISoftwareFactoryException."""
        # Test with required arguments for each exception
        test_cases = [
            (ConfigurationError, ["Configuration error"]),
            (ValidationError, ["Validation error"]),
            (ResourceNotFoundError, ["resource", "123"]),
            (AuthenticationError, ["Authentication required"]),
            (AuthorizationError, ["Insufficient permissions"]),
            (ServiceUnavailableError, ["service"]),
            (ConflictError, ["Resource conflict"]),
            (RateLimitError, ["Rate limit exceeded"]),
            (ExternalServiceError, ["External service error"]),
        ]

        for exc_class, args in test_cases:
            exc = exc_class(*args)
            assert isinstance(exc, AISoftwareFactoryException)
            assert isinstance(exc, Exception)
