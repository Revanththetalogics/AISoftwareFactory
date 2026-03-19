"""
Database session management for AI Software Factory.

This module provides database engine and session management
using SQLAlchemy with connection pooling.
"""

from typing import AsyncGenerator

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
    Initialize database tables.
    
    Creates all tables defined in models.
    Also enables required PostgreSQL extensions.
    """
    from backend.db.base import Base
    
    async with engine.begin() as conn:
        # Enable required extensions
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        logger.info("pg_trgm extension enabled")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables initialized")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        >>> async with get_db() as db:
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
