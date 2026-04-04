"""
Request/Response Logging Middleware.

This module provides comprehensive logging middleware for FastAPI applications
to track all incoming requests and outgoing responses with detailed information.
"""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from backend.core.logging import get_logger

logger = get_logger(__name__)


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses with detailed information."""

    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
        exclude_paths: list[str] = None,
        max_body_length: int = 1000,
    ):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/favicon.ico"]
        self.max_body_length = max_body_length

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Check if path should be excluded
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Record start time
        start_time = time.time()

        # Log request information
        await self._log_request(request, request_id)

        try:
            # Process the request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response information
            await self._log_response(response, request_id, process_time)

            # Add timing header
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Log exceptions
            process_time = time.time() - start_time
            await self._log_exception(request, e, request_id, process_time)
            raise

    async def _log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request details."""
        try:
            # Get request body if needed
            body = None
            if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
                body = await self._get_request_body(request)

            # Prepare log data
            log_data = {
                "request_id": request_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": self._sanitize_headers(dict(request.headers)),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "unknown"),
                "content_type": request.headers.get("content-type", "unknown"),
                "content_length": request.headers.get("content-length", "0"),
            }

            if body:
                log_data["body"] = body

            logger.info("Incoming request", extra=log_data)

        except Exception as e:
            logger.error(f"Failed to log request: {e}")

    async def _log_response(self, response: Response, request_id: str, process_time: float) -> None:
        """Log outgoing response details."""
        try:
            # Get response body if needed
            body = None
            if self.log_response_body:
                body = await self._get_response_body(response)

            # Prepare log data
            log_data = {
                "request_id": request_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "headers": self._sanitize_headers(dict(response.headers)),
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": response.headers.get("content-length", "0"),
            }

            if body:
                log_data["body"] = body

            # Use appropriate log level based on status code
            if 200 <= response.status_code < 300:
                logger.info("Outgoing response", extra=log_data)
            elif 400 <= response.status_code < 500:
                logger.warning("Client error response", extra=log_data)
            elif response.status_code >= 500:
                logger.error("Server error response", extra=log_data)
            else:
                logger.info("Response", extra=log_data)

        except Exception as e:
            logger.error(f"Failed to log response: {e}")

    async def _log_exception(
        self, request: Request, exception: Exception, request_id: str, process_time: float
    ) -> None:
        """Log exceptions that occur during request processing."""
        try:
            log_data = {
                "request_id": request_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "method": request.method,
                "path": request.url.path,
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
                "process_time_ms": round(process_time * 1000, 2),
            }

            logger.error("Request processing failed", extra=log_data, exc_info=exception)

        except Exception as e:
            logger.error(f"Failed to log exception: {e}")

    async def _get_request_body(self, request: Request) -> str:
        """Safely extract request body."""
        try:
            body_bytes = await request.body()
            if not body_bytes:
                return ""

            # Decode body
            try:
                body_str = body_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return f"<binary data: {len(body_bytes)} bytes>"

            # Truncate if too long
            if len(body_str) > self.max_body_length:
                body_str = body_str[: self.max_body_length] + "... [truncated]"

            return body_str

        except Exception as e:
            return f"<failed to read body: {e}>"

    async def _get_response_body(self, response: Response) -> str:
        """Safely extract response body."""
        try:
            # This is tricky because response bodies are streams
            # For now, we'll just log that we attempted to read it
            return "<response body captured>"
        except Exception as e:
            return f"<failed to read response body: {e}>"

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to client host
        client = request.client
        return client.host if client else "unknown"

    def _sanitize_headers(self, headers: dict[str, str]) -> dict[str, str]:
        """Remove sensitive headers from logging."""
        sensitive_headers = {
            "authorization",
            "cookie",
            "set-cookie",
            "x-api-key",
            "x-auth-token",
            "proxy-authorization",
        }

        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = "***"
            else:
                sanitized[key] = value

        return sanitized


class StructuredLogger:
    """Helper class for structured logging with consistent formatting."""

    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)

    def log_request_received(self, request_info: dict[str, Any]) -> None:
        """Log when a request is received."""
        self.logger.info("Request received", extra=request_info)

    def log_request_processed(self, response_info: dict[str, Any]) -> None:
        """Log when a request is processed."""
        self.logger.info("Request processed", extra=response_info)

    def log_slow_request(self, request_info: dict[str, Any], threshold_ms: float = 1000) -> None:
        """Log slow requests."""
        process_time = request_info.get("process_time_ms", 0)
        if process_time > threshold_ms:
            self.logger.warning("Slow request detected", extra=request_info)

    def log_error_request(self, error_info: dict[str, Any]) -> None:
        """Log requests that resulted in errors."""
        self.logger.error("Error request", extra=error_info)


# Pre-configured middleware instances
def create_logging_middleware(
    log_request_body: bool = False, log_response_body: bool = False, exclude_paths: list[str] = None
) -> RequestResponseLoggingMiddleware:
    """Factory function to create logging middleware with common settings."""
    return RequestResponseLoggingMiddleware(
        app=None,  # Will be set when included in app
        log_request_body=log_request_body,
        log_response_body=log_response_body,
        exclude_paths=exclude_paths or ["/health", "/metrics", "/favicon.ico", "/static/"],
    )


# Utility functions for log analysis
class LogAnalyzer:
    """Utility class for analyzing request/response logs."""

    @staticmethod
    def get_endpoint_metrics(logs: list[dict]) -> dict[str, Any]:
        """Calculate metrics for different endpoints."""
        endpoint_stats = {}

        for log in logs:
            if "path" in log and "process_time_ms" in log:
                path = log["path"]
                time_ms = log["process_time_ms"]

                if path not in endpoint_stats:
                    endpoint_stats[path] = {
                        "count": 0,
                        "total_time": 0,
                        "avg_time": 0,
                        "min_time": float("inf"),
                        "max_time": 0,
                        "errors": 0,
                    }

                stats = endpoint_stats[path]
                stats["count"] += 1
                stats["total_time"] += time_ms
                stats["avg_time"] = stats["total_time"] / stats["count"]
                stats["min_time"] = min(stats["min_time"], time_ms)
                stats["max_time"] = max(stats["max_time"], time_ms)

                if log.get("status_code", 0) >= 400:
                    stats["errors"] += 1

        return endpoint_stats

    @staticmethod
    def get_slow_endpoints(endpoint_stats: dict, threshold_ms: float = 1000) -> dict:
        """Get endpoints that exceed the time threshold."""
        slow_endpoints = {}
        for path, stats in endpoint_stats.items():
            if stats["avg_time"] > threshold_ms:
                slow_endpoints[path] = stats

        return dict(sorted(slow_endpoints.items(), key=lambda x: x[1]["avg_time"], reverse=True))


# Configuration for different environments
LOGGING_CONFIGS = {
    "development": {"log_request_body": True, "log_response_body": True, "exclude_paths": ["/health", "/metrics"]},
    "production": {
        "log_request_body": False,
        "log_response_body": False,
        "exclude_paths": ["/health", "/metrics", "/favicon.ico", "/static/", "/docs", "/redoc"],
    },
    "staging": {
        "log_request_body": True,
        "log_response_body": False,
        "exclude_paths": ["/health", "/metrics", "/favicon.ico"],
    },
}
