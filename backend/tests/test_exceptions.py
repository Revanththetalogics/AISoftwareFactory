"""
Tests for custom exception hierarchy.

This module tests the custom exception classes and their functionality.
"""

import pytest

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
        exc = AISoftwareFactoryException()
        
        assert exc.message == "An unexpected error occurred"
        assert exc.error_code == "INTERNAL_ERROR"
        assert exc.status_code == 500
        assert exc.details == {}
    
    def test_custom_values(self):
        """Test that custom values are set correctly."""
        exc = AISoftwareFactoryException(
            message="Custom message",
            error_code="CUSTOM_ERROR",
            status_code=400,
            details={"key": "value"}
        )
        
        assert exc.message == "Custom message"
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.status_code == 400
        assert exc.details == {"key": "value"}
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        exc = AISoftwareFactoryException(
            message="Test message",
            error_code="TEST_ERROR",
            details={"foo": "bar"}
        )
        
        result = exc.to_dict()
        
        assert result == {
            "error_code": "TEST_ERROR",
            "message": "Test message",
            "details": {"foo": "bar"}
        }
    
    def test_str_representation(self):
        """Test string representation."""
        exc = AISoftwareFactoryException(message="Test message")
        
        assert str(exc) == "[INTERNAL_ERROR] Test message"
    
    def test_str_with_details(self):
        """Test string representation with details."""
        exc = AISoftwareFactoryException(
            message="Test message",
            details={"key": "value"}
        )
        
        assert "[INTERNAL_ERROR] Test message" in str(exc)
        assert "Details" in str(exc)


class TestConfigurationError:
    """Test cases for ConfigurationError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = ConfigurationError()
        
        assert exc.message == "Configuration error"
        assert exc.error_code == "CONFIGURATION_ERROR"
        assert exc.status_code == 500


class TestValidationError:
    """Test cases for ValidationError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = ValidationError()
        
        assert exc.message == "Validation error"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400
    
    def test_with_errors(self):
        """Test with field errors."""
        errors = [
            {"field": "email", "message": "Invalid email"},
            {"field": "name", "message": "Name is required"}
        ]
        exc = ValidationError(errors=errors)
        
        assert exc.details["errors"] == errors


class TestResourceNotFoundError:
    """Test cases for ResourceNotFoundError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = ResourceNotFoundError()
        
        assert exc.message == "Resource not found"
        assert exc.error_code == "RESOURCE_NOT_FOUND"
        assert exc.status_code == 404
    
    def test_with_resource_type(self):
        """Test with resource type."""
        exc = ResourceNotFoundError(resource_type="project")
        
        assert exc.message == "project not found"
        assert exc.details["resource_type"] == "project"
    
    def test_with_resource_type_and_id(self):
        """Test with resource type and ID."""
        exc = ResourceNotFoundError(resource_type="user", resource_id="123")
        
        assert exc.message == "user not found with id '123'"
        assert exc.details["resource_type"] == "user"
        assert exc.details["resource_id"] == "123"


class TestAuthenticationError:
    """Test cases for AuthenticationError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = AuthenticationError()
        
        assert exc.message == "Authentication failed"
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.status_code == 401


class TestAuthorizationError:
    """Test cases for AuthorizationError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = AuthorizationError()
        
        assert exc.message == "Access denied"
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.status_code == 403


class TestServiceUnavailableError:
    """Test cases for ServiceUnavailableError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = ServiceUnavailableError()
        
        assert exc.message == "Service temporarily unavailable"
        assert exc.error_code == "SERVICE_UNAVAILABLE"
        assert exc.status_code == 503
    
    def test_with_service(self):
        """Test with service name."""
        exc = ServiceUnavailableError(service="database")
        
        assert exc.message == "database is temporarily unavailable"
        assert exc.details["service"] == "database"


class TestConflictError:
    """Test cases for ConflictError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = ConflictError()
        
        assert exc.message == "Resource conflict"
        assert exc.error_code == "CONFLICT_ERROR"
        assert exc.status_code == 409


class TestRateLimitError:
    """Test cases for RateLimitError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = RateLimitError()
        
        assert exc.message == "Rate limit exceeded"
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429


class TestExternalServiceError:
    """Test cases for ExternalServiceError."""
    
    def test_default_values(self):
        """Test default values."""
        exc = ExternalServiceError()
        
        assert exc.message == "External service error"
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == 502
    
    def test_with_service(self):
        """Test with service name."""
        exc = ExternalServiceError(service="stripe")
        
        assert exc.details["service"] == "stripe"


class TestExceptionInheritance:
    """Test that all exceptions inherit from base class."""
    
    def test_all_inherit_from_base(self):
        """Test that all custom exceptions inherit from AISoftwareFactoryException."""
        exceptions = [
            ConfigurationError,
            ValidationError,
            ResourceNotFoundError,
            AuthenticationError,
            AuthorizationError,
            ServiceUnavailableError,
            ConflictError,
            RateLimitError,
            ExternalServiceError,
        ]
        
        for exc_class in exceptions:
            exc = exc_class()
            assert isinstance(exc, AISoftwareFactoryException)
            assert isinstance(exc, Exception)
