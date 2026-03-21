"""
Prometheus metrics middleware for HTTP request tracking.

This middleware collects HTTP request metrics including:
- Request count by method, endpoint, and status code
- Request duration histogram
- Active requests gauge
- Error count by type
"""

import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.logging import get_logger
from backend.infrastructure.metrics import get_metrics_collector

logger = get_logger(__name__)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for HTTP requests.

    Tracks request count, duration, active requests, and errors
    for monitoring and alerting purposes.

    Attributes:
        exclude_paths: Paths to exclude from metrics collection

    Example:
        >>> app.add_middleware(
        ...     PrometheusMetricsMiddleware,
        ...     exclude_paths=["/health", "/metrics"]
        ... )
    """

    def __init__(
        self,
        app,
        exclude_paths: list | None = None,
    ):
        """
        Initialize middleware.

        Args:
            app: FastAPI application
            exclude_paths: Paths to exclude from metrics
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/ready", "/live"]
        self.collector = get_metrics_collector()

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """
        Process request with metrics collection.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler
        """
        # Skip metrics for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Record start time and increment active requests
        start_time = time.time()
        self.collector._active_request_count += 1
        self.collector.concurrent_requests.set(self.collector._active_request_count)

        method = request.method
        # Normalize path to prevent high cardinality (replace IDs with placeholder)
        path = self._normalize_path(request.url.path)

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record success metrics
            self.collector.record_api_request(
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration=duration
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration = time.time() - start_time

            # Record error metrics
            self.collector.record_api_error(
                method=method,
                endpoint=path,
                error_type=type(exc).__name__
            )

            # Also record as a request with 500 status
            self.collector.record_api_request(
                method=method,
                endpoint=path,
                status_code=500,
                duration=duration
            )

            raise

        finally:
            # Decrement active requests
            self.collector._active_request_count = max(
                0, self.collector._active_request_count - 1
            )
            self.collector.concurrent_requests.set(self.collector._active_request_count)

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path to prevent high cardinality metrics.

        Replaces UUIDs and numeric IDs with placeholders to keep
        metric label cardinality under control.

        Args:
            path: Original request path

        Returns:
            Normalized path
        """
        import re

        # Replace UUIDs
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}',
            path,
            flags=re.IGNORECASE
        )

        # Replace numeric IDs in path segments
        path = re.sub(r'/\d+(?=/|$)', '/{id}', path)

        return path
