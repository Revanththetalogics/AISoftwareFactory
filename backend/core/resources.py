"""
Enhanced Resource Management

Provides connection pooling, lifecycle management, and monitoring
for database and Redis connections.
"""

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

from backend.core.config import get_settings
from backend.core.exceptions import CacheError, DatabaseError
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

class ResourceManager:
    """Centralized resource manager for database and cache connections."""

    def __init__(self):
        self._db_engine = None
        self._db_session_factory = None
        self._redis_pool = None
        self._redis_client = None
        self._initialized = False
        self._metrics = {
            'db_connections_active': 0,
            'db_connections_total': 0,
            'redis_connections_active': 0,
            'redis_connections_total': 0,
            'db_connection_errors': 0,
            'redis_connection_errors': 0
        }

    async def initialize(self):
        """Initialize all resources."""
        if self._initialized:
            return

        try:
            await self._initialize_database()
            await self._initialize_redis()
            self._initialized = True
            logger.info("Resource manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize resource manager: {e}")
            raise

    async def _initialize_database(self):
        """Initialize database connection pool."""
        try:
            # Create async engine with connection pooling
            self._db_engine = create_async_engine(
                settings.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=settings.DB_POOL_RECYCLE,
                echo=settings.DEBUG,
                connect_args={
                    "server_settings": {
                        "application_name": "theta_ai_backend"
                    }
                }
            )

            # Create session factory
            self._db_session_factory = async_sessionmaker(
                bind=self._db_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False
            )

            # Test connection
            async with self._db_engine.connect() as conn:
                await conn.execute("SELECT 1")

            logger.info(
                "Database connection pool initialized",
                extra={
                    "pool_size": settings.DB_POOL_SIZE,
                    "max_overflow": settings.DB_MAX_OVERFLOW
                }
            )

        except Exception as e:
            self._metrics['db_connection_errors'] += 1
            raise DatabaseError(f"Failed to initialize database: {str(e)}", "initialize")

    async def _initialize_redis(self):
        """Initialize Redis connection pool."""
        try:
            # Create connection pool
            self._redis_pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={
                    60: 30,  # TCP_KEEPIDLE
                    61: 10,  # TCP_KEEPINTVL
                    62: 3    # TCP_KEEPCNT
                }
            )

            # Create Redis client
            self._redis_client = Redis(connection_pool=self._redis_pool)

            # Test connection
            await self._redis_client.ping()

            logger.info(
                "Redis connection pool initialized",
                extra={
                    "pool_size": settings.REDIS_POOL_SIZE
                }
            )

        except Exception as e:
            self._metrics['redis_connection_errors'] += 1
            raise CacheError(f"Failed to initialize Redis: {str(e)}", "initialize")

    @asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup."""
        if not self._initialized:
            await self.initialize()

        session = None
        start_time = time.time()

        try:
            self._metrics['db_connections_active'] += 1
            self._metrics['db_connections_total'] += 1

            session = self._db_session_factory()

            logger.debug("Database session acquired")

            yield session

            # Commit if no exceptions occurred
            if session.is_active:
                await session.commit()

        except Exception:
            # Rollback on error
            if session and session.is_active:
                await session.rollback()
            self._metrics['db_connection_errors'] += 1
            raise
        finally:
            # Always close the session
            if session:
                await session.close()
                self._metrics['db_connections_active'] -= 1

            duration = time.time() - start_time
            logger.debug(
                "Database session released",
                extra={
                    "duration_ms": round(duration * 1000, 2),
                    "active_connections": self._metrics['db_connections_active']
                }
            )

    def get_redis_client(self) -> Redis:
        """Get Redis client instance."""
        if not self._initialized:
            raise CacheError("Resource manager not initialized", "get_client")

        if not self._redis_client:
            raise CacheError("Redis client not available", "get_client")

        self._metrics['redis_connections_active'] += 1
        self._metrics['redis_connections_total'] += 1

        return self._redis_client

    async def close_redis_connection(self, client: Redis):
        """Close Redis connection."""
        self._metrics['redis_connections_active'] -= 1
        # Note: In connection pool, we don't actually close individual connections
        # They're managed by the pool

    async def shutdown(self):
        """Gracefully shutdown all resources."""
        logger.info("Shutting down resource manager")

        # Close database engine
        if self._db_engine:
            await self._db_engine.dispose()
            logger.info("Database engine disposed")

        # Close Redis pool
        if self._redis_pool:
            await self._redis_pool.disconnect()
            logger.info("Redis pool disconnected")

        self._initialized = False
        logger.info("Resource manager shutdown complete")

    def get_metrics(self) -> dict[str, Any]:
        """Get current resource metrics."""
        return {
            **self._metrics,
            'uptime': datetime.now(UTC).isoformat(),
            'db_pool_initialized': self._db_engine is not None,
            'redis_pool_initialized': self._redis_pool is not None
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on all resources."""
        health_status = {
            'database': {'status': 'unknown', 'latency_ms': None},
            'redis': {'status': 'unknown', 'latency_ms': None}
        }

        # Check database
        try:
            start_time = time.time()
            async with self.get_db_session() as session:
                result = await session.execute("SELECT 1")
                latency = round((time.time() - start_time) * 1000, 2)
                health_status['database'] = {
                    'status': 'healthy',
                    'latency_ms': latency
                }
        except Exception as e:
            health_status['database'] = {
                'status': 'unhealthy',
                'error': str(e),
                'latency_ms': None
            }
            logger.error(f"Database health check failed: {e}")

        # Check Redis
        try:
            start_time = time.time()
            redis_client = self.get_redis_client()
            await redis_client.ping()
            latency = round((time.time() - start_time) * 1000, 2)
            health_status['redis'] = {
                'status': 'healthy',
                'latency_ms': latency
            }
            await self.close_redis_connection(redis_client)
        except Exception as e:
            health_status['redis'] = {
                'status': 'unhealthy',
                'error': str(e),
                'latency_ms': None
            }
            logger.error(f"Redis health check failed: {e}")

        return health_status

# Global resource manager instance
resource_manager = ResourceManager()

# Convenience functions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session."""
    async with resource_manager.get_db_session() as session:
        yield session

def get_redis() -> Redis:
    """Get Redis client (synchronous function for dependency injection)."""
    return resource_manager.get_redis_client()

async def close_redis(client: Redis):
    """Close Redis connection."""
    await resource_manager.close_redis_connection(client)

# Connection pool monitoring
class ConnectionMonitor:
    """Monitor connection pool health and performance."""

    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self._monitoring_task = None
        self._stop_event = asyncio.Event()

    async def start_monitoring(self):
        """Start connection monitoring."""
        if self._monitoring_task and not self._monitoring_task.done():
            return

        self._stop_event.clear()
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Connection monitoring started")

    async def stop_monitoring(self):
        """Stop connection monitoring."""
        self._stop_event.set()
        if self._monitoring_task:
            await self._monitoring_task
        logger.info("Connection monitoring stopped")

    async def _monitor_loop(self):
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            try:
                await self._perform_monitoring()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.interval)

    async def _perform_monitoring(self):
        """Perform actual monitoring tasks."""
        metrics = resource_manager.get_metrics()

        # Log metrics
        logger.info(
            "Connection pool metrics",
            extra=metrics
        )

        # Check for problematic states
        if metrics['db_connections_active'] > settings.DB_POOL_SIZE * 0.8:
            logger.warning(
                "High database connection usage",
                extra={'active': metrics['db_connections_active']}
            )

        if metrics['redis_connections_active'] > settings.REDIS_POOL_SIZE * 0.8:
            logger.warning(
                "High Redis connection usage",
                extra={'active': metrics['redis_connections_active']}
            )

        # Perform health check periodically
        if metrics['db_connection_errors'] > 0 or metrics['redis_connection_errors'] > 0:
            health = await resource_manager.health_check()
            unhealthy_services = [
                service for service, status in health.items()
                if status['status'] == 'unhealthy'
            ]

            if unhealthy_services:
                logger.error(
                    "Unhealthy services detected",
                    extra={'services': unhealthy_services}
                )

# Global monitor instance
connection_monitor = ConnectionMonitor()
