"""
Middleware module for AI Software Factory backend.

This module provides FastAPI middleware for cross-cutting concerns including
error handling, request logging, correlation ID management, and CORS.
"""

from backend.middleware.error_handler import ErrorHandlerMiddleware
from backend.middleware.request_logging import RequestLoggingMiddleware
from backend.middleware.correlation_id import CorrelationIdMiddleware

__all__ = [
    "ErrorHandlerMiddleware",
    "RequestLoggingMiddleware",
    "CorrelationIdMiddleware",
]
