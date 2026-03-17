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

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from backend.api import api_router
from backend.api.routes import websocket as websocket_routes
from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger
from backend.middleware import (
    CorrelationIdMiddleware,
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
)
from backend.middleware.error_handler import setup_exception_handlers

# Initialize logging on module load
configure_logging()
logger = get_logger(__name__)


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
    
    # Add middleware (order matters - executed in reverse for requests)
    # 1. Error handling (outermost)
    app.add_middleware(ErrorHandlerMiddleware)
    
    # 2. Request logging
    app.add_middleware(
        RequestLoggingMiddleware,
        exclude_paths=["/health", "/api/v1/health", "/metrics", "/ready", "/live"],
    )
    
    # 3. Correlation ID (innermost)
    app.add_middleware(CorrelationIdMiddleware)
    
    # 4. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
    
    # Validate critical configuration
    try:
        if settings.is_production:
            if settings.SECRET_KEY == "your-secret-key-change-in-production":
                logger.warning(
                    "Using default SECRET_KEY in production. "
                    "This should be changed for security."
                )
        
        logger.info("Configuration validated successfully")
        
    except Exception as exc:
        logger.error("Configuration validation failed", error=str(exc))
        raise
    
    # Initialize database connection
    try:
        from backend.db import init_db
        await init_db()
        logger.info("Database connection established")
    except Exception as exc:
        logger.error("Failed to initialize database", error=str(exc))
        # Don't raise - allow app to start without DB for health checks
    
    # Future: Initialize Redis connection (Phase 4)
    # Future: Load agent configurations (Phase 2)
    
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Handle application shutdown.
    
    This function is called when the application shuts down and performs
    cleanup tasks such as:
    - Closing database connections
    - Closing Redis connections
    - Graceful agent shutdown
    """
    logger.info("Application shutting down")
    
    # Future: Close database connections (Phase 5)
    # Future: Close Redis connections (Phase 4)
    # Future: Graceful agent shutdown (Phase 2)
    
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
if __name__ == "__main__":
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
