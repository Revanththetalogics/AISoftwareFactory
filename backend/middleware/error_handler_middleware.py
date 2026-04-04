"""
Error Handler Middleware module.

Re-exports ErrorHandlerMiddleware for compatibility.
"""

from backend.middleware.error_handler import ErrorHandlerMiddleware

__all__ = ["ErrorHandlerMiddleware"]
