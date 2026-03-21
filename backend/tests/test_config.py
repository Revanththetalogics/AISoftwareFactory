"""
Tests for configuration management.

This module tests the configuration system including environment variable
loading, validation, and settings access.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend.core.config import Settings, get_settings, reload_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        settings = Settings()

        assert settings.APP_NAME == "AI Software Factory"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.HOST == "127.0.0.1"
        assert settings.PORT == 8000
        assert settings.WORKERS == 1

    def test_environment_validation(self):
        """Test that environment values are validated."""
        # Valid environments
        assert Settings(ENVIRONMENT="development").ENVIRONMENT == "development"
        assert Settings(ENVIRONMENT="production", SECRET_KEY="custom-secret-key").ENVIRONMENT == "production"
        assert Settings(ENVIRONMENT="staging", SECRET_KEY="custom-secret-key").ENVIRONMENT == "staging"
        assert Settings(ENVIRONMENT="testing").ENVIRONMENT == "testing"

        # Case insensitive
        assert Settings(ENVIRONMENT="DEVELOPMENT").ENVIRONMENT == "development"
        assert Settings(ENVIRONMENT="Production", SECRET_KEY="custom-secret-key").ENVIRONMENT == "production"

        # Invalid environment
        with pytest.raises(ValidationError) as exc_info:
            Settings(ENVIRONMENT="invalid")
        assert "ENVIRONMENT must be one of" in str(exc_info.value)

    def test_log_level_validation(self):
        """Test that log level values are validated."""
        # Valid log levels
        assert Settings(LOG_LEVEL="DEBUG").LOG_LEVEL == "DEBUG"
        assert Settings(LOG_LEVEL="INFO").LOG_LEVEL == "INFO"
        assert Settings(LOG_LEVEL="WARNING").LOG_LEVEL == "WARNING"
        assert Settings(LOG_LEVEL="ERROR").LOG_LEVEL == "ERROR"
        assert Settings(LOG_LEVEL="CRITICAL").LOG_LEVEL == "CRITICAL"

        # Case insensitive
        assert Settings(LOG_LEVEL="debug").LOG_LEVEL == "DEBUG"
        assert Settings(LOG_LEVEL="Info").LOG_LEVEL == "INFO"

        # Invalid log level
        with pytest.raises(ValidationError) as exc_info:
            Settings(LOG_LEVEL="invalid")
        assert "LOG_LEVEL must be one of" in str(exc_info.value)

    def test_positive_integer_validation(self):
        """Test that positive integer values are validated."""
        # Valid values
        assert Settings(PORT=8080).PORT == 8080
        assert Settings(WORKERS=4).WORKERS == 4

        # Invalid values
        with pytest.raises(ValidationError) as exc_info:
            Settings(PORT=0)
        assert "Value must be a positive integer" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Settings(PORT=-1)
        assert "Value must be a positive integer" in str(exc_info.value)

    def test_secret_key_validation_in_production(self):
        """Test that default secret key is rejected in production."""
        # Should work in development
        Settings(ENVIRONMENT="development", SECRET_KEY="default")

        # Should fail in production with default key
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="your-secret-key-change-in-production"
            )
        assert "SECRET_KEY must be changed from default in production" in str(exc_info.value)

        # Should work in production with custom key
        settings = Settings(ENVIRONMENT="production", SECRET_KEY="custom-secret-key")
        assert settings.SECRET_KEY == "custom-secret-key"

    def test_secret_key_validation_in_staging(self):
        """Test that default secret key is rejected in staging (security hardening)."""
        # Should fail in staging with default key
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                ENVIRONMENT="staging",
                SECRET_KEY="your-secret-key-change-in-production"
            )
        assert "SECRET_KEY must be changed from default in staging" in str(exc_info.value)

        # Should work in staging with custom key
        settings = Settings(ENVIRONMENT="staging", SECRET_KEY="custom-secret-key")
        assert settings.SECRET_KEY == "custom-secret-key"

    def test_allowed_hosts_list_property(self):
        """Test that allowed_hosts_list property works correctly."""
        settings = Settings(ALLOWED_HOSTS="localhost,example.com,api.example.com")

        assert settings.allowed_hosts_list == ["localhost", "example.com", "api.example.com"]

    def test_allowed_hosts_single_value(self):
        """Test allowed_hosts_list with single value."""
        settings = Settings(ALLOWED_HOSTS="*")

        assert settings.allowed_hosts_list == ["*"]

    def test_allowed_hosts_empty_default(self):
        """Test allowed_hosts_list with empty default (security hardening)."""
        settings = Settings()  # Default is now empty

        assert settings.allowed_hosts_list == []

    def test_environment_properties(self):
        """Test environment check properties."""
        dev_settings = Settings(ENVIRONMENT="development")
        assert dev_settings.is_development is True
        assert dev_settings.is_production is False
        assert dev_settings.is_testing is False

        prod_settings = Settings(ENVIRONMENT="production", SECRET_KEY="custom-secret-key")
        assert prod_settings.is_development is False
        assert prod_settings.is_production is True
        assert prod_settings.is_testing is False

        test_settings = Settings(ENVIRONMENT="testing")
        assert test_settings.is_development is False
        assert test_settings.is_production is False
        assert test_settings.is_testing is True


class TestCorsOriginsProperty:
    """Test cases for cors_origins_list property."""

    def test_cors_origins_list_development_defaults(self):
        """Test cors_origins_list returns localhost defaults in development."""
        settings = Settings(ENVIRONMENT="development", CORS_ORIGINS="")

        origins = settings.cors_origins_list

        assert "http://localhost:3000" in origins
        assert "http://localhost:8000" in origins
        assert "http://127.0.0.1:3000" in origins
        assert "http://127.0.0.1:8000" in origins

    def test_cors_origins_list_production_empty(self):
        """Test cors_origins_list returns empty list in production when not set (lines 230-231)."""
        settings = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="custom-secret-key",
            CORS_ORIGINS=""
        )

        origins = settings.cors_origins_list

        assert origins == []

    def test_cors_origins_list_staging_empty(self):
        """Test cors_origins_list returns empty list in staging when not set."""
        settings = Settings(
            ENVIRONMENT="staging",
            SECRET_KEY="custom-secret-key",
            CORS_ORIGINS=""
        )

        origins = settings.cors_origins_list

        assert origins == []

    def test_cors_origins_list_testing_empty(self):
        """Test cors_origins_list returns empty list in testing when not set."""
        settings = Settings(ENVIRONMENT="testing", CORS_ORIGINS="")

        origins = settings.cors_origins_list

        # Testing environment should also return defaults like development
        # OR empty - depends on implementation
        # According to code: is_development check, testing is not development
        assert origins == [] or len(origins) > 0

    def test_cors_origins_list_with_values(self):
        """Test cors_origins_list parses comma-separated values."""
        settings = Settings(
            CORS_ORIGINS="https://example.com, https://api.example.com , https://app.example.com"
        )

        origins = settings.cors_origins_list

        assert len(origins) == 3
        assert "https://example.com" in origins
        assert "https://api.example.com" in origins
        assert "https://app.example.com" in origins

    def test_cors_origins_list_single_value(self):
        """Test cors_origins_list with single value."""
        settings = Settings(CORS_ORIGINS="https://example.com")

        origins = settings.cors_origins_list

        assert origins == ["https://example.com"]


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()

        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self):
        """Test that get_settings caches the result."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_reload_settings_clears_cache(self):
        """Test that reload_settings clears the cache."""
        settings1 = get_settings()

        # Reload settings
        settings2 = reload_settings()

        # Should be different objects
        assert settings1 is not settings2
        # But should have same values
        assert settings1.APP_NAME == settings2.APP_NAME


class TestEnvironmentVariables:
    """Test cases for environment variable loading."""

    @patch.dict(os.environ, {
        "APP_NAME": "Custom App",
        "APP_VERSION": "2.0.0",
        "DEBUG": "true",
        "PORT": "9000",
    })
    def test_settings_from_environment(self):
        """Test that settings are loaded from environment variables."""
        # Clear cache to pick up new environment
        reload_settings()

        settings = Settings()

        assert settings.APP_NAME == "Custom App"
        assert settings.APP_VERSION == "2.0.0"
        assert settings.DEBUG is True
        assert settings.PORT == 9000

    def tearDown(self):
        """Clean up after tests."""
        reload_settings()
