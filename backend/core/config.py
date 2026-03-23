"""
Configuration management for AI Software Factory backend.

This module provides centralized configuration management using pydantic-settings.
It supports environment-based configuration with type safety and validation.
"""

from functools import lru_cache

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
    HOST: str = Field(
        default="127.0.0.1",
        description="Server host address. Use 0.0.0.0 for Docker/containerized deployments"
    )
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of worker processes")

    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="Secret key for encryption")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration time")

    # CORS
    ALLOWED_HOSTS: str = Field(default="", description="Comma-separated list of allowed hosts (must be explicitly set in production)")
    CORS_ORIGINS: str = Field(default="", description="Comma-separated list of allowed CORS origins")

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
    OLLAMA_MODEL: str = Field(
        default="llama3.2",
        description="Default Ollama model for general tasks"
    )
    LLM_DEFAULT_MODEL: str = Field(
        default="llama3.2",
        description="Default LLM model name used by the model router"
    )
    LLM_PROVIDER: str = Field(
        default="ollama",
        description="LLM provider to use (ollama, openai)"
    )

    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics endpoint port")

    # OpenTelemetry settings
    OTEL_ENABLED: bool = Field(default=True, description="Enable OpenTelemetry tracing")
    OTEL_EXPORTER_ENDPOINT: str = Field(default="", description="OTLP exporter endpoint (e.g., localhost:4317)")
    OTEL_SERVICE_NAME: str = Field(default="theta-ai-backend", description="Service name for tracing")

    # Escalation
    ESCALATION_WEBHOOK_URL: str = Field(default="", description="Webhook URL for human escalation notifications")

    # Timeout Configuration (seconds)
    LLM_TIMEOUT_SECONDS: int = Field(
        default=30,
        description="LLM API call timeout in seconds"
    )
    LLM_STREAM_TIMEOUT_SECONDS: int = Field(
        default=60,
        description="LLM streaming API call timeout in seconds"
    )
    DB_QUERY_TIMEOUT_SECONDS: int = Field(
        default=10,
        description="Database query timeout in seconds"
    )
    EXTERNAL_HTTP_TIMEOUT_SECONDS: int = Field(
        default=15,
        description="External HTTP call timeout in seconds"
    )

    # Circuit Breaker Configuration
    CB_FAILURE_THRESHOLD: int = Field(
        default=5,
        description="Number of failures before circuit breaker opens"
    )
    CB_RECOVERY_TIMEOUT_SECONDS: int = Field(
        default=30,
        description="Seconds before circuit breaker attempts recovery"
    )

    # Rate Limiting Configuration
    RATE_LIMIT_DEFAULT: int = Field(
        default=100,
        description="Default requests per minute for regular users"
    )
    RATE_LIMIT_ADMIN: int = Field(
        default=500,
        description="Requests per minute for admin users"
    )
    RATE_LIMIT_WINDOW_SECONDS: int = Field(
        default=60,
        description="Rate limit window in seconds"
    )

    # Backup Configuration
    BACKUP_ENABLED: bool = Field(
        default=True,
        description="Enable database backups"
    )
    BACKUP_RETENTION_DAYS: int = Field(
        default=30,
        description="Days to retain backups"
    )
    BACKUP_SCHEDULE: str = Field(
        default="0 2 * * *",
        description="Backup cron schedule (default: daily at 2 AM)"
    )
    BACKUP_DIR: str = Field(
        default="./backups",
        description="Directory for storing backups"
    )

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
        """Validate secret key in non-development environments."""
        values = info.data
        environment = values.get("ENVIRONMENT", "development")
        # In production or staging, SECRET_KEY must be changed from default
        if environment in ("production", "staging") and v == "your-secret-key-change-in-production":
            raise ValueError(f"SECRET_KEY must be changed from default in {environment}")
        return v

    @property
    def allowed_hosts_list(self) -> list[str]:
        """Get allowed hosts as a list."""
        if not self.ALLOWED_HOSTS:
            return []
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Get CORS origins as a list.

        Returns:
            List of allowed CORS origins. If not configured,
            returns localhost defaults for development only.
        """
        if not self.CORS_ORIGINS:
            # In development, allow localhost origins by default
            if self.is_development:
                return [
                    "http://localhost:3000",
                    "http://localhost:8000",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8000",
                ]
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

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


@lru_cache
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
