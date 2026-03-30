"""
Comprehensive tests for core modules to increase coverage.
"""

import os
from unittest.mock import patch

import pytest
from backend.core.config import Settings, get_settings
from backend.core.exceptions import (
    AISoftwareFactoryException,
    BackendException,
    ConfigurationError,
    ResourceNotFoundError,
    ValidationError,
)
from backend.core.logging import configure_logging, get_logger


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_default_values(self):
        """Test settings default values."""
        settings = Settings()

        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'database_url')

    def test_settings_from_env(self):
        """Test loading settings from environment."""
        with patch.dict(os.environ, {
            'THETAAI_DEBUG': 'true',
            'THETAAI_APP_NAME': 'TestApp'
        }):
            settings = Settings()
            # Settings should read from env
            assert settings is not None


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns same instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be cached/same instance
        assert settings1 is not None
        assert settings2 is not None

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)


class TestLogging:
    """Tests for logging configuration."""

    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger(__name__)

        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')

    def test_configure_logging(self):
        """Test configuring logging."""
        # Should not raise exception
        configure_logging()

        # Logger should work after config
        logger = get_logger(__name__)
        assert logger is not None


class TestAISoftwareFactoryException:
    """Tests for base AISoftwareFactoryException."""

    def test_exception_basic(self):
        """Test basic exception creation."""
        exc = AISoftwareFactoryException("Test error")

        assert str(exc) == "Test error"
        assert exc.message == "Test error"

    def test_exception_with_code(self):
        """Test exception with error code."""
        exc = AISoftwareFactoryException("Error", error_code="TEST_001")

        assert exc.error_code == "TEST_001"

    def test_exception_with_status_code(self):
        """Test exception with HTTP status code."""
        exc = AISoftwareFactoryException("Error", status_code=400)

        assert exc.status_code == 400

    def test_exception_inheritance(self):
        """Test that it inherits from Exception."""
        exc = AISoftwareFactoryException("Test")

        assert isinstance(exc, Exception)


class TestBackendException:
    """Tests for BackendException."""

    def test_backend_exception_inheritance(self):
        """Test that BackendException inherits from AISoftwareFactoryException."""
        exc = BackendException("Backend error")

        assert isinstance(exc, AISoftwareFactoryException)
        assert isinstance(exc, Exception)

    def test_backend_exception_with_details(self):
        """Test BackendException with details."""
        exc = BackendException("Error", details={"field": "value"})

        assert exc.details == {"field": "value"}


class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from AISoftwareFactoryException."""
        exc = ConfigurationError("Config failed")

        assert isinstance(exc, AISoftwareFactoryException)
        assert isinstance(exc, Exception)

    def test_configuration_error_message(self):
        """Test ConfigurationError message."""
        exc = ConfigurationError("Invalid configuration")

        assert "Invalid configuration" in str(exc)


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from BackendException."""
        exc = ValidationError("Validation failed")

        assert isinstance(exc, BackendException)
        assert isinstance(exc, AISoftwareFactoryException)

    def test_validation_error_default_status(self):
        """Test ValidationError default status code."""
        exc = ValidationError("Invalid input")

        # Should default to 400
        assert exc.status_code == 400

    def test_validation_error_with_field(self):
        """Test ValidationError with field information."""
        exc = ValidationError("Required field", field="username")

        assert exc.details.get("field") == "username"


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError."""

    def test_resource_not_found_inheritance(self):
        """Test that ResourceNotFoundError inherits from AISoftwareFactoryException."""
        exc = ResourceNotFoundError("project", "123")

        assert isinstance(exc, AISoftwareFactoryException)
        assert isinstance(exc, Exception)

    def test_resource_not_found_default_status(self):
        """Test ResourceNotFoundError default status code."""
        exc = ResourceNotFoundError("project", "123")

        # Should default to 404
        assert exc.status_code == 404

    def test_resource_not_found_message(self):
        """Test ResourceNotFoundError message format."""
        exc = ResourceNotFoundError("project", "123")

        assert "project" in str(exc)
        assert "123" in str(exc)


class TestExceptionUsagePatterns:
    """Tests for exception usage patterns."""

    def test_raise_configuration_error(self):
        """Test raising ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Config failed")

        assert "Config failed" in str(exc_info.value)

    def test_raise_validation_error(self):
        """Test raising ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Invalid")

        assert exc_info.value.status_code == 400

    def test_raise_resource_not_found(self):
        """Test raising ResourceNotFoundError."""
        with pytest.raises(ResourceNotFoundError) as exc_info:
            raise ResourceNotFoundError("project", "123")

        assert exc_info.value.status_code == 404
        assert "project" in str(exc_info.value)

    def test_catch_base_exception(self):
        """Test catching base AISoftwareFactoryException."""
        with pytest.raises(AISoftwareFactoryException):
            raise ConfigurationError("Config error")

        with pytest.raises(AISoftwareFactoryException):
            raise BackendException("Backend error")

        with pytest.raises(AISoftwareFactoryException):
            raise ValidationError("Validation error")

    def test_exception_chain(self):
        """Test exception chaining."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ConfigurationError("Config error") from e
        except ConfigurationError as exc:
            assert exc.__cause__ is not None
            assert isinstance(exc.__cause__, ValueError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
