"""
Enhanced Error Handler Middleware

Provides comprehensive error handling with structured responses,
request correlation, and detailed logging.
"""

import logging
import traceback
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from backend.core.exceptions import (
    AISoftwareFactoryException,
    BackendException,
    ValidationError,
    handle_backend_exception,
)
from backend.core.logging import get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware:
    """Enhanced error handling middleware."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate request ID for correlation
        request_id = str(uuid.uuid4())
        scope["request_id"] = request_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add request ID to response headers
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            # Handle the exception
            response = await self.handle_exception(exc, request_id, scope)
            await response(scope, receive, send)

    async def handle_exception(self, exc: Exception, request_id: str, scope: dict[str, Any]) -> JSONResponse:
        """Handle different types of exceptions."""

        # Extract request info for logging
        request_info = self._extract_request_info(scope)

        # Handle BackendException and AISoftwareFactoryException subclasses
        if isinstance(exc, (BackendException, AISoftwareFactoryException)):
            return self._handle_backend_exception(exc, request_id, request_info)

        # Handle FastAPI HTTPException
        elif isinstance(exc, HTTPException):
            return self._handle_http_exception(exc, request_id, request_info)

        # Handle validation errors
        elif isinstance(exc, ValidationError):
            return self._handle_validation_error(exc, request_id, request_info)

        # Handle generic exceptions
        else:
            return self._handle_generic_exception(exc, request_id, request_info)

    def _handle_backend_exception(
        self, exc: AISoftwareFactoryException, request_id: str, request_info: dict[str, Any]
    ) -> JSONResponse:
        """Handle BackendException and subclasses."""

        # Log the error with full context
        self._log_backend_exception(exc, request_id, request_info)

        # Convert to HTTPException and create response
        http_exc = handle_backend_exception(exc, request_id, logger)

        # Add request_id to top level for test compatibility
        response_content = http_exc.detail.copy()
        response_content["request_id"] = request_id

        return JSONResponse(
            status_code=http_exc.status_code, content=response_content, headers={"X-Request-ID": request_id}
        )

    def _handle_http_exception(self, exc: HTTPException, request_id: str, request_info: dict[str, Any]) -> JSONResponse:
        """Handle FastAPI HTTPException."""

        # Log HTTP exceptions (4xx are warnings, 5xx are errors)
        log_level = logging.ERROR if exc.status_code >= 500 else logging.WARNING
        logger.log(
            log_level,
            f"HTTP {exc.status_code}: {exc.detail}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "client": request_info.get("client"),
            },
        )

        # Ensure consistent error response format
        if isinstance(exc.detail, dict):
            response_content = exc.detail
        else:
            response_content = {
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                    "status_code": exc.status_code,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            }

        return JSONResponse(status_code=exc.status_code, content=response_content, headers={"X-Request-ID": request_id})

    def _handle_validation_error(
        self, exc: ValidationError, request_id: str, request_info: dict[str, Any]
    ) -> JSONResponse:
        """Handle validation errors specifically."""

        logger.warning(
            f"Validation error: {exc.message}",
            extra={
                "request_id": request_id,
                "field": exc.details.get("field"),
                "value": exc.details.get("value"),
                "method": request_info.get("method"),
                "path": request_info.get("path"),
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "status_code": exc.status_code,
                    "details": exc.details,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            },
            headers={"X-Request-ID": request_id},
        )

    def _handle_generic_exception(self, exc: Exception, request_id: str, request_info: dict[str, Any]) -> JSONResponse:
        """Handle unexpected exceptions."""

        # Log the full traceback for debugging
        logger.error(
            f"Unexpected error: {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "client": request_info.get("client"),
                "traceback": traceback.format_exc(),
            },
        )

        # Return generic error response
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "details": {},
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_id": request_id,
                },
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )

    def _extract_request_info(self, scope: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant request information."""
        return {
            "method": scope.get("method", "UNKNOWN"),
            "path": scope.get("path", "UNKNOWN"),
            "client": scope.get("client", ["UNKNOWN", 0])[0] if scope.get("client") else "UNKNOWN",
            "scheme": scope.get("scheme", "http"),
            "http_version": scope.get("http_version", "1.1"),
        }

    def _log_backend_exception(self, exc: AISoftwareFactoryException, request_id: str, request_info: dict[str, Any]):
        """Log backend exception with appropriate level."""

        # Determine log level based on status code
        if exc.status_code >= 500:
            log_level = logging.ERROR
        elif exc.status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        logger.log(
            log_level,
            f"{exc.error_code}: {exc.message}",
            extra={
                "request_id": request_id,
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": getattr(exc, "details", {}),
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "client": request_info.get("client"),
            },
        )


def setup_exception_handlers(app):
    """Setup exception handlers for the FastAPI app."""
    # Register custom exception handlers
    app.add_exception_handler(AISoftwareFactoryException, _handle_custom_exception)
    app.add_exception_handler(Exception, _handle_general_exception)


def _get_request_id(request) -> str:
    """Extract request_id from request state safely."""
    try:
        return str(getattr(request.state, "request_id", "unknown"))
    except Exception:
        return "unknown"


async def _handle_custom_exception(request, exc: AISoftwareFactoryException):
    """Handle custom AISoftwareFactoryException."""
    request_id = _get_request_id(request)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "status_code": exc.status_code,
                "details": getattr(exc, "details", {}),
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "request_id": request_id,
        },
    )


async def _handle_general_exception(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", extra={"traceback": traceback.format_exc()})

    request_id = _get_request_id(request)

    try:
        from backend.core.config import get_settings

        settings = get_settings()
        is_dev = getattr(settings, "is_development", False) or getattr(settings, "is_testing", False)
    except Exception:
        is_dev = False

    message = (
        f"An unexpected error occurred: {type(exc).__name__}: {str(exc)}" if is_dev else "An unexpected error occurred"
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": message,
                "status_code": 500,
                "details": {},
                "timestamp": datetime.now(UTC).isoformat(),
            },
            "request_id": request_id,
        },
    )
