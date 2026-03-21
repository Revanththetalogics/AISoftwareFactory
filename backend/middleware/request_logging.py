"""
Request logging middleware for API access logging.

This middleware logs all incoming requests and their responses for monitoring,
debugging, and audit purposes.
"""

import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.logging import get_correlation_id, get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.

    This middleware logs:
    - Request method, path, and query parameters
    - Client IP address
    - Response status code
    - Request duration
    - Correlation ID

    Attributes:
        exclude_paths: List of paths to exclude from logging (e.g., health checks)

    Example:
        >>> app.add_middleware(RequestLoggingMiddleware, exclude_paths=["/health"])
    """

    def __init__(
        self,
        app,
        exclude_paths: Optional[list] = None,
    ):
        """
        Initialize middleware.

        Args:
            app: FastAPI application
            exclude_paths: Paths to exclude from logging
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics"]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """
        Process request with logging.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler
        """
        # Skip logging for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            client_ip=client_ip,
            correlation_id=get_correlation_id(),
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                correlation_id=get_correlation_id(),
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Log error
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
                correlation_id=get_correlation_id(),
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Checks X-Forwarded-For header first for proxied requests,
        falls back to direct connection IP.

        Args:
            request: FastAPI request

        Returns:
            Client IP address
        """
        # Check for forwarded IP (when behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"
