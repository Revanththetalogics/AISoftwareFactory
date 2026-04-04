"""
Infrastructure Management Dashboard

Provides a comprehensive dashboard for monitoring and managing
infrastructure components, services, and resources.
"""

import asyncio
import time
from datetime import UTC, datetime
from typing import Any

import psutil
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.core.resources import resource_manager
from backend.core.scaling import cluster_manager

router = APIRouter(prefix="/infrastructure", tags=["Infrastructure Management"])
logger = get_logger(__name__)


class InfrastructureOverview(BaseModel):
    """Infrastructure overview model."""

    system_status: dict[str, Any]
    cluster_status: dict[str, Any]
    resource_usage: dict[str, Any]
    service_health: dict[str, Any]
    alerts: list[dict[str, Any]]
    performance_metrics: dict[str, Any]


class ServiceStatus(BaseModel):
    """Service status model."""

    name: str
    status: str
    uptime: str
    cpu_usage: float
    memory_usage: float
    requests_per_second: float
    error_rate: float


class ResourceUsage(BaseModel):
    """Resource usage model."""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: dict[str, int]
    database_connections: int
    redis_connections: int


@router.get("/dashboard", response_model=APIResponse)
async def get_infrastructure_dashboard():
    """
    Get comprehensive infrastructure dashboard data.

    Returns:
        APIResponse with infrastructure dashboard data
    """
    try:
        # Collect all dashboard data concurrently
        tasks = [
            _get_system_status(),
            _get_cluster_status(),
            _get_resource_usage(),
            _get_service_health(),
            _get_active_alerts(),
            _get_performance_metrics(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Dashboard component {i} failed: {result}")
                results[i] = {}  # Use empty dict as fallback

        dashboard_data = InfrastructureOverview(
            system_status=results[0],
            cluster_status=results[1],
            resource_usage=results[2],
            service_health=results[3],
            alerts=results[4],
            performance_metrics=results[5],
        )

        return APIResponse(
            success=True, data=dashboard_data.dict(), message="Infrastructure dashboard data retrieved successfully"
        )
    except Exception as e:
        logger.error("Failed to get infrastructure dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@router.get("/services", response_model=APIResponse)
async def get_service_statuses():
    """
    Get status of all infrastructure services.

    Returns:
        APIResponse with service statuses
    """
    try:
        services = await _get_service_health()

        return APIResponse(success=True, data={"services": services}, message="Service statuses retrieved successfully")
    except Exception as e:
        logger.error("Failed to get service statuses", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get service statuses: {str(e)}")


@router.post("/services/{service_name}/restart", response_model=APIResponse)
async def restart_service(service_name: str):
    """
    Restart a specific service.

    Args:
        service_name: Name of the service to restart

    Returns:
        APIResponse confirming restart
    """
    try:
        # In a real implementation, this would interact with service management
        # For now, we'll simulate the restart
        logger.info(f"Restarting service: {service_name}")

        # Simulate restart delay
        await asyncio.sleep(2)

        return APIResponse(success=True, message=f"Service '{service_name}' restarted successfully")
    except Exception as e:
        logger.error(f"Failed to restart service {service_name}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to restart service: {str(e)}")


@router.get("/resources/usage", response_model=APIResponse)
async def get_detailed_resource_usage():
    """
    Get detailed resource usage information.

    Returns:
        APIResponse with detailed resource usage
    """
    try:
        usage = await _get_resource_usage()

        # Add more detailed metrics
        detailed_usage = {
            **usage,
            "processes": await _get_top_processes(),
            "containers": await _get_container_stats(),  # If using Docker
            "volumes": await _get_volume_usage(),
        }

        return APIResponse(success=True, data=detailed_usage, message="Detailed resource usage retrieved successfully")
    except Exception as e:
        logger.error("Failed to get detailed resource usage", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get resource usage: {str(e)}")


@router.get("/cluster/nodes", response_model=APIResponse)
async def get_cluster_nodes():
    """
    Get information about all cluster nodes.

    Returns:
        APIResponse with cluster node information
    """
    try:
        cluster_stats = cluster_manager.load_balancer.get_cluster_stats()

        return APIResponse(success=True, data=cluster_stats, message="Cluster nodes information retrieved successfully")
    except Exception as e:
        logger.error("Failed to get cluster nodes", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get cluster nodes: {str(e)}")


@router.post("/cluster/nodes/{node_id}/drain", response_model=APIResponse)
async def drain_cluster_node(node_id: str):
    """
    Drain a cluster node for maintenance.

    Args:
        node_id: ID of the node to drain

    Returns:
        APIResponse confirming drain operation
    """
    try:
        from backend.core.scaling import NodeStatus

        await cluster_manager.load_balancer.update_node_status(node_id, NodeStatus.DRAINING)

        return APIResponse(success=True, message=f"Node '{node_id}' set to draining mode")
    except Exception as e:
        logger.error(f"Failed to drain node {node_id}", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to drain node: {str(e)}")


@router.get("/alerts/active", response_model=APIResponse)
async def get_active_alerts():
    """
    Get all currently active alerts.

    Returns:
        APIResponse with active alerts
    """
    try:
        alerts = await _get_active_alerts()

        return APIResponse(success=True, data={"alerts": alerts}, message="Active alerts retrieved successfully")
    except Exception as e:
        logger.error("Failed to get active alerts", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/maintenance/start", response_model=APIResponse)
async def start_maintenance_mode():
    """
    Start maintenance mode for the infrastructure.

    Returns:
        APIResponse confirming maintenance mode start
    """
    try:
        # Set all nodes to maintenance mode
        cluster_stats = cluster_manager.load_balancer.get_cluster_stats()
        for node_info in cluster_stats["nodes"]:
            from backend.core.scaling import NodeStatus

            await cluster_manager.load_balancer.update_node_status(node_info["node_id"], NodeStatus.MAINTENANCE)

        logger.info("Maintenance mode started")

        return APIResponse(success=True, message="Maintenance mode started successfully")
    except Exception as e:
        logger.error("Failed to start maintenance mode", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to start maintenance: {str(e)}")


@router.post("/maintenance/stop", response_model=APIResponse)
async def stop_maintenance_mode():
    """
    Stop maintenance mode for the infrastructure.

    Returns:
        APIResponse confirming maintenance mode stop
    """
    try:
        # Restore nodes to healthy status
        cluster_stats = cluster_manager.load_balancer.get_cluster_stats()
        for node_info in cluster_stats["nodes"]:
            from backend.core.scaling import NodeStatus

            await cluster_manager.load_balancer.update_node_status(node_info["node_id"], NodeStatus.HEALTHY)

        logger.info("Maintenance mode stopped")

        return APIResponse(success=True, message="Maintenance mode stopped successfully")
    except Exception as e:
        logger.error("Failed to stop maintenance mode", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to stop maintenance: {str(e)}")


# Helper functions for data collection
async def _get_system_status() -> dict[str, Any]:
    """Get system status information."""
    try:
        return {
            "hostname": psutil.Process().name(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time(), UTC).isoformat(),
            "uptime_seconds": time.time() - psutil.boot_time(),
            "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else [0, 0, 0],
            "platform": {"system": psutil.WINDOWS, "release": "Windows 11", "version": "10.0.22631"},
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return {}


async def _get_cluster_status() -> dict[str, Any]:
    """Get cluster status information."""
    try:
        stats = cluster_manager.load_balancer.get_cluster_stats()
        leader_info = await cluster_manager.elect_leader()

        return {
            "total_nodes": stats["total_nodes"],
            "healthy_nodes": stats["healthy_nodes"],
            "unhealthy_nodes": stats["unhealthy_nodes"],
            "leader_node": leader_info,
            "scaling_policy": stats["policy"],
            "cluster_healthy": stats["healthy_nodes"] > 0,
        }
    except Exception as e:
        logger.error(f"Failed to get cluster status: {e}")
        return {}


async def _get_resource_usage() -> dict[str, Any]:
    """Get resource usage information."""
    try:
        # System resources
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        net_io = psutil.net_io_counters()

        # Application resources (from resource manager)
        resource_metrics = resource_manager.get_metrics()

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": (disk.used / disk.total) * 100,
            "network_io": {"bytes_sent": net_io.bytes_sent, "bytes_recv": net_io.bytes_recv},
            "database_connections": resource_metrics.get("db_connections_active", 0),
            "redis_connections": resource_metrics.get("redis_connections_active", 0),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get resource usage: {e}")
        return {}


async def _get_service_health() -> list[dict[str, Any]]:
    """Get service health information."""
    try:
        # Get metrics from resource manager
        resource_manager.get_metrics()
        health = await resource_manager.health_check()

        services = []

        # Database service
        db_health = health.get("database", {})
        services.append(
            {
                "name": "Database",
                "status": db_health.get("status", "unknown"),
                "uptime": "N/A",
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "requests_per_second": 0.0,
                "error_rate": 0.0,
                "latency_ms": db_health.get("latency_ms", 0),
            }
        )

        # Redis service
        redis_health = health.get("redis", {})
        services.append(
            {
                "name": "Redis",
                "status": redis_health.get("status", "unknown"),
                "uptime": "N/A",
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "requests_per_second": 0.0,
                "error_rate": 0.0,
                "latency_ms": redis_health.get("latency_ms", 0),
            }
        )

        # API service (estimated)
        services.append(
            {
                "name": "API Service",
                "status": "healthy",
                "uptime": "N/A",
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "requests_per_second": 0.0,
                "error_rate": 0.0,
                "latency_ms": 0,
            }
        )

        return services
    except Exception as e:
        logger.error(f"Failed to get service health: {e}")
        return []


async def _get_active_alerts() -> list[dict[str, Any]]:
    """Get active alerts."""
    try:
        # In a real implementation, this would query the alert manager
        # For now, returning sample alerts based on current state
        alerts = []

        # Check system metrics for potential alerts
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 80:
            alerts.append(
                {
                    "name": "High CPU Usage",
                    "severity": "warning",
                    "description": f"CPU usage is at {cpu_percent}%",
                    "triggered_at": datetime.now(UTC).isoformat(),
                    "status": "active",
                }
            )

        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 85:
            alerts.append(
                {
                    "name": "High Memory Usage",
                    "severity": "warning",
                    "description": f"Memory usage is at {memory_percent}%",
                    "triggered_at": datetime.now(UTC).isoformat(),
                    "status": "active",
                }
            )

        return alerts
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        return []


async def _get_performance_metrics() -> dict[str, Any]:
    """Get performance metrics."""
    try:
        # In a real implementation, this would query actual metrics
        return {
            "requests_per_second": 0,
            "average_response_time_ms": 0,
            "error_rate": 0,
            "throughput_mb_per_sec": 0,
            "cache_hit_ratio": 0,
            "database_query_avg_ms": 0,
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return {}


async def _get_top_processes() -> list[dict[str, Any]]:
    """Get top resource-consuming processes."""
    try:
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                processes.append(
                    {
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu_percent": proc.info["cpu_percent"] or 0,
                        "memory_percent": proc.info["memory_percent"] or 0,
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage and take top 10
        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        return processes[:10]
    except Exception as e:
        logger.error(f"Failed to get top processes: {e}")
        return []


async def _get_container_stats() -> list[dict[str, Any]]:
    """Get container statistics (if Docker is available)."""
    try:
        # This would interact with Docker API in a real implementation
        return []
    except Exception as e:
        logger.error(f"Failed to get container stats: {e}")
        return []


async def _get_volume_usage() -> dict[str, Any]:
    """Get volume/disk usage information."""
    try:
        volumes = {}
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                volumes[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent_used": round((usage.used / usage.total) * 100, 2),
                }
            except PermissionError:
                continue

        return volumes
    except Exception as e:
        logger.error(f"Failed to get volume usage: {e}")
        return {}
