"""
Enhanced Backend Error Handling

Provides granular exception types and improved error handling patterns
for better debugging and user experience.
"""

import logging
from typing import Any

from fastapi import HTTPException, status


# Base exception class
class AISoftwareFactoryException(Exception):
    """Base exception for all AI Software Factory errors."""

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class BackendException(AISoftwareFactoryException):
    """Base exception for all backend errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "BACKEND_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message, error_code, status_code)


# Configuration exception
class ConfigurationError(AISoftwareFactoryException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None):
        super().__init__(
            message=message, error_code="CONFIGURATION_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        self.config_key = config_key


# Resource not found exception
class ResourceNotFoundError(AISoftwareFactoryException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


# Validation exceptions
class ValidationError(BackendException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        errors: list | None = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        details: dict[str, Any] = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        if errors is not None:
            details["errors"] = errors

        super().__init__(message=message, error_code="VALIDATION_ERROR", status_code=status_code, details=details)


class SchemaValidationError(ValidationError):
    """Raised when database schema validation fails."""

    def __init__(self, message: str, schema: str, field: str | None = None):
        super().__init__(message=message, field=field)
        self.details["schema"] = schema


# Resource exceptions
class NotFoundException(BackendException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with id '{resource_id}' not found",
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ConflictException(BackendException):
    """Raised when there's a conflict with the current state."""

    def __init__(self, message: str, resource_type: str, resource_id: str):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


# Authentication/Authorization exceptions
class AuthenticationError(BackendException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, error_code="AUTHENTICATION_ERROR", status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationError(BackendException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions", required_permission: str | None = None):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission

        super().__init__(
            message=message, error_code="AUTHORIZATION_ERROR", status_code=status.HTTP_403_FORBIDDEN, details=details
        )


# Service exceptions
class ServiceUnavailableError(BackendException):
    """Raised when an external service is unavailable."""

    def __init__(self, service_name: str, reason: str = "Service temporarily unavailable"):
        super().__init__(
            message=f"Service '{service_name}' is unavailable: {reason}",
            error_code="SERVICE_UNAVAILABLE",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"service_name": service_name, "reason": reason},
        )


class DatabaseError(BackendException):
    """Raised when database operations fail."""

    def __init__(self, message: str, operation: str, table: str | None = None):
        details = {"operation": operation}
        if table:
            details["table"] = table

        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class CacheError(BackendException):
    """Raised when cache operations fail."""

    def __init__(self, message: str, operation: str, key: str | None = None):
        details = {"operation": operation}
        if key:
            details["key"] = key

        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


# Git/File exceptions
class GitError(BackendException):
    """Raised when Git operations fail."""

    def __init__(self, message: str, operation: str, repo_name: str | None = None):
        details = {"operation": operation}
        if repo_name:
            details["repo_name"] = repo_name

        super().__init__(
            message=message, error_code="GIT_ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=details
        )


class FileNotFoundError(BackendException):
    """Raised when a file is not found."""

    def __init__(self, file_path: str, operation: str = "access"):
        super().__init__(
            message=f"File not found: {file_path}",
            error_code="FILE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"file_path": file_path, "operation": operation},
        )


# Simulation/Knowledge exceptions
class SimulationError(BackendException):
    """Raised when simulation operations fail."""

    def __init__(self, message: str, simulation_id: str | None = None):
        details = {}
        if simulation_id:
            details["simulation_id"] = simulation_id

        super().__init__(
            message=message,
            error_code="SIMULATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class KnowledgeBaseError(BackendException):
    """Raised when knowledge base operations fail."""

    def __init__(self, message: str, operation: str, document_id: str | None = None):
        details = {"operation": operation}
        if document_id:
            details["document_id"] = document_id

        super().__init__(
            message=message,
            error_code="KNOWLEDGE_BASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


# Network/Communication exceptions
class NetworkError(BackendException):
    """Raised when network communication fails."""

    def __init__(self, message: str, endpoint: str, timeout: float | None = None):
        details = {"endpoint": endpoint}
        if timeout:
            details["timeout"] = timeout

        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


# Business logic exceptions
class BusinessLogicError(BackendException):
    """Raised when business rules are violated."""

    def __init__(self, message: str, rule: str):
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"rule": rule},
        )


# Rate limiting exception
class RateLimitError(BackendException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(
            message=message, error_code="RATE_LIMIT_EXCEEDED", status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.retry_after = retry_after


class RateLimitExceededError(RateLimitError):
    """Alias for RateLimitError for backward compatibility."""

    pass


class ExternalServiceError(BackendException):
    """Raised when an external service fails."""

    def __init__(self, message: str = "External service error", service: str | None = None):
        super().__init__(message=message, error_code="EXTERNAL_SERVICE_ERROR", status_code=status.HTTP_502_BAD_GATEWAY)
        self.service = service


class ConflictError(BackendException):
    """Raised when there's a conflict with the current state of a resource."""

    def __init__(self, message: str = "Resource conflict", resource: str | None = None):
        super().__init__(message=message, error_code="CONFLICT_ERROR", status_code=status.HTTP_409_CONFLICT)
        self.resource = resource


# Enhanced error response model
class ErrorResponse:
    """Structured error response format."""

    def __init__(self, error: AISoftwareFactoryException, request_id: str | None = None):
        self.error = {
            "code": error.error_code,
            "message": error.message,
            "status_code": error.status_code,
            "details": getattr(error, "details", {}),
            "timestamp": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
        }
        if request_id:
            self.error["request_id"] = request_id

    def to_dict(self) -> dict[str, Any]:
        return {"success": False, "error": self.error}


# Exception handler utility
def handle_backend_exception(
    exc: AISoftwareFactoryException, request_id: str | None = None, logger: logging.Logger | None = None
) -> HTTPException:
    """Convert BackendException to HTTPException with proper logging."""

    # Log the error
    if logger:
        log_level = logging.ERROR if exc.status_code >= 500 else logging.WARNING
        logger.log(
            log_level,
            f"Backend error: {exc.error_code} - {exc.message}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": getattr(exc, "details", {}),
                "request_id": request_id,
            },
        )

    # Create structured error response
    error_response = ErrorResponse(exc, request_id)

    # Return HTTPException with structured response
    return HTTPException(status_code=exc.status_code, detail=error_response.to_dict())


# Convenience functions for raising common exceptions
def raise_validation_error(field: str, value: Any, message: str = None):
    """Raise a validation error."""
    if not message:
        message = f"Invalid value for field '{field}'"
    raise ValidationError(message, field, value)


def raise_not_found(resource_type: str, resource_id: str):
    """Raise a not found error."""
    raise NotFoundException(resource_type, resource_id)


def raise_auth_error(message: str = "Authentication required"):
    """Raise an authentication error."""
    raise AuthenticationError(message)


def raise_forbidden(permission: str = None):
    """Raise an authorization error."""
    message = "Access forbidden"
    if permission:
        message = f"Access forbidden: requires '{permission}' permission"
    raise AuthorizationError(message, permission)


def raise_conflict(resource_type: str, resource_id: str, message: str = None):
    """Raise a conflict error."""
    if not message:
        message = f"Resource {resource_type} '{resource_id}' is in conflicting state"
    raise ConflictException(message, resource_type, resource_id)
