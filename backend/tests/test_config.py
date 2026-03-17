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
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
        assert settings.WORKERS == 1
    
    def test_environment_validation(self):
        """Test that environment values are validated."""
        # Valid environments
        assert Settings(ENVIRONMENT="development").ENVIRONMENT == "development"
        assert Settings(ENVIRONMENT="production", SECRET_KEY="custom-secret-key").ENVIRONMENT == "production"
        assert Settings(ENVIRONMENT="staging").ENVIRONMENT == "staging"
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
    
    def test_allowed_hosts_list_property(self):
        """Test that allowed_hosts_list property works correctly."""
        settings = Settings(ALLOWED_HOSTS="localhost,example.com,api.example.com")
        
        assert settings.allowed_hosts_list == ["localhost", "example.com", "api.example.com"]
    
    def test_allowed_hosts_single_value(self):
        """Test allowed_hosts_list with single value."""
        settings = Settings(ALLOWED_HOSTS="*")
        
        assert settings.allowed_hosts_list == ["*"]
    
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
