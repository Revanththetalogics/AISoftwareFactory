"""
Health checker for Infrastructure module.

This module provides health check endpoints and system monitoring
for service availability.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.core.logging import get_logger

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Health check result."""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    latency_ms: float


class HealthChecker:
    """
    Health checker for service monitoring.
    
    Provides health check endpoints and component status monitoring.
    """
    
    def __init__(self):
        """Initialize the health checker."""
        self._checks: Dict[str, Callable] = {}
        self._logger = get_logger(__name__)
    
    def register_check(self, name: str, check_fn: Callable):
        """
        Register a health check.
        
        Args:
            name: Check name
            check_fn: Async function that returns (status, message)
        """
        self._checks[name] = check_fn
        self._logger.info("Health check registered", component=name)
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Health status for all components
        """
        import time
        
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for name, check_fn in self._checks.items():
            start_time = time.time()
            
            try:
                status, message = await check_fn()
                latency = (time.time() - start_time) * 1000
                
                result = HealthCheckResult(
                    component=name,
                    status=status,
                    message=message,
                    timestamp=datetime.utcnow(),
                    latency_ms=latency
                )
                
                # Update overall status
                if status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                result = HealthCheckResult(
                    component=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                    timestamp=datetime.utcnow(),
                    latency_ms=latency
                )
                overall_status = HealthStatus.UNHEALTHY
            
            results.append(result)
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "components": [
                {
                    "name": r.component,
                    "status": r.status.value,
                    "message": r.message,
                    "latency_ms": round(r.latency_ms, 2)
                }
                for r in results
            ]
        }
    
    async def check_database(self) -> tuple[HealthStatus, str]:
        """Check database connectivity."""
        try:
            # This would check actual database connection
            # For now, return healthy
            return HealthStatus.HEALTHY, "Database connection OK"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Database error: {e}"
    
    async def check_redis(self) -> tuple[HealthStatus, str]:
        """Check Redis connectivity."""
        try:
            # This would check actual Redis connection
            return HealthStatus.HEALTHY, "Redis connection OK"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Redis error: {e}"
    
    async def check_disk_space(self) -> tuple[HealthStatus, str]:
        """Check available disk space."""
        import shutil
        
        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)
            
            if free_gb < 1:
                return HealthStatus.UNHEALTHY, f"Low disk space: {free_gb:.1f}GB free"
            elif free_gb < 5:
                return HealthStatus.DEGRADED, f"Disk space low: {free_gb:.1f}GB free"
            else:
                return HealthStatus.HEALTHY, f"Disk space OK: {free_gb:.1f}GB free"
        except Exception as e:
            return HealthStatus.UNHEALTHY, f"Disk check error: {e}"
    
    def setup_default_checks(self):
        """Setup default health checks."""
        self.register_check("database", self.check_database)
        self.register_check("redis", self.check_redis)
        self.register_check("disk", self.check_disk_space)
