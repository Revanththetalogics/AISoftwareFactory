"""
Custom exception hierarchy for AI Software Factory backend.

This module provides a comprehensive exception hierarchy for proper error handling,
enabling consistent error responses and logging across the application.
"""

from typing import Any


class AISoftwareFactoryException(Exception):
    """
    Base exception for all AI Software Factory errors.

    This is the root exception class that all other custom exceptions inherit from.
    It provides common functionality for error codes, messages, and additional context.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code
        status_code: HTTP status code for API responses
        details: Additional error details

    Example:
        >>> raise AISoftwareFactoryException("Something went wrong", error_code="INTERNAL_ERROR")
    """

    message: str = "An unexpected error occurred"
    error_code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize exception with error details.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            details: Additional error context
        """
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        self.status_code = status_code or self.status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to dictionary for API responses.

        Returns:
            Dictionary containing error details

        Example:
            >>> exc = AISoftwareFactoryException("Not found", error_code="NOT_FOUND")
            >>> exc.to_dict()
            {'error_code': 'NOT_FOUND', 'message': 'Not found', 'details': {}}
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }

    def __str__(self) -> str:
        """Return string representation of exception."""
        if self.details:
            return f"[{self.error_code}] {self.message} - Details: {self.details}"
        return f"[{self.error_code}] {self.message}"


class ConfigurationError(AISoftwareFactoryException):
    """
    Exception raised for configuration-related errors.

    This includes missing environment variables, invalid configuration values,
    or configuration file errors.

    Attributes:
        status_code: 500 (server configuration error)

    Example:
        >>> raise ConfigurationError("Missing DATABASE_URL environment variable")
    """

    message = "Configuration error"
    error_code = "CONFIGURATION_ERROR"
    status_code = 500


class ValidationError(AISoftwareFactoryException):
    """
    Exception raised for input validation errors.

    This includes invalid request data, missing required fields,
    or data format errors.

    Attributes:
        status_code: 400 (bad request)

    Example:
        >>> raise ValidationError("Invalid email format", details={"field": "email"})
    """

    message = "Validation error"
    error_code = "VALIDATION_ERROR"
    status_code = 400

    def __init__(
        self,
        message: str | None = None,
        errors: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize validation error with field-specific errors.

        Args:
            message: General error message
            errors: List of field-specific errors
            **kwargs: Additional arguments passed to parent
        """
        details = kwargs.get("details", {})
        if errors:
            details["errors"] = errors
        kwargs["details"] = details
        super().__init__(message=message, **kwargs)


class ResourceNotFoundError(AISoftwareFactoryException):
    """
    Exception raised when a requested resource is not found.

    This includes missing database records, files, or any other resources.

    Attributes:
        status_code: 404 (not found)

    Example:
        >>> raise ResourceNotFoundError("Project not found", details={"project_id": "123"})
    """

    message = "Resource not found"
    error_code = "RESOURCE_NOT_FOUND"
    status_code = 404

    def __init__(
        self,
        resource_type: str | None = None,
        resource_id: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize not found error with resource details.

        Args:
            resource_type: Type of resource (e.g., "project", "user")
            resource_id: ID of the missing resource
            **kwargs: Additional arguments passed to parent
        """
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        kwargs["details"] = details

        message = kwargs.get("message")
        if not message and resource_type:
            message = f"{resource_type} not found"
            if resource_id:
                message += f" with id '{resource_id}'"
        kwargs["message"] = message

        super().__init__(**kwargs)


class AuthenticationError(AISoftwareFactoryException):
    """
    Exception raised for authentication failures.

    This includes invalid credentials, expired tokens, or missing authentication.

    Attributes:
        status_code: 401 (unauthorized)

    Example:
        >>> raise AuthenticationError("Invalid credentials")
    """

    message = "Authentication failed"
    error_code = "AUTHENTICATION_ERROR"
    status_code = 401


class AuthorizationError(AISoftwareFactoryException):
    """
    Exception raised for authorization failures.

    This includes insufficient permissions or access denied errors.

    Attributes:
        status_code: 403 (forbidden)

    Example:
        >>> raise AuthorizationError("Insufficient permissions", details={"required": "admin"})
    """

    message = "Access denied"
    error_code = "AUTHORIZATION_ERROR"
    status_code = 403


class ServiceUnavailableError(AISoftwareFactoryException):
    """
    Exception raised when a dependent service is unavailable.

    This includes database connection failures, external API errors,
    or any service dependency issues.

    Attributes:
        status_code: 503 (service unavailable)

    Example:
        >>> raise ServiceUnavailableError("Database connection failed")
    """

    message = "Service temporarily unavailable"
    error_code = "SERVICE_UNAVAILABLE"
    status_code = 503

    def __init__(
        self,
        service: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize service error with service details.

        Args:
            service: Name of the unavailable service
            **kwargs: Additional arguments passed to parent
        """
        details = kwargs.get("details", {})
        if service:
            details["service"] = service
        kwargs["details"] = details

        message = kwargs.get("message")
        if not message and service:
            message = f"{service} is temporarily unavailable"
        kwargs["message"] = message

        super().__init__(**kwargs)


class ConflictError(AISoftwareFactoryException):
    """
    Exception raised for resource conflicts.

    This includes duplicate resources, version conflicts, or state conflicts.

    Attributes:
        status_code: 409 (conflict)

    Example:
        >>> raise ConflictError("Project with this name already exists")
    """

    message = "Resource conflict"
    error_code = "CONFLICT_ERROR"
    status_code = 409


class RateLimitError(AISoftwareFactoryException):
    """
    Exception raised when rate limit is exceeded.

    Attributes:
        status_code: 429 (too many requests)

    Example:
        >>> raise RateLimitError("Rate limit exceeded", details={"retry_after": 60})
    """

    message = "Rate limit exceeded"
    error_code = "RATE_LIMIT_EXCEEDED"
    status_code = 429


class ExternalServiceError(AISoftwareFactoryException):
    """
    Exception raised for external service integration errors.

    This includes errors from third-party APIs or services.

    Attributes:
        status_code: 502 (bad gateway)

    Example:
        >>> raise ExternalServiceError("OpenAI API error", details={"status": 500})
    """

    message = "External service error"
    error_code = "EXTERNAL_SERVICE_ERROR"
    status_code = 502

    def __init__(
        self,
        service: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize external service error.

        Args:
            service: Name of the external service
            **kwargs: Additional arguments passed to parent
        """
        details = kwargs.get("details", {})
        if service:
            details["service"] = service
        kwargs["details"] = details
        super().__init__(**kwargs)
