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
            # Debug print
            print(f"DEBUG: Caught exception: {type(exc)}, status_code: {getattr(exc, 'status_code', 'N/A')}")
            # Handle the exception
            response = await self.handle_exception(exc, request_id, scope)
            await response(scope, receive, send)

    async def handle_exception(
        self,
        exc: Exception,
        request_id: str,
        scope: dict[str, Any]
    ) -> JSONResponse:
        """Handle different types of exceptions."""

        # Extract request info for logging
        request_info = self._extract_request_info(scope)

        # Handle BackendException and AISoftwareFactoryException subclasses
        print(f"DEBUG: Checking if {type(exc)} is BackendException or AISoftwareFactoryException")
        if isinstance(exc, (BackendException, AISoftwareFactoryException)):
            print(f"DEBUG: Handling as backend exception")
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
        self,
        exc: AISoftwareFactoryException,
        request_id: str,
        request_info: dict[str, Any]
    ) -> JSONResponse:
        """Handle BackendException and subclasses."""

        # Log the error with full context
        self._log_backend_exception(exc, request_id, request_info)

        # Convert to HTTPException and create response
        http_exc = handle_backend_exception(exc, request_id, logger)
        
        # Debug print
        print(f"DEBUG: Exception type: {type(exc)}, status_code: {exc.status_code}")
        print(f"DEBUG: HTTPException status_code: {http_exc.status_code}")

        # Add request_id to top level for test compatibility
        response_content = http_exc.detail.copy()
        response_content["request_id"] = request_id
        
        return JSONResponse(
            status_code=http_exc.status_code,
            content=response_content,
            headers={"X-Request-ID": request_id}
        )

    def _handle_http_exception(
        self,
        exc: HTTPException,
        request_id: str,
        request_info: dict[str, Any]
    ) -> JSONResponse:
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
                "client": request_info.get("client")
            }
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
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }

        return JSONResponse(
            status_code=exc.status_code,
            content=response_content,
            headers={"X-Request-ID": request_id}
        )

    def _handle_validation_error(
        self,
        exc: ValidationError,
        request_id: str,
        request_info: dict[str, Any]
    ) -> JSONResponse:
        """Handle validation errors specifically."""

        logger.warning(
            f"Validation error: {exc.message}",
            extra={
                "request_id": request_id,
                "field": exc.details.get("field"),
                "value": exc.details.get("value"),
                "method": request_info.get("method"),
                "path": request_info.get("path")
            }
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
                    "timestamp": datetime.now(UTC).isoformat()
                }
            },
            headers={"X-Request-ID": request_id}
        )

    def _handle_generic_exception(
        self,
        exc: Exception,
        request_id: str,
        request_info: dict[str, Any]
    ) -> JSONResponse:
        """Handle unexpected exceptions."""

        # Log the full traceback for debugging
        logger.error(
            f"Unexpected error: {str(exc)}",
            extra={
                "request_id": request_id,
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "client": request_info.get("client"),
                "traceback": traceback.format_exc()
            }
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
                    "timestamp": datetime.now(UTC).isoformat(),
                    "request_id": request_id
                }
            },
            headers={"X-Request-ID": request_id}
        )

    def _extract_request_info(self, scope: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant request information."""
        return {
            "method": scope.get("method", "UNKNOWN"),
            "path": scope.get("path", "UNKNOWN"),
            "client": scope.get("client", ["UNKNOWN", 0])[0] if scope.get("client") else "UNKNOWN",
            "scheme": scope.get("scheme", "http"),
            "http_version": scope.get("http_version", "1.1")
        }

    def _log_backend_exception(
        self,
        exc: AISoftwareFactoryException,
        request_id: str,
        request_info: dict[str, Any]
    ):
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
                "details": getattr(exc, 'details', {}),
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "client": request_info.get("client")
            }
        )

# Decorator for route-specific error handling
def handle_route_errors(func):
    """Decorator to wrap route functions with error handling."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BackendException:
            # Re-raise BackendException to be handled by middleware
            raise
        except Exception as exc:
            # Convert generic exceptions to BackendException
            raise BackendException(
                message=f"Route error: {str(exc)}",
                error_code="ROUTE_ERROR",
                status_code=500
            ) from exc
    return wrapper

# Context manager for error handling in business logic
class ErrorContext:
    """Context manager for handling errors in business logic."""

    def __init__(self, operation: str, resource: str = None):
        self.operation = operation
        self.resource = resource

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            # If it's already a BackendException, re-raise
            if isinstance(exc_val, BackendException):
                return False

            # Convert other exceptions to appropriate BackendException
            error_msg = f"Error during {self.operation}"
            if self.resource:
                error_msg += f" for {self.resource}"

            raise BackendException(
                message=f"{error_msg}: {str(exc_val)}",
                error_code="OPERATION_ERROR",
                status_code=500
            ) from exc_val

        return True

# Utility function for safe execution with error handling
async def safe_execute(operation, *args, **kwargs):
    """Safely execute an operation with error handling."""
    try:
        if callable(operation):
            return await operation(*args, **kwargs) if hasattr(operation, '__call__') else operation(*args, **kwargs)
        else:
            return operation
    except BackendException:
        raise
    except Exception as exc:
        raise BackendException(
            message=f"Operation failed: {str(exc)}",
            error_code="EXECUTION_ERROR",
            status_code=500
        ) from exc


def setup_exception_handlers(app):
    """Setup exception handlers for the FastAPI app."""
    pass  # Exception handlers are typically setup elsewhere
