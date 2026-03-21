"""
Health checker for Infrastructure module.

This module provides health check endpoints and system monitoring
for service availability, including database connectivity,
schema integrity, and connection pool statistics.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

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
    details: dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """
    Health checker for service monitoring.

    Provides health check endpoints and component status monitoring,
    including database connectivity, schema validation, and connection
    pool statistics.
    """

    def __init__(self):
        """Initialize the health checker."""
        self._checks: dict[str, Callable] = {}
        self._logger = get_logger(__name__)

    def register_check(self, name: str, check_fn: Callable):
        """
        Register a health check.

        Args:
            name: Check name
            check_fn: Async function that returns (status, message, details)
        """
        self._checks[name] = check_fn
        self._logger.info("Health check registered", component=name)

    async def check_health(self) -> dict[str, Any]:
        """
        Run all health checks.

        Returns:
            Health status for all components including response times
        """
        results = []
        overall_status = HealthStatus.HEALTHY
        total_latency_ms = 0.0

        for name, check_fn in self._checks.items():
            start_time = time.time()

            try:
                check_result = await check_fn()
                # Support both (status, message) and (status, message, details) returns
                if len(check_result) == 3:
                    status, message, details = check_result
                else:
                    status, message = check_result
                    details = {}

                latency = (time.time() - start_time) * 1000
                total_latency_ms += latency

                result = HealthCheckResult(
                    component=name,
                    status=status,
                    message=message,
                    timestamp=datetime.utcnow(),
                    latency_ms=latency,
                    details=details
                )

                # Update overall status
                if status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED

            except Exception as e:
                latency = (time.time() - start_time) * 1000
                total_latency_ms += latency
                result = HealthCheckResult(
                    component=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                    timestamp=datetime.utcnow(),
                    latency_ms=latency,
                    details={"error_type": type(e).__name__}
                )
                overall_status = HealthStatus.UNHEALTHY

            results.append(result)

        return {
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "total_response_time_ms": round(total_latency_ms, 2),
            "components": [
                {
                    "name": r.component,
                    "status": r.status.value,
                    "message": r.message,
                    "latency_ms": round(r.latency_ms, 2),
                    "details": r.details
                }
                for r in results
            ]
        }

    async def check_database(self) -> tuple[HealthStatus, str, dict[str, Any]]:
        """
        Check database connectivity, query execution, and pool statistics.

        Returns:
            Tuple of (status, message, details) with connection pool info
        """
        from sqlalchemy import text

        details: dict[str, Any] = {}

        try:
            from backend.db.session import AsyncSessionLocal, engine

            # Get connection pool statistics
            pool = engine.pool
            details["pool_stats"] = {
                "size": pool.size() if hasattr(pool, 'size') else "N/A",
                "checkedin": pool.checkedin() if hasattr(pool, 'checkedin') else "N/A",
                "checkedout": pool.checkedout() if hasattr(pool, 'checkedout') else "N/A",
                "overflow": pool.overflow() if hasattr(pool, 'overflow') else "N/A",
            }

            # Test actual query execution with timing
            query_start = time.time()
            async with AsyncSessionLocal() as session:
                # Simple ping query
                result = await session.execute(text("SELECT 1"))
                result.fetchone()

            query_latency = (time.time() - query_start) * 1000
            details["query_latency_ms"] = round(query_latency, 2)

            # Verify critical tables exist
            critical_tables = ['users', 'projects', 'workflows', 'tasks']
            tables_ok = []
            tables_missing = []

            async with AsyncSessionLocal() as session:
                for table in critical_tables:
                    try:
                        await session.execute(text(f"SELECT 1 FROM {table} LIMIT 0"))
                        tables_ok.append(table)
                    except Exception:
                        tables_missing.append(table)

            details["schema"] = {
                "tables_verified": tables_ok,
                "tables_missing": tables_missing
            }

            # Determine status based on results
            if tables_missing:
                return (
                    HealthStatus.DEGRADED,
                    f"Database connected but missing tables: {tables_missing}",
                    details
                )

            # Check if query latency is too high (> 1000ms is concerning)
            if query_latency > 1000:
                return (
                    HealthStatus.DEGRADED,
                    f"Database slow: {query_latency:.0f}ms query latency",
                    details
                )

            return (
                HealthStatus.HEALTHY,
                f"Database OK ({query_latency:.1f}ms)",
                details
            )

        except Exception as e:
            details["error"] = str(e)
            return (
                HealthStatus.UNHEALTHY,
                f"Database error: {e}",
                details
            )

    async def check_redis(self) -> tuple[HealthStatus, str, dict[str, Any]]:
        """
        Check Redis connectivity with latency measurement.

        Returns:
            Tuple of (status, message, details)
        """
        details: dict[str, Any] = {}

        try:
            import redis.asyncio as redis

            from backend.core.config import get_settings

            settings = get_settings()

            ping_start = time.time()
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            ping_latency = (time.time() - ping_start) * 1000

            # Get Redis info
            try:
                info = await redis_client.info("server")
                details["redis_version"] = info.get("redis_version", "unknown")
            except Exception:
                pass

            await redis_client.close()

            details["ping_latency_ms"] = round(ping_latency, 2)

            if ping_latency > 100:
                return (
                    HealthStatus.DEGRADED,
                    f"Redis slow: {ping_latency:.0f}ms",
                    details
                )

            return (
                HealthStatus.HEALTHY,
                f"Redis OK ({ping_latency:.1f}ms)",
                details
            )

        except Exception as e:
            details["error"] = str(e)
            return (
                HealthStatus.UNHEALTHY,
                f"Redis error: {e}",
                details
            )

    async def check_disk_space(self) -> tuple[HealthStatus, str, dict[str, Any]]:
        """
        Check available disk space.

        Returns:
            Tuple of (status, message, details)
        """
        import shutil

        details: dict[str, Any] = {}

        try:
            total, used, free = shutil.disk_usage("/")
            total_gb = total / (1024**3)
            used_gb = used / (1024**3)
            free_gb = free / (1024**3)
            usage_percent = (used / total) * 100

            details["total_gb"] = round(total_gb, 2)
            details["used_gb"] = round(used_gb, 2)
            details["free_gb"] = round(free_gb, 2)
            details["usage_percent"] = round(usage_percent, 1)

            if free_gb < 1:
                return (
                    HealthStatus.UNHEALTHY,
                    f"Critical: {free_gb:.1f}GB free",
                    details
                )
            elif free_gb < 5:
                return (
                    HealthStatus.DEGRADED,
                    f"Low disk: {free_gb:.1f}GB free",
                    details
                )
            else:
                return (
                    HealthStatus.HEALTHY,
                    f"Disk OK: {free_gb:.1f}GB free ({usage_percent:.0f}% used)",
                    details
                )
        except Exception as e:
            details["error"] = str(e)
            return (
                HealthStatus.UNHEALTHY,
                f"Disk check error: {e}",
                details
            )

    def setup_default_checks(self):
        """Setup default health checks."""
        self.register_check("database", self.check_database)
        self.register_check("redis", self.check_redis)
        self.register_check("disk", self.check_disk_space)
