"""
Tests for database session management.

This module tests the database session management including
init_db, get_db, and get_db_context functions.
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestInitDb:
    """Test cases for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """Test init_db creates tables and enables extensions (lines 54-65)."""
        # Mock the engine
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        mock_engine_context = AsyncMock()
        mock_engine_context.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_engine_context.__aexit__ = AsyncMock(return_value=None)

        with patch('backend.db.session.engine') as mock_engine:
            mock_engine.begin.return_value = mock_engine_context

            # Import after patching
            from backend.db.session import init_db

            await init_db()

            # Verify pg_trgm extension was enabled
            mock_conn.execute.assert_called()
            # Verify create_all was called via run_sync
            mock_conn.run_sync.assert_called_once()


class TestGetDb:
    """Test cases for get_db async generator."""

    @pytest.mark.asyncio
    async def test_get_db_success(self):
        """Test get_db yields session and commits on success (lines 79-87)."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        # Create an async context manager for AsyncSessionLocal
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)

        with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_context):
            from backend.db.session import get_db

            # Use the async generator
            gen = get_db()
            session = await gen.__anext__()

            assert session == mock_session

            # Complete the generator normally
            try:
                await gen.__anext__()
            except StopAsyncIteration:
                pass

            # Should commit and close
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_exception_rollback(self):
        """Test get_db rolls back on exception (lines 83-85)."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock(side_effect=Exception("DB error"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)

        with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_context):
            from backend.db.session import get_db

            gen = get_db()
            await gen.__anext__()

            # Trying to finish the generator should rollback and raise
            with pytest.raises(Exception, match="DB error"):
                await gen.__anext__()

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()


class TestGetDbContext:
    """Test cases for get_db_context async context manager."""

    @pytest.mark.asyncio
    async def test_get_db_context_success(self):
        """Test get_db_context yields session and commits on success (lines 104-112)."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)

        with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_context):
            from backend.db.session import get_db_context

            async with get_db_context() as session:
                assert session == mock_session

            # Should commit and close
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_context_exception_rollback(self):
        """Test get_db_context rolls back on exception (lines 108-110)."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)

        with patch('backend.db.session.AsyncSessionLocal', return_value=mock_session_context):
            from backend.db.session import get_db_context

            with pytest.raises(ValueError, match="Test error"):
                async with get_db_context():
                    raise ValueError("Test error")

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
