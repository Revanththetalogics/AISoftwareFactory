"""
Health check endpoints for AI Software Factory backend.

This module provides comprehensive health check endpoints for monitoring
application status, dependencies, and system health.
"""

import time
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from backend.core.config import get_settings
from backend.core.logging import get_correlation_id, get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthStatus(StrEnum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Health status of a single component."""
    name: str = Field(..., description="Component name")
    status: HealthStatus = Field(..., description="Component health status")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    message: str | None = Field(None, description="Optional status message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional details")


class HealthResponse(BaseModel):
    """
    Health check response model.

    This model provides comprehensive health information about the application
    and its dependencies.

    Attributes:
        status: Overall health status
        version: Application version
        timestamp: ISO format timestamp
        correlation_id: Request correlation ID
        uptime_seconds: Application uptime in seconds
        components: List of component health statuses
    """
    status: HealthStatus = Field(..., description="Overall health status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="ISO format timestamp")
    correlation_id: str = Field(..., description="Request correlation ID")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    components: list[ComponentHealth] = Field(
        default_factory=list,
        description="Component health statuses"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z",
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "uptime_seconds": 3600.5,
                "components": [
                    {
                        "name": "application",
                        "status": "healthy",
                        "response_time_ms": 0.5,
                        "message": "Application is running",
                        "details": {}
                    }
                ]
            }
        }
    }


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool = Field(..., description="Whether the application is ready to serve traffic")
    timestamp: str = Field(..., description="ISO format timestamp")
    checks: dict[str, bool] = Field(
        default_factory=dict,
        description="Individual readiness checks"
    )


class LivenessResponse(BaseModel):
    """Liveness check response model."""
    alive: bool = Field(..., description="Whether the application is alive")
    timestamp: str = Field(..., description="ISO format timestamp")


# Application start time for uptime calculation
_app_start_time: float = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive health check",
    description="Returns detailed health status of the application and all its components.",
    responses={
        200: {"description": "Application is healthy"},
        503: {"description": "Application is unhealthy or degraded"},
    },
)
async def health_check() -> HealthResponse:
    """
    Perform comprehensive health check.

    This endpoint checks:
    - Application status
    - Configuration validity
    - Future: Database connectivity (Phase 5)
    - Future: Redis connectivity (Phase 4)
    - Future: External service health

    Returns:
        HealthResponse: Comprehensive health status

    Example:
        >>> curl http://localhost:8000/api/v1/health
        {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": "2024-01-15T10:30:00Z",
            "correlation_id": "abc-123",
            "uptime_seconds": 3600.5,
            "components": [...]
        }
    """
    start_time = time.time()
    settings = get_settings()
    components: list[ComponentHealth] = []

    # Check application health
    try:
        app_check_start = time.time()

        # Verify configuration is loaded
        _ = settings.APP_NAME
        _ = settings.APP_VERSION

        app_response_time = (time.time() - app_check_start) * 1000

        components.append(
            ComponentHealth(
                name="application",
                status=HealthStatus.HEALTHY,
                response_time_ms=round(app_response_time, 2),
                message="Application is running normally",
                details={
                    "environment": settings.ENVIRONMENT,
                    "debug": settings.DEBUG,
                }
            )
        )

    except Exception as exc:
        components.append(
            ComponentHealth(
                name="application",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                message=f"Application check failed: {str(exc)}",
                details={"error": str(exc)}
            )
        )
        logger.error("Health check failed for application", error=str(exc))

    # Check configuration health
    try:
        config_check_start = time.time()

        # Validate critical configuration
        if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
            if settings.is_production:
                raise ValueError("SECRET_KEY not properly configured for production")

        config_response_time = (time.time() - config_check_start) * 1000

        components.append(
            ComponentHealth(
                name="configuration",
                status=HealthStatus.HEALTHY,
                response_time_ms=round(config_response_time, 2),
                message="Configuration is valid",
                details={
                    "environment": settings.ENVIRONMENT,
                    "log_level": settings.LOG_LEVEL,
                }
            )
        )

    except Exception as exc:
        components.append(
            ComponentHealth(
                name="configuration",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                message=f"Configuration check failed: {str(exc)}",
                details={"error": str(exc)}
            )
        )
        logger.error("Health check failed for configuration", error=str(exc))

    # Calculate overall status
    unhealthy_count = sum(
        1 for c in components if c.status == HealthStatus.UNHEALTHY
    )
    degraded_count = sum(
        1 for c in components if c.status == HealthStatus.DEGRADED
    )

    if unhealthy_count > 0:
        overall_status = HealthStatus.UNHEALTHY
    elif degraded_count > 0:
        overall_status = HealthStatus.DEGRADED  # pragma: no cover - future use
    else:
        overall_status = HealthStatus.HEALTHY

    response_time = (time.time() - start_time) * 1000

    logger.info(
        "Health check completed",
        status=overall_status.value,
        response_time_ms=round(response_time, 2),
        components_checked=len(components),
        correlation_id=get_correlation_id(),
    )

    return HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        correlation_id=get_correlation_id(),
        uptime_seconds=round(time.time() - _app_start_time, 2),
        components=components,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Returns whether the application is ready to serve traffic.",
)
async def readiness_check() -> ReadinessResponse:
    """
    Check if application is ready to serve traffic.

    This endpoint is used by orchestrators (Kubernetes, etc.) to determine
    if the application should receive traffic.

    Returns:
        ReadinessResponse: Readiness status

    Example:
        >>> curl http://localhost:8000/api/v1/ready
        {
            "ready": true,
            "timestamp": "2024-01-15T10:30:00Z",
            "checks": {"application": true}
        }
    """
    settings = get_settings()
    checks: dict[str, bool] = {}

    # Check application is configured
    try:
        _ = settings.APP_NAME
        checks["application"] = True
    except Exception:
        checks["application"] = False

    # Future: Check database connectivity (Phase 5)
    checks["database"] = True  # Stub for now

    # Future: Check Redis connectivity (Phase 4)
    checks["redis"] = True  # Stub for now

    all_ready = all(checks.values())

    return ReadinessResponse(
        ready=all_ready,
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        checks=checks,
    )


@router.get(
    "/live",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Returns whether the application is alive.",
)
async def liveness_check() -> LivenessResponse:
    """
    Check if application is alive.

    This endpoint is used by orchestrators (Kubernetes, etc.) to determine
    if the application should be restarted.

    Returns:
        LivenessResponse: Liveness status

    Example:
        >>> curl http://localhost:8000/api/v1/live
        {
            "alive": true,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    """
    return LivenessResponse(
        alive=True,
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )


@router.get(
    "/health/simple",
    status_code=status.HTTP_200_OK,
    summary="Simple health check",
    description="Returns a simple OK response for basic health checks.",
)
async def simple_health_check() -> dict[str, str]:
    """
    Simple health check endpoint.

    This is a lightweight endpoint for basic health checks that don't
    need detailed component status.

    Returns:
        dict: Simple status message

    Example:
        >>> curl http://localhost:8000/api/v1/health/simple
        {"status": "ok", "version": "1.0.0"}
    """
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
    }
