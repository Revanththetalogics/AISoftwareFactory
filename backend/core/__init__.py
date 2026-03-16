"""
Core module for AI Software Factory backend.

This module provides foundational components including configuration management,
structured logging, and exception handling.
"""

from backend.core.config import Settings, get_settings
from backend.core.exceptions import (
    AISoftwareFactoryException,
    ConfigurationError,
    ValidationError,
    ResourceNotFoundError,
    AuthenticationError,
    AuthorizationError,
    ServiceUnavailableError,
)
from backend.core.logging import get_logger, configure_logging

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
