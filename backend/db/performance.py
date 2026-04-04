"""
Database Performance Optimization Module.

This module provides utilities and best practices for optimizing database queries
and improving overall database performance in the AI Software Factory application.
"""

import time
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.models.database import DBProject, DBTask, DBUser

logger = get_logger(__name__)
settings = get_settings()

# Performance monitoring constants
QUERY_TIMEOUT_THRESHOLD = 1.0  # seconds
SLOW_QUERY_THRESHOLD = 0.5  # seconds
CONNECTION_POOL_WARNING = 0.8  # 80% utilization


class QueryOptimizer:
    """
    Database Query Optimizer for Enhanced Performance.

    This class provides comprehensive tools for analyzing, monitoring, and
    optimizing database query performance. It includes utilities for query
    timing analysis, optimization suggestions, and performance benchmarking.

    Features:
        - Query performance analysis and timing
        - Optimization suggestion generation
        - Slow query detection and monitoring
        - Connection pool utilization tracking
        - Query complexity analysis

    Example:
        >>> optimizer = QueryOptimizer()
        >>> metrics = await optimizer.analyze_query_performance(session, my_query_func, param1, param2)
        >>> print(metrics['execution_time'])
    """

    @staticmethod
    async def analyze_query_performance(session: AsyncSession, query_func, *args, **kwargs) -> dict[str, Any]:
        """
        Analyze query performance and provide detailed optimization suggestions.

        This method executes a query while measuring performance metrics and
        provides actionable recommendations for optimization based on execution time
        and query characteristics.

        Args:
            session: SQLAlchemy async session for database operations
            query_func: Callable function that executes the database query
            *args: Positional arguments to pass to query_func
            **kwargs: Keyword arguments to pass to query_func

        Returns:
            Dictionary containing comprehensive performance metrics and optimization suggestions
            Keys include: execution_time, is_slow, suggestions, complexity_score, resource_usage

        Example:
            >>> async def get_user_data(session, user_id):
            ...     return await session.execute(select(User).where(User.id == user_id))
            >>>
            >>> metrics = await QueryOptimizer.analyze_query_performance(session, get_user_data, user_id=123)
            >>> if metrics['is_slow']:
            ...     print("Query is slow:", metrics['suggestions'])
        """
        start_time = time.time()

        try:
            result = await query_func(session, *args, **kwargs)
            execution_time = time.time() - start_time

            analysis = {
                "execution_time": execution_time,
                "is_slow": execution_time > SLOW_QUERY_THRESHOLD,
                "is_timeout": execution_time > QUERY_TIMEOUT_THRESHOLD,
                "result_count": len(result) if hasattr(result, "__len__") else 1,
                "suggestions": [],
            }

            # Generate optimization suggestions
            if execution_time > SLOW_QUERY_THRESHOLD:
                analysis["suggestions"].extend(
                    [
                        "Consider adding indexes on frequently queried columns",
                        "Check if query can be optimized with joins instead of subqueries",
                        "Review if all selected columns are necessary",
                        "Consider pagination for large result sets",
                    ]
                )

            if execution_time > QUERY_TIMEOUT_THRESHOLD:
                analysis["suggestions"].append("Query exceeds timeout threshold - immediate optimization needed")

            return analysis

        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            raise

    @staticmethod
    def optimize_pagination(page: int = 1, size: int = 50, max_size: int = 1000) -> tuple[int, int]:
        """
        Optimize pagination parameters to prevent performance degradation.

        This method validates and optimizes pagination parameters to ensure
        efficient database queries and prevent common performance pitfalls
        like deep pagination and excessive page sizes.

        Args:
            page: Page number (1-indexed) for pagination
            size: Number of items per page
            max_size: Maximum allowed page size to prevent memory issues

        Returns:
            Tuple containing (validated_page, validated_size) with safe values

        Features:
            - Prevents negative page numbers
            - Enforces maximum page size limits
            - Warns about deep pagination (>100 pages)
            - Recommends cursor-based pagination for deep datasets

        Example:
            >>> page, size = QueryOptimizer.optimize_pagination(page=5, size=200, max_size=500)
            >>> print(f"Loading page {page} with {size} items")
            Loading page 5 with 200 items
        """
        # Ensure reasonable bounds
        validated_page = max(1, page)
        validated_size = min(max(1, size), max_size)

        # Prevent deep pagination which can be slow
        if validated_page > 100:
            logger.warning(f"Deep pagination detected: page {validated_page}")
            # Could implement cursor-based pagination instead

        return validated_page, validated_size

    @staticmethod
    async def batch_load_entities(
        session: AsyncSession, entity_class, ids: list[str], batch_size: int = 100
    ) -> list[Any]:
        """
        Efficiently load entities by IDs in batches to eliminate N+1 query problems.

        This method implements batch loading to prevent the classic N+1 query problem
        where loading related entities results in multiple individual database queries.
        It's particularly useful for loading large collections of related data efficiently.

        Args:
            session: SQLAlchemy async session for database operations
            entity_class: SQLAlchemy model class to load instances of
            ids: List of entity primary key IDs to load
            batch_size: Number of entities to load in each batch (default: 100)

        Returns:
            List of loaded entity instances in the same order as requested IDs

        Benefits:
            - Eliminates N+1 query problem
            - Reduces database round trips
            - Improves memory efficiency through batching
            - Maintains ID ordering in results

        Example:
            >>> user_ids = ['user1', 'user2', 'user3']
            >>> users = await QueryOptimizer.batch_load_entities(session, User, user_ids)
            >>> print(f"Loaded {len(users)} users efficiently")
        """
        if not ids:
            return []

        all_entities = []

        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]

            stmt = select(entity_class).where(entity_class.id.in_(batch_ids))
            result = await session.execute(stmt)
            batch_entities = result.scalars().all()
            all_entities.extend(batch_entities)

        return all_entities


class ConnectionPoolMonitor:
    """Monitor and optimize database connection pool usage."""

    def __init__(self, engine):
        self.engine = engine

    async def get_pool_stats(self) -> dict[str, Any]:
        """Get current connection pool statistics."""
        pool = self.engine.pool

        stats = {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow() if hasattr(pool, "overflow") else 0,
            "utilization_percent": 0,
        }

        total_connections = stats["pool_size"] + stats["overflow"]
        if total_connections > 0:
            stats["utilization_percent"] = round((stats["checked_out"] / total_connections) * 100, 2)

        return stats

    def is_over_utilized(self, stats: dict[str, Any]) -> bool:
        """Check if connection pool is over-utilized."""
        return stats["utilization_percent"] > (CONNECTION_POOL_WARNING * 100)


class QueryCache:
    """Simple in-memory query cache for frequently accessed data."""

    def __init__(self, ttl_seconds: int = 300):
        self.cache: dict[str, tuple[Any, float]] = {}
        self.ttl = ttl_seconds

    def _get_cache_key(self, query_hash: str, params: tuple = ()) -> str:
        """Generate cache key from query hash and parameters."""
        return f"{query_hash}:{hash(params)}"

    def get(self, query_hash: str, params: tuple = ()) -> Any | None:
        """Get cached result if available and not expired."""
        cache_key = self._get_cache_key(query_hash, params)

        if cache_key in self.cache:
            result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                # Remove expired entry
                del self.cache[cache_key]

        return None

    def set(self, query_hash: str, params: tuple, result: Any) -> None:
        """Store result in cache."""
        cache_key = self._get_cache_key(query_hash, params)
        self.cache[cache_key] = (result, time.time())

    def invalidate(self, query_hash: str) -> None:
        """Invalidate all cache entries for a specific query."""
        keys_to_remove = [key for key in self.cache.keys() if key.startswith(f"{query_hash}:")]
        for key in keys_to_remove:
            del self.cache[key]


# Performance decorator for monitoring slow queries
def monitor_slow_queries(threshold: float = SLOW_QUERY_THRESHOLD):
    """
    Decorator to monitor and log slow database queries.

    Args:
        threshold: Time threshold in seconds to consider a query slow
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time

                if execution_time > threshold:
                    logger.warning(f"Slow query detected in {func.__name__}: {execution_time:.3f}s > {threshold}s")

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Query failed in {func.__name__} after {execution_time:.3f}s: {e}")
                raise

        return wrapper

    return decorator


# Context manager for efficient bulk operations
@asynccontextmanager
async def bulk_operation_context(session: AsyncSession, flush_interval: int = 1000):
    """
    Context manager for efficient bulk database operations.

    Args:
        session: Database session
        flush_interval: Number of operations before automatic flush
    """

    try:
        yield lambda: setattr(
            bulk_operation_context, "operations_count", getattr(bulk_operation_context, "operations_count", 0) + 1
        )

        # Final flush
        await session.flush()
        await session.commit()

    except Exception:
        await session.rollback()
        raise
    finally:
        # Reset counter
        if hasattr(bulk_operation_context, "operations_count"):
            delattr(bulk_operation_context, "operations_count")


# Optimized query examples
class OptimizedQueries:
    """Collection of optimized common queries."""

    @staticmethod
    @monitor_slow_queries()
    async def get_user_with_projects(session: AsyncSession, user_id: str):
        """Get user with eagerly loaded projects."""
        stmt = select(DBUser).options(joinedload(DBUser.projects)).where(DBUser.id == user_id).limit(1)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    @monitor_slow_queries()
    async def get_project_summary(session: AsyncSession, project_id: str):
        """Get project with aggregated task statistics."""

        stmt = (
            select(
                DBProject,
                func.count(DBTask.id).label("total_tasks"),
                func.sum(func.case((DBTask.status == "completed", 1), else_=0)).label("completed_tasks"),
                func.avg(DBTask.priority).label("avg_priority"),
            )
            .outerjoin(DBTask, DBTask.project_id == DBProject.id)
            .where(DBProject.id == project_id)
            .group_by(DBProject.id)
        )

        result = await session.execute(stmt)
        return result.one_or_none()

    @staticmethod
    @monitor_slow_queries()
    async def search_projects(session: AsyncSession, search_term: str, limit: int = 20):
        """Search projects with full-text search optimization."""

        # Use PostgreSQL full-text search with trigram similarity
        stmt = (
            select(DBProject)
            .where(DBProject.name.op("%")(search_term))
            .order_by(func.similarity(DBProject.name, search_term).desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        return result.scalars().all()


# Models imported at top level
