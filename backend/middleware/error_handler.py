"""
Global error handling middleware for AI Software Factory backend.

This middleware catches all exceptions and converts them to standardized
HTTP responses with proper error codes and logging.
"""

import traceback

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.core.config import get_settings
from backend.core.exceptions import AISoftwareFactoryException
from backend.core.logging import get_correlation_id, get_logger

logger = get_logger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global error handling.

    This middleware catches all exceptions and:
    1. Logs errors with full context
    2. Converts custom exceptions to HTTP responses
    3. Returns generic 500 errors for unexpected exceptions (in production)
    4. Includes stack traces (in development)
    5. Adds correlation ID to error responses

    Example:
        >>> app.add_middleware(ErrorHandlerMiddleware)
    """

    def __init__(self, app):
        """
        Initialize middleware.

        Args:
            app: FastAPI application
        """
        super().__init__(app)
        self.settings = get_settings()

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """
        Process request with error handling.

        Args:
            request: Incoming request
            call_next: Next middleware/handler in chain

        Returns:
            Response from handler or error response
        """
        try:
            return await call_next(request)

        except AISoftwareFactoryException as exc:
            # Handle custom application exceptions
            return self._handle_custom_exception(exc, request)

        except Exception as exc:
            # Handle unexpected exceptions
            return self._handle_unexpected_exception(exc, request)

    def _handle_custom_exception(
        self,
        exc: AISoftwareFactoryException,
        request: Request,
    ) -> JSONResponse:
        """
        Handle custom application exceptions.

        Args:
            exc: Custom exception instance
            request: FastAPI request

        Returns:
            JSON error response with standardized format
        """
        request_id = get_correlation_id()

        # Log the error with context
        logger.error(
            "Application error",
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path,
            method=request.method,
            request_id=request_id,
        )

        # Build standardized error response
        error_response = {
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details or {},
            },
            "request_id": request_id,
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
        )

    def _handle_unexpected_exception(
        self,
        exc: Exception,
        request: Request,
    ) -> JSONResponse:
        """
        Handle unexpected exceptions.

        In production, returns a generic error message.
        In development, includes the full error details and stack trace.

        Args:
            exc: Unexpected exception
            request: FastAPI request

        Returns:
            JSON error response with standardized format
        """
        request_id = get_correlation_id()

        # Log the full error with stack trace
        logger.exception(
            "Unexpected error",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
            method=request.method,
            request_id=request_id,
        )

        if self.settings.is_development or self.settings.is_testing:
            # Return detailed error in development
            error_response = {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(exc),
                    "details": {
                        "type": type(exc).__name__,
                        "stack_trace": traceback.format_exc().split("\n"),
                    },
                },
                "request_id": request_id,
            }
        else:
            # Return generic error in production
            error_response = {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {},
                },
                "request_id": request_id,
            }

        return JSONResponse(
            status_code=500,
            content=error_response,
        )


def setup_exception_handlers(app) -> None:
    """
    Setup exception handlers for FastAPI application.

    This function adds exception handlers for specific exception types
    that may be raised outside of the middleware context.

    Args:
        app: FastAPI application instance

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> setup_exception_handlers(app)
    """

    @app.exception_handler(AISoftwareFactoryException)
    async def custom_exception_handler(
        request: Request,
        exc: AISoftwareFactoryException,
    ) -> JSONResponse:
        """Handle custom application exceptions."""
        request_id = get_correlation_id()

        logger.error(
            "Application error (handler)",
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            path=request.url.path,
            request_id=request_id,
        )

        error_response = {
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details or {},
            },
            "request_id": request_id,
        }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        settings = get_settings()
        request_id = get_correlation_id()

        logger.exception(
            "Unexpected error (handler)",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=request.url.path,
            request_id=request_id,
        )

        if settings.is_development or settings.is_testing:
            error_response = {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(exc),
                    "details": {
                        "type": type(exc).__name__,
                        "stack_trace": traceback.format_exc().split("\n"),
                    },
                },
                "request_id": request_id,
            }
        else:
            error_response = {
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": {},
                },
                "request_id": request_id,
            }

        return JSONResponse(
            status_code=500,
            content=error_response,
        )
