"""
Tests for API Dependencies.
"""

import pytest
from fastapi import HTTPException

from backend.api.dependencies import (
    get_current_user,
    require_permissions,
    User,
)


class TestGetCurrentUser:
    """Test cases for get_current_user."""
    
    @pytest.mark.asyncio
    async def test_no_credentials(self):
        """Test anonymous access."""
        user = await get_current_user(None)
        
        assert user is not None
        assert user.user_id == "anonymous"
        assert "read" in user.permissions
    
    @pytest.mark.asyncio
    async def test_test_token(self):
        """Test with test token."""
        class MockCredentials:
            credentials = "test-token"
        
        user = await get_current_user(MockCredentials())
        
        assert user.user_id == "user-123"
        assert "write" in user.permissions


class TestRequirePermissions:
    """Test cases for require_permissions."""
    
    @pytest.mark.asyncio
    async def test_sufficient_permissions(self):
        """Test user with sufficient permissions."""
        user = User(
            user_id="user-123",
            username="test",
            email="test@example.com",
            permissions=["read", "write"],
        )
        
        result = await require_permissions(["read"], user)
        
        assert result.user_id == "user-123"
    
    @pytest.mark.asyncio
    async def test_insufficient_permissions(self):
        """Test user with insufficient permissions."""
        user = User(
            user_id="user-123",
            username="test",
            email="test@example.com",
            permissions=["read"],
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await require_permissions(["write"], user)
        
        assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_admin_override(self):
        """Test admin can access anything."""
        user = User(
            user_id="admin-123",
            username="admin",
            email="admin@example.com",
            permissions=["admin"],
        )
        
        result = await require_permissions(["write", "execute"], user)
        
        assert result.user_id == "admin-123"
    
    @pytest.mark.asyncio
    async def test_no_user(self):
        """Test no user provided."""
        with pytest.raises(HTTPException) as exc_info:
            await require_permissions(["read"], None)
        
        assert exc_info.value.status_code == 401
