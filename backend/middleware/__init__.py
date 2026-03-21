"""
Middleware module for AI Software Factory backend.

This module provides FastAPI middleware for cross-cutting concerns including
error handling, request logging, correlation ID management, authentication, CORS, and CSRF.
"""

from backend.middleware.auth_middleware import AuthenticationMiddleware
from backend.middleware.correlation_id import CorrelationIdMiddleware
from backend.middleware.csrf_middleware import CSRFMiddleware
from backend.middleware.error_handler import ErrorHandlerMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware

__all__ = [
    "AuthenticationMiddleware",
    "ErrorHandlerMiddleware",
    "RequestLoggingMiddleware",
    "CorrelationIdMiddleware",
    "CSRFMiddleware",
]
