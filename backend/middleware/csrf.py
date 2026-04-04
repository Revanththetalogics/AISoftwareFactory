"""
CSRF Middleware module.

Re-exports CSRFMiddleware for compatibility.
"""

from backend.middleware.csrf_middleware import CSRFMiddleware

__all__ = ["CSRFMiddleware"]
