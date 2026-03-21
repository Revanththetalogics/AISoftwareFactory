"""
Database session management for AI Software Factory.

This module provides database engine and session management
using SQLAlchemy with connection pooling.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)

settings = get_settings()

# Convert PostgreSQL URL to async version
# postgresql:// -> postgresql+asyncpg://
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.is_development,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """
    Initialize database tables and extensions.

    For production environments, use Alembic migrations instead.
    This function is for development/local setup only.
    """
    from backend.db.base import Base

    async with engine.begin() as conn:
        # Enable required PostgreSQL extensions
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        logger.info("pg_trgm extension enabled")

        # Create all tables (development only - use alembic for production)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    logger.info("Database initialization complete")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as an async generator (for FastAPI Depends).

    Yields:
        AsyncSession: Database session

    Example:
        >>> async for db in get_db():
        ...     result = await db.execute(query)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session as an async context manager.

    Use this for standalone operations outside of FastAPI Depends.

    Yields:
        AsyncSession: Database session

    Example:
        >>> async with get_db_context() as db:
        ...     result = await db.execute(query)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Synchronous session for non-async contexts
SessionLocal = AsyncSessionLocal
