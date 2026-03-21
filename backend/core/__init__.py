"""
Core module for AI Software Factory backend.

This module provides foundational components including configuration management,
structured logging, and exception handling.
"""

from backend.core.config import Settings, get_settings
from backend.core.exceptions import (
    AISoftwareFactoryException,
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    ValidationError,
)
from backend.core.logging import configure_logging, get_logger

__all__ = [
    "Settings",
    "get_settings",
    "AISoftwareFactoryException",
    "ConfigurationError",
    "ValidationError",
    "ResourceNotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "ServiceUnavailableError",
    "get_logger",
    "configure_logging",
]
