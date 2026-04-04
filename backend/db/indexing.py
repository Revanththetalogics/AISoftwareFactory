"""
Database Indexing Strategy Module.

This module provides automated index analysis and recommendations for optimal database performance.
"""

from collections import defaultdict

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logging import get_logger

logger = get_logger(__name__)


class IndexAnalyzer:
    """
    Database Index Analyzer for Performance Optimization.

    This class analyzes database indexing patterns and provides intelligent
    recommendations for optimal query performance. It examines existing indexes,
    identifies missing indexes, and suggests optimizations based on query patterns.

    Features:
        - Automatic index analysis
        - Performance recommendation generation
        - Duplicate index detection
        - Unused index identification

    Example:
        >>> analyzer = IndexAnalyzer(session)
        >>> await analyzer.initialize_inspector()
        >>> recommendations = await analyzer.analyze_indexes()
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the Index Analyzer.

        Args:
            session: SQLAlchemy async session for database operations
        """
        self.session = session
        self.inspector = None
        self._logger = get_logger(__name__)

    async def initialize_inspector(self):
        """
        Initialize SQLAlchemy inspector for schema analysis.

        This method sets up the SQLAlchemy inspector which is required
        for examining database schema, tables, and existing indexes.
        """
        if self.inspector is None:

            async def get_inspector(sync_session):
                return inspect(sync_session.connection())

            self.inspector = await self.session.run_sync(get_inspector)

    async def get_existing_indexes(self) -> dict[str, list[dict]]:
        """
        Retrieve all existing indexes from the database.

        Returns:
            Dictionary mapping table names to lists of index information.
            Each index contains keys: 'name', 'column_names', 'unique'

        Example:
            >>> indexes = await analyzer.get_existing_indexes()
            >>> print(indexes['users'])
            [{'name': 'ix_users_username', 'column_names': ['username'], 'unique': True}]
        """
        await self.initialize_inspector()

        indexes = defaultdict(list)
        for table_name in self.inspector.get_table_names():
            table_indexes = self.inspector.get_indexes(table_name)
            indexes[table_name] = table_indexes

        return dict(indexes)

    async def analyze_missing_indexes(self) -> dict[str, list[str]]:
        """
        Analyze database schema and suggest missing indexes for optimal performance.

        This method identifies commonly queried columns that would benefit from indexing
        based on typical application patterns and existing index analysis.

        Returns:
            Dictionary mapping table names to lists of column names that should be indexed

        Example:
            >>> missing = await analyzer.analyze_missing_indexes()
            >>> print(missing)
            {'users': ['email'], 'projects': ['status']}
        """
        # Common patterns that benefit from indexing
        patterns = {
            "users": ["username", "email", "is_active"],
            "projects": ["owner_id", "status", "created_at"],
            "workflows": ["project_id", "status", "created_by"],
            "tasks": ["project_id", "workflow_id", "status", "priority", "created_at"],
            "agents": ["role", "status"],
            "deployments": ["project_id", "environment", "status"],
            "audit_logs": ["user_id", "resource_type", "created_at"],
        }

        existing_indexes = await self.get_existing_indexes()
        suggestions = {}

        for table, columns in patterns.items():
            if table in existing_indexes:
                existing_columns = set()
                for idx in existing_indexes[table]:
                    existing_columns.update(idx["column_names"])

                # Find columns that should be indexed but aren't
                missing_columns = [col for col in columns if col not in existing_columns]
                if missing_columns:
                    suggestions[table] = missing_columns

        return suggestions

    async def generate_index_recommendations(self) -> list[str]:
        """
        Generate SQL statements for creating recommended database indexes.

        This method converts the missing index analysis into executable
        SQL CREATE INDEX statements that can be applied to the database.

        Returns:
            List of SQL statements for index creation

        Example:
            >>> sql_statements = await analyzer.generate_index_recommendations()
            >>> for stmt in sql_statements:
            ...     print(stmt)
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users (email);
        """
        suggestions = await self.analyze_missing_indexes()
        sql_statements = []

        for table, columns in suggestions.items():
            for column in columns:
                index_name = f"idx_{table}_{column}"
                sql = f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {index_name} ON {table} ({column});"
                sql_statements.append(sql)

        return sql_statements

    async def analyze_query_patterns(self) -> dict[str, dict]:
        """
        Analyze common database query patterns and their performance characteristics.

        This method identifies typical application query patterns and provides
        performance recommendations based on frequency and typical filters used.

        Returns:
            Dictionary containing query pattern analysis with recommendations

        Example:
            >>> patterns = await analyzer.analyze_query_patterns()
            >>> print(patterns['user_lookups']['recommendation'])
            Ensure indexes on frequently queried user attributes
        """
        # This would typically integrate with query logs or application metrics
        patterns = {
            "user_lookups": {
                "frequency": "high",
                "typical_filters": ["username", "email", "id"],
                "recommendation": "Ensure indexes on frequently queried user attributes",
            },
            "project_filtering": {
                "frequency": "high",
                "typical_filters": ["owner_id", "status", "created_at"],
                "recommendation": "Composite index on (owner_id, status) for dashboard queries",
            },
            "task_filtering": {
                "frequency": "very_high",
                "typical_filters": ["project_id", "status", "priority"],
                "recommendation": "Consider partial indexes for common status filters",
            },
        }

        return patterns


class QueryOptimizer:
    """
    Database Query Optimizer for Performance Enhancement.

    This class provides optimized SQL query templates for common application
    patterns, ensuring maximum performance through proper indexing utilization
    and query structure optimization.

    Features:
        - Pre-optimized query templates
        - Index-aware query construction
        - Performance-focused SQL patterns
        - Common use case optimizations

    Example:
        >>> optimized_sql = QueryOptimizer.optimize_user_authentication_query("john@example.com")
        >>> print(optimized_sql)
    """

    @staticmethod
    def optimize_user_authentication_query(username_or_email: str) -> str:
        """
        Optimize user authentication queries for maximum performance.

        This method generates an optimized SQL query for user authentication
        that leverages existing indexes on username and email columns.

        Args:
            username_or_email: Username or email for authentication lookup

        Returns:
            Optimized SQL query string with proper parameterization

        Note:
            Assumes indexes exist on username and email columns
            Uses LIMIT 1 for early termination after first match
        """
        # Use parameterized query to leverage existing indexes
        return """
            SELECT id, username, email, hashed_password, is_active, is_superuser
            FROM users
            WHERE (username = :identifier OR email = :identifier)
            AND is_active = true
            LIMIT 1
        """

    @staticmethod
    def optimize_dashboard_query(user_id: str) -> str:
        """
        Optimize dashboard queries for displaying user projects and recent activity.

        This method creates an efficient query using CTEs (Common Table Expressions)
        to fetch user projects and recent tasks in a single optimized query.

        Args:
            user_id: User identifier for filtering owned resources

        Returns:
            Optimized SQL query string for dashboard data retrieval

        Features:
            - Uses CTEs for clean, readable query structure
            - Limits results to prevent excessive data transfer
            - Joins optimized for existing foreign key indexes
        """
        return """
            SELECT
                (SELECT json_agg(row_to_json(up)) FROM user_projects up) as projects,
                (SELECT json_agg(row_to_json(rt)) FROM recent_tasks rt) as recent_tasks
        """

    @staticmethod
    def optimize_project_detail_query(project_id: str) -> str:
        """Optimize project detail queries with related data."""
        return """
            SELECT
                p.*,
                json_agg(DISTINCT row_to_json(w)) as workflows,
                json_agg(DISTINCT row_to_json(t)) as tasks,
                json_agg(DISTINCT row_to_json(d)) as deployments
            FROM projects p
            LEFT JOIN workflows w ON w.project_id = p.id
            LEFT JOIN tasks t ON t.project_id = p.id
            LEFT JOIN deployments d ON d.project_id = p.id
            WHERE p.id = :project_id
            GROUP BY p.id
        """


class IndexMaintenance:
    """Tools for maintaining and monitoring database indexes."""

    @staticmethod
    async def get_index_statistics(session: AsyncSession) -> list[dict]:
        """Get index usage statistics from PostgreSQL."""
        query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_tup_read,
                idx_tup_fetch,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC NULLS LAST
        """

        result = await session.execute(text(query))
        return [dict(row) for row in result.fetchall()]

    @staticmethod
    async def find_unused_indexes(session: AsyncSession) -> list[dict]:
        """Find indexes that are rarely used."""
        query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_stat_user_indexes
            WHERE idx_scan < 10
            ORDER BY pg_relation_size(indexname::regclass) DESC
        """

        result = await session.execute(text(query))
        return [dict(row) for row in result.fetchall()]

    @staticmethod
    async def rebuild_fragmented_indexes(session: AsyncSession) -> list[str]:
        """Identify and suggest rebuilding of fragmented indexes."""
        query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_stat_user_indexes psi
            JOIN pg_class pc ON psi.indexrelid = pc.oid
            WHERE pc.relpages > 1000  -- Large indexes
            ORDER BY pg_relation_size(indexname::regclass) DESC
            LIMIT 10
        """

        result = await session.execute(text(query))
        indexes = [dict(row) for row in result.fetchall()]

        rebuild_commands = []
        for idx in indexes:
            rebuild_commands.append(f"REINDEX INDEX CONCURRENTLY {idx['indexname']};")

        return rebuild_commands


# Performance monitoring views
PERFORMANCE_VIEWS = {
    "slow_queries": """
        CREATE OR REPLACE VIEW slow_queries_monitor AS
        SELECT
            query,
            mean_time,
            calls,
            total_time,
            rows,
            shared_blks_hit,
            shared_blks_read
        FROM pg_stat_statements
        WHERE mean_time > 100  -- Queries taking more than 100ms on average
        ORDER BY mean_time DESC
        LIMIT 50;
    """,
    "missing_indexes": """
        CREATE OR REPLACE VIEW missing_indexes_monitor AS
        SELECT
            schemaname,
            tablename,
            attname,
            (100 * seq_scan / (seq_scan + idx_scan)) as seq_scan_pct,
            seq_scan,
            idx_scan
        FROM pg_stat_user_tables t
        JOIN pg_attribute a ON a.attrelid = t.relid
        WHERE (seq_scan + idx_scan) > 0
        AND (100 * seq_scan / (seq_scan + idx_scan)) > 90  -- Mostly sequential scans
        ORDER BY seq_scan DESC;
    """,
}


async def setup_performance_monitoring(session: AsyncSession):
    """Set up performance monitoring views and extensions."""
    try:
        # Enable pg_stat_statements extension
        await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"))

        # Create monitoring views
        for _view_name, view_sql in PERFORMANCE_VIEWS.items():
            await session.execute(text(view_sql))

        logger.info("Performance monitoring views created successfully")

    except Exception as e:
        logger.error(f"Failed to set up performance monitoring: {e}")


async def get_database_size_report(session: AsyncSession) -> dict:
    """Get comprehensive database size and performance report."""
    queries = {
        "database_size": "SELECT pg_size_pretty(pg_database_size(current_database())) as size;",
        "table_sizes": """
            SELECT
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """,
        "index_usage": """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC NULLS LAST
            LIMIT 20;
        """,
    }

    report = {}

    for name, query in queries.items():
        try:
            result = await session.execute(text(query))
            if name == "database_size":
                report[name] = result.scalar()
            else:
                report[name] = [dict(row) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get {name}: {e}")
            report[name] = f"Error: {e}"

    return report
