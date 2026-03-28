"""
Database Performance Monitoring API Endpoints.

Provides endpoints for monitoring and analyzing database performance.
"""

import time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.db.indexing import IndexAnalyzer, get_database_size_report, setup_performance_monitoring
from backend.db.performance import ConnectionPoolMonitor, QueryCache, QueryOptimizer
from backend.db.session import get_db

logger = get_logger(__name__)
router = APIRouter(prefix="/db-performance", tags=["Database Performance"])

# Global instances
query_optimizer = QueryOptimizer()
query_cache = QueryCache()

@router.get("/health")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive database health and performance check."""
    try:
        start_time = time.time()

        # Basic connectivity
        await db.execute("SELECT 1")
        connectivity_time = time.time() - start_time

        # Pool statistics
        from backend.db.session import engine
        pool_monitor = ConnectionPoolMonitor(engine)
        pool_stats = await pool_monitor.get_pool_stats()

        # Recent performance metrics
        QueryOptimizer()

        health_data = {
            "status": "healthy" if connectivity_time < 1.0 else "degraded",
            "connectivity_time_ms": round(connectivity_time * 1000, 2),
            "connection_pool": pool_stats,
            "is_over_utilized": pool_monitor.is_over_utilized(pool_stats),
            "timestamp": time.time()
        }

        return APIResponse(
            success=True,
            data=health_data,
            message="Database health check completed"
        )

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

@router.get("/statistics")
async def get_database_statistics(
    include_indexes: bool = Query(True, description="Include index statistics"),
    include_cache: bool = Query(False, description="Include cache statistics"),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive database statistics and performance metrics."""
    try:
        # Get database size report
        size_report = await get_database_size_report(db)

        # Get index statistics if requested
        index_stats = None
        if include_indexes:
            analyzer = IndexAnalyzer(db)
            index_stats = await analyzer.get_index_statistics()

        # Get connection pool info
        from backend.db.session import engine
        pool_monitor = ConnectionPoolMonitor(engine)
        pool_stats = await pool_monitor.get_pool_stats()

        # Cache statistics
        cache_stats = None
        if include_cache:
            cache_stats = {
                "cache_size": len(query_cache.cache),
                "ttl_seconds": query_cache.ttl
            }

        statistics = {
            "database_size": size_report.get("database_size"),
            "tables": size_report.get("table_sizes", []),
            "indexes": index_stats,
            "connection_pool": pool_stats,
            "cache": cache_stats,
            "generated_at": time.time()
        }

        return APIResponse(
            success=True,
            data=statistics,
            message="Database statistics retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@router.get("/index-analysis")
async def analyze_database_indexes(db: AsyncSession = Depends(get_db)):
    """Analyze current indexing and provide optimization recommendations."""
    try:
        analyzer = IndexAnalyzer(db)

        # Get existing indexes
        existing_indexes = await analyzer.get_existing_indexes()

        # Get recommendations
        recommendations = await analyzer.analyze_missing_indexes()
        index_sql = await analyzer.generate_index_recommendations()

        # Get unused indexes
        unused_indexes = await analyzer.find_unused_indexes()

        analysis = {
            "existing_indexes": existing_indexes,
            "missing_indexes": recommendations,
            "recommended_sql": index_sql,
            "unused_indexes": unused_indexes,
            "query_patterns": await analyzer.analyze_query_patterns()
        }

        return APIResponse(
            success=True,
            data=analysis,
            message="Index analysis completed"
        )

    except Exception as e:
        logger.error(f"Index analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Index analysis failed: {str(e)}")

@router.post("/setup-monitoring")
async def setup_database_monitoring(db: AsyncSession = Depends(get_db)):
    """Set up database performance monitoring tools and extensions."""
    try:
        await setup_performance_monitoring(db)

        return APIResponse(
            success=True,
            data={"message": "Performance monitoring setup completed"},
            message="Monitoring tools configured successfully"
        )

    except Exception as e:
        logger.error(f"Failed to setup monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Monitoring setup failed: {str(e)}")

@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = Query(50, ge=1, le=1000, description="Number of queries to return"),
    min_time_ms: float = Query(100.0, ge=0, description="Minimum execution time in milliseconds"),
    db: AsyncSession = Depends(get_db)
):
    """Get information about slow-running queries."""
    try:
        # Query pg_stat_statements for slow queries
        query = """
            SELECT
                query,
                calls,
                total_time,
                mean_time,
                min_time,
                max_time,
                stddev_time,
                rows,
                shared_blks_hit,
                shared_blks_read,
                shared_blks_dirtied,
                shared_blks_written
            FROM pg_stat_statements
            WHERE mean_time > :min_time
            ORDER BY mean_time DESC
            LIMIT :limit
        """

        result = await db.execute(query, {"min_time": min_time_ms, "limit": limit})
        slow_queries = [dict(row) for row in result.fetchall()]

        return APIResponse(
            success=True,
            data={
                "slow_queries": slow_queries,
                "count": len(slow_queries),
                "threshold_ms": min_time_ms
            },
            message="Slow queries retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail=f"Slow query analysis failed: {str(e)}")

@router.get("/query-optimization/{table_name}")
async def get_query_optimization_suggestions(
    table_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get query optimization suggestions for a specific table."""
    try:
        analyzer = IndexAnalyzer(db)

        # Get table-specific analysis
        table_analysis = {
            "table_name": table_name,
            "existing_indexes": await analyzer.get_existing_indexes(),
            "missing_indexes": await analyzer.analyze_missing_indexes(),
            "size_information": None,
            "access_patterns": None
        }

        # Get table size
        try:
            size_query = """
                SELECT
                    pg_size_pretty(pg_total_relation_size(:table_name)) as total_size,
                    pg_size_pretty(pg_relation_size(:table_name)) as table_size,
                    pg_size_pretty(pg_indexes_size(:table_name)) as indexes_size
            """
            size_result = await db.execute(size_query, {"table_name": f"public.{table_name}"})
            table_analysis["size_information"] = dict(size_result.fetchone()) if size_result.rowcount > 0 else None
        except Exception:
            table_analysis["size_information"] = "Unable to retrieve size information"

        return APIResponse(
            success=True,
            data=table_analysis,
            message=f"Optimization suggestions for {table_name}"
        )

    except Exception as e:
        logger.error(f"Failed to get optimization suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization analysis failed: {str(e)}")

@router.post("/analyze-query")
async def analyze_specific_query(
    query_text: str = Query(..., description="SQL query to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a specific query for performance issues."""
    try:
        # Use EXPLAIN ANALYZE to get query plan
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query_text}"

        result = await db.execute(explain_query)
        query_plan = result.fetchall()

        analysis = {
            "query": query_text,
            "execution_plan": query_plan,
            "suggestions": []
        }

        # Basic analysis of the query plan
        if query_plan:
            plan_data = query_plan[0][0]  # JSON format from EXPLAIN
            if isinstance(plan_data, list) and len(plan_data) > 0:
                plan = plan_data[0].get('Plan', {})

                # Look for common performance issues
                if plan.get('Node Type') == 'Seq Scan':
                    analysis["suggestions"].append("Consider adding indexes for sequential scan")

                if plan.get('Actual Rows', 0) > plan.get('Plan Rows', 0) * 10:
                    analysis["suggestions"].append("Statistics may be outdated - consider ANALYZE")

                cost = plan.get('Total Cost', 0)
                if cost > 1000:
                    analysis["suggestions"].append(f"High cost query ({cost}) - optimization recommended")

        return APIResponse(
            success=True,
            data=analysis,
            message="Query analysis completed"
        )

    except Exception as e:
        logger.error(f"Query analysis failed: {e}")
        raise HTTPException(status_code=400, detail=f"Query analysis failed: {str(e)}")

@router.get("/cache-statistics")
async def get_cache_statistics():
    """Get query cache statistics."""
    try:
        cache_stats = {
            "cache_size": len(query_cache.cache),
            "ttl_seconds": query_cache.ttl,
            "entries": [
                {
                    "key": key,
                    "age_seconds": time.time() - timestamp
                }
                for key, (_, timestamp) in query_cache.cache.items()
            ]
        }

        return APIResponse(
            success=True,
            data=cache_stats,
            message="Cache statistics retrieved"
        )

    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Cache statistics failed: {str(e)}")

@router.delete("/cache")
async def clear_query_cache():
    """Clear the query cache."""
    try:
        cache_size = len(query_cache.cache)
        query_cache.cache.clear()

        return APIResponse(
            success=True,
            data={"cleared_entries": cache_size},
            message=f"Cleared {cache_size} cached entries"
        )

    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clearing failed: {str(e)}")
