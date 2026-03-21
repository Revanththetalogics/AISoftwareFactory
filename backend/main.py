"""
AI Software Factory - Backend Application Entry Point

This module initializes and configures the FastAPI application with all
middleware, routes, and integrations for the AI Software Factory platform.

The application provides:
- RESTful API endpoints for project management
- Agent orchestration and workflow management
- Real-time communication via WebSockets
- Health monitoring and observability

Example:
    >>> uvicorn backend.main:app --reload --port 8000
"""

import asyncio
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from backend.api import api_router
from backend.api.routes import websocket as websocket_routes
from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger
from backend.infrastructure.tracing import setup_tracing
from backend.middleware import (
    AuthenticationMiddleware,
    CorrelationIdMiddleware,
    CSRFMiddleware,
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
)
from backend.middleware.error_handler import setup_exception_handlers
from backend.middleware.metrics_middleware import PrometheusMetricsMiddleware
from backend.middleware.rate_limit_middleware import RateLimitMiddleware

# Initialize logging on module load
configure_logging()
logger = get_logger(__name__)


async def _connect_with_retry(
    name: str,
    connect_fn: Callable[[], Awaitable[None]],
    max_retries: int = 3,
    delay: float = 2.0,
    critical: bool = False
) -> bool:
    """
    Attempt to connect to a service with retries.

    Args:
        name: Human-readable service name for logging
        connect_fn: Async function that attempts the connection
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
        critical: If True, raises exception on failure; if False, returns False

    Returns:
        bool: True if connection successful, False if non-critical service failed

    Raises:
        RuntimeError: If critical service fails to connect after all retries
    """
    for attempt in range(1, max_retries + 1):
        try:
            await connect_fn()
            logger.info(f"{name}: Connected successfully")
            return True
        except Exception as e:
            if attempt < max_retries:
                logger.warning(
                    f"{name}: Connection attempt {attempt}/{max_retries} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
            else:
                if critical:
                    logger.error(
                        f"{name}: CRITICAL - Failed to connect after {max_retries} attempts: {e}"
                    )
                    raise RuntimeError(
                        f"Failed to connect to critical service {name} after {max_retries} attempts"
                    ) from e
                else:
                    logger.warning(
                        f"{name}: Failed to connect after {max_retries} attempts: {e}. "
                        "Service will be unavailable."
                    )
                    return False


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This factory function creates a fully configured FastAPI application
    with all middleware, routes, and integrations.

    Returns:
        FastAPI: Configured application instance

    Example:
        >>> app = create_application()
        >>> # Use app for testing or ASGI server
    """
    settings = get_settings()

    # Create FastAPI application
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered software engineering platform for autonomous SaaS development",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        debug=settings.DEBUG,
    )

    # Setup exception handlers
    setup_exception_handlers(app)

    # Add middleware (order matters - last added runs first for requests)
    # Desired request flow: CORS → CSRF → Auth → Error Handler → Request Logging → Metrics → Correlation ID

    # 7. Correlation ID (innermost - runs last on requests)
    app.add_middleware(CorrelationIdMiddleware)

    # 6. Prometheus Metrics (captures request count, duration, active requests)
    app.add_middleware(
        PrometheusMetricsMiddleware,
        exclude_paths=["/health", "/api/v1/health", "/metrics", "/ready", "/live"],
    )

    # 5. Request logging
    app.add_middleware(
        RequestLoggingMiddleware,
        exclude_paths=["/health", "/api/v1/health", "/metrics", "/ready", "/live"],
    )

    # 4. Error handling
    app.add_middleware(ErrorHandlerMiddleware)

    # 3.5 Rate limiting (runs after auth, applies per-user limits)
    app.add_middleware(
        RateLimitMiddleware,
        default_rate=settings.RATE_LIMIT_DEFAULT,
        admin_rate=settings.RATE_LIMIT_ADMIN,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )

    # 3. Authentication (runs after CORS/CSRF, before error handling on requests)
    app.add_middleware(AuthenticationMiddleware)

    # 2. CSRF Protection (Double Submit Cookie pattern)
    app.add_middleware(CSRFMiddleware)

    # 1. CORS (outermost - runs first on requests)
    # SECURITY: Use explicit origins list, never use wildcards with credentials
    cors_origins = settings.cors_origins_list
    if not cors_origins and settings.is_development:
        # Allow localhost in development mode
        cors_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            allow_headers=["*"],
        )
    else:
        # No CORS in production without explicit origins
        logger.warning(
            "CORS not configured - no CORS_ORIGINS set. "
            "Cross-origin requests will be blocked."
        )

    # Include API routes
    app.include_router(api_router)

    # Include WebSocket routes
    app.include_router(websocket_routes.router)

    # Add metrics endpoint if enabled
    if settings.ENABLE_METRICS:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    return app


# Create application instance
app = create_application()


async def validate_database_schema() -> None:
    """
    Validate database schema integrity on startup.

    Verifies that critical tables exist and have expected structure.
    Does not fail the application startup - just logs warnings.
    """
    from sqlalchemy import text

    from backend.db.session import AsyncSessionLocal

    critical_tables = ['users', 'projects', 'workflows', 'tasks', 'agents', 'deployments', 'audit_logs']
    missing_tables = []

    async with AsyncSessionLocal() as session:
        for table in critical_tables:
            try:
                # Use SQLAlchemy inspector to safely check table existence
                from sqlalchemy import inspect
                inspector = await session.run_sync(lambda sync_session: inspect(sync_session.connection()))
                if table not in inspector.get_table_names():
                    missing_tables.append(table)
            except Exception as e:
                logger.debug(f"Error checking table {table}: {e}")
                missing_tables.append(table)

        if missing_tables:
            logger.warning(
                "Missing database tables detected",
                missing_tables=missing_tables,
                hint="Run 'alembic upgrade head' to create tables"
            )
        else:
            logger.info(
                "Database schema validation: OK",
                tables_verified=len(critical_tables)
            )

        # Check for critical indexes on users table
        try:
            result = await session.execute(text("""
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'users'
            """))
            indexes = [row[0] for row in result.fetchall()]
            expected_indexes = ['ix_users_username', 'ix_users_email', 'idx_users_active']
            missing_indexes = [idx for idx in expected_indexes if idx not in indexes]

            if missing_indexes:
                logger.warning(
                    "Missing recommended indexes on users table",
                    missing_indexes=missing_indexes
                )
        except Exception as e:
            logger.debug("Could not verify indexes", error=str(e))


@app.on_event("startup")
async def startup_event() -> None:
    """
    Handle application startup.

    This function is called when the application starts and performs
    initialization tasks such as:
    - Logging startup information
    - Validating configuration
    - Future: Database connections (Phase 5)
    - Future: Redis connections (Phase 4)
    - Future: Loading agent configurations (Phase 2)
    """
    settings = get_settings()

    logger.info(
        "Application starting up",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        debug=settings.DEBUG,
    )

    # Validate critical configuration - FATAL in non-development environments
    try:
        default_keys = ("your-secret-key-change-in-production", "change-me-in-production")
        if settings.SECRET_KEY in default_keys:
            if settings.ENVIRONMENT not in ("development", "testing"):
                logger.critical(
                    "FATAL: Default SECRET_KEY detected in %s environment!",
                    settings.ENVIRONMENT
                )
                raise SystemExit(
                    f"Cannot start with default SECRET_KEY in {settings.ENVIRONMENT} environment. "
                    "Please set a secure SECRET_KEY environment variable."
                )
            else:
                logger.warning(
                    "Using default SECRET_KEY in %s environment. "
                    "This is acceptable for development but must be changed for production.",
                    settings.ENVIRONMENT
                )

        logger.info("Configuration validated successfully")

    except Exception as exc:
        logger.error("Configuration validation failed", error=str(exc))
        raise

    # Log service connection details (mask password in database URL)
    db_url_display = settings.DATABASE_URL
    if '@' in db_url_display:
        parts = db_url_display.split('@')
        creds = parts[0].split('://')
        if len(creds) > 1:
            db_url_display = f"{creds[0]}://***@{parts[1]}"

    logger.info(
        "Service connection configuration",
        database_url=db_url_display,
        redis_url=settings.REDIS_URL,
        ollama_url=settings.OLLAMA_URL,
    )

    # Initialize database connection with retry (CRITICAL - must succeed)
    db_status = "disconnected"

    async def _init_database():
        from backend.db import init_db
        await init_db()

    try:
        db_connected = await _connect_with_retry(
            name="Database",
            connect_fn=_init_database,
            max_retries=3,
            delay=2.0,
            critical=True  # Database is critical - fail startup if can't connect
        )
        if db_connected:
            db_status = "connected"

            # Validate database schema on startup
            try:
                await validate_database_schema()
            except Exception as schema_exc:
                logger.warning(
                    "Database schema validation warning",
                    error=str(schema_exc),
                    hint="Run 'alembic upgrade head' to apply migrations"
                )

            # Create default admin user if no users exist
            try:
                from backend.services.auth_service import AuthService
                auth_service = AuthService()
                admin_user = await auth_service.create_default_admin()
                if admin_user:
                    logger.info(
                        "Default admin user created - CHANGE PASSWORD IMMEDIATELY",
                        username=admin_user.username,
                        email=admin_user.email
                    )
            except Exception as exc:
                logger.warning("Could not create default admin user", error=str(exc))

    except RuntimeError as exc:
        logger.error("Failed to initialize database", error=str(exc), status=db_status)
        # For critical database failure, we could choose to exit here
        # For now, allow app to start for health checks but log critical error

    # Initialize Redis connection with retry (non-critical)
    redis_status = "disconnected"

    async def _init_redis():
        import redis.asyncio as redis_lib
        redis_client = redis_lib.from_url(settings.REDIS_URL)
        await redis_client.ping()
        await redis_client.close()

    redis_connected = await _connect_with_retry(
        name="Redis",
        connect_fn=_init_redis,
        max_retries=3,
        delay=1.0,
        critical=False  # Redis is non-critical - warn and continue
    )
    if redis_connected:
        redis_status = "connected"

    # Test Ollama connection with retry (non-critical - optional service)
    ollama_status = "disconnected"

    async def _init_ollama():
        import httpx
        # Use httpx for safe HTTP requests with proper validation
        async with httpx.AsyncClient(verify=True) as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5.0)
            response.raise_for_status()

    ollama_connected = await _connect_with_retry(
        name="Ollama",
        connect_fn=_init_ollama,
        max_retries=2,
        delay=2.0,
        critical=False  # Ollama is optional - warn and continue
    )
    if ollama_connected:
        ollama_status = "connected"

    # Initialize OpenTelemetry tracing
    if settings.OTEL_ENABLED:
        tracing_provider = setup_tracing(
            app,
            service_name=settings.OTEL_SERVICE_NAME,
            otlp_endpoint=settings.OTEL_EXPORTER_ENDPOINT or None
        )
        if tracing_provider:
            logger.info(
                "OpenTelemetry tracing initialized",
                service_name=settings.OTEL_SERVICE_NAME,
                exporter_endpoint=settings.OTEL_EXPORTER_ENDPOINT or "none"
            )

    # Service status summary
    logger.info(
        "Service connectivity summary",
        database=db_status,
        redis=redis_status,
        ollama=ollama_status,
    )

    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Handle graceful application shutdown.

    This function is called when the application shuts down and performs
    cleanup tasks including:
    - Closing database connection pools
    - Closing Redis connections
    - Flushing logs
    """
    logger.info("Application shutting down gracefully...")

    # Close database connections
    try:
        from backend.db.session import engine
        if engine:
            await engine.dispose()
            logger.info("Database connections closed")
    except Exception as exc:
        logger.warning("Error closing database connections", error=str(exc))

    # Close Redis connections
    try:
        import redis.asyncio as redis_lib
        settings = get_settings()
        redis_client = redis_lib.from_url(settings.REDIS_URL)
        await redis_client.close()
        logger.info("Redis connections closed")
    except Exception as exc:
        logger.debug("Redis cleanup skipped", error=str(exc))

    logger.info("Application shutdown complete")


@app.get("/")
async def root() -> dict:
    """
    Root endpoint returning basic application information.

    Returns:
        dict: Application name and version

    Example:
        >>> curl http://localhost:8000/
        {
            "name": "AI Software Factory",
            "version": "1.0.0",
            "documentation": "/docs"
        }
    """
    settings = get_settings()
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "documentation": "/docs" if settings.is_development else None,
    }


# For running with: python -m backend.main
if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        workers=settings.WORKERS if not settings.is_development else 1,
        log_level=settings.LOG_LEVEL.lower(),
    )
