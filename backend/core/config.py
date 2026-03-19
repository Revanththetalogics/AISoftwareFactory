"""
Configuration management for AI Software Factory backend.

This module provides centralized configuration management using pydantic-settings.
It supports environment-based configuration with type safety and validation.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with environment-based configuration.
    
    All settings are loaded from environment variables or .env file.
    Values are validated at startup to ensure proper configuration.
    
    Attributes:
        APP_NAME: Application name
        APP_VERSION: Application version
        DEBUG: Debug mode flag
        ENVIRONMENT: Deployment environment (development, staging, production)
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        # Server Configuration
        HOST: Server host address
        PORT: Server port
        WORKERS: Number of worker processes
        
        # Security
        SECRET_KEY: Secret key for encryption
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time
        
        # CORS
        ALLOWED_HOSTS: List of allowed hosts for CORS
        
        # Database (for future phases)
        DATABASE_URL: PostgreSQL connection URL
        DATABASE_POOL_SIZE: Database connection pool size
        
        # Redis (for future phases)
        REDIS_URL: Redis connection URL
        
        # Monitoring
        ENABLE_METRICS: Enable Prometheus metrics
        METRICS_PORT: Metrics endpoint port
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application Settings
    APP_NAME: str = Field(default="AI Software Factory", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode flag")
    ENVIRONMENT: str = Field(default="development", description="Deployment environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="Secret key for encryption")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration time")
    
    # CORS
    ALLOWED_HOSTS: str = Field(default="*", description="Comma-separated list of allowed hosts")
    
    # Database Configuration (Phase 5)
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/ai_factory",
        description="PostgreSQL connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    
    # Redis Configuration (Phase 4)
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Ollama AI Service
    OLLAMA_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics endpoint port")
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v.lower()
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()
    
    @field_validator("PORT", "METRICS_PORT", "DATABASE_POOL_SIZE", "WORKERS")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Validate positive integer values."""
        if v < 1:
            raise ValueError("Value must be a positive integer")
        return v
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate secret key in production."""
        values = info.data
        if values.get("ENVIRONMENT") == "production" and v == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed from default in production")
        return v
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list."""
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    This function uses LRU cache to avoid reloading settings
    on every call, improving performance.
    
    Returns:
        Settings: Application settings instance
        
    Example:
        >>> settings = get_settings()
        >>> print(settings.APP_NAME)
        'AI Software Factory'
    """
    return Settings()


def reload_settings() -> Settings:
    """
    Force reload settings from environment.
    
    This is useful for testing or when environment variables change.
    
    Returns:
        Settings: Fresh application settings instance
    """
    get_settings.cache_clear()
    return get_settings()
