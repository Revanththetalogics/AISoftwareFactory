"""
Resource Management API Routes

Provides endpoints for monitoring and managing database and Redis connections.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.core.resources import connection_monitor, resource_manager

router = APIRouter(prefix="/resources", tags=["Resource Management"])
logger = get_logger(__name__)


class ResourceMetrics(BaseModel):
    """Resource metrics response model."""

    db_connections_active: int
    db_connections_total: int
    redis_connections_active: int
    redis_connections_total: int
    db_connection_errors: int
    redis_connection_errors: int
    db_pool_initialized: bool
    redis_pool_initialized: bool
    uptime: str


class HealthStatus(BaseModel):
    """Health status response model."""

    database: dict[str, Any]
    redis: dict[str, Any]


@router.get("/metrics", response_model=APIResponse)
async def get_resource_metrics():
    """
    Get current resource usage metrics.

    Returns:
        APIResponse with resource metrics
    """
    try:
        metrics = resource_manager.get_metrics()

        return APIResponse(success=True, data=metrics, message="Resource metrics retrieved successfully")
    except Exception as e:
        logger.error("Failed to get resource metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/health", response_model=APIResponse)
async def get_resource_health():
    """
    Get health status of all resources.

    Returns:
        APIResponse with health status
    """
    try:
        health = await resource_manager.health_check()

        # Determine overall status
        overall_healthy = all(status["status"] == "healthy" for status in health.values())

        return APIResponse(success=overall_healthy, data=health, message="Health check completed")
    except Exception as e:
        logger.error("Failed to perform health check", error=str(e))
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/monitor/start", response_model=APIResponse)
async def start_monitoring():
    """
    Start connection monitoring.

    Returns:
        APIResponse confirming monitoring started
    """
    try:
        await connection_monitor.start_monitoring()

        return APIResponse(success=True, message="Connection monitoring started")
    except Exception as e:
        logger.error("Failed to start monitoring", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/monitor/stop", response_model=APIResponse)
async def stop_monitoring():
    """
    Stop connection monitoring.

    Returns:
        APIResponse confirming monitoring stopped
    """
    try:
        await connection_monitor.stop_monitoring()

        return APIResponse(success=True, message="Connection monitoring stopped")
    except Exception as e:
        logger.error("Failed to stop monitoring", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.post("/refresh", response_model=APIResponse)
async def refresh_resources():
    """
    Refresh and reinitialize resources.

    Returns:
        APIResponse confirming resources refreshed
    """
    try:
        # Shutdown existing resources
        await resource_manager.shutdown()

        # Reinitialize
        await resource_manager.initialize()

        return APIResponse(success=True, message="Resources refreshed successfully")
    except Exception as e:
        logger.error("Failed to refresh resources", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to refresh resources: {str(e)}")


@router.get("/status", response_model=APIResponse)
async def get_resource_status():
    """
    Get comprehensive resource status.

    Returns:
        APIResponse with detailed resource status
    """
    try:
        metrics = resource_manager.get_metrics()
        health = await resource_manager.health_check()

        status = {
            "metrics": metrics,
            "health": health,
            "monitoring_enabled": connection_monitor._monitoring_task is not None
            and not connection_monitor._monitoring_task.done(),
        }

        return APIResponse(success=True, data=status, message="Resource status retrieved successfully")
    except Exception as e:
        logger.error("Failed to get resource status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
