"""
API Dependencies for AI Software Factory.

This module provides dependency injection for authentication, authorization,
and common services.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.core.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


class User:
    """User model for authentication."""
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        permissions: list[str],
        is_active: bool = True,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.permissions = permissions
        self.is_active = is_active


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """
    Get current authenticated user.
    
    This is a stub implementation. In production, this would:
    - Validate JWT tokens
    - Check token expiration
    - Fetch user from database
    - Verify user is active
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        User object or None for unauthenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    # Stub: Allow unauthenticated access for development
    if not credentials:
        return User(
            user_id="anonymous",
            username="anonymous",
            email="anonymous@example.com",
            permissions=["read"],
        )
    
    # Stub: Validate token format
    token = credentials.credentials
    if token == "test-token":
        return User(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            permissions=["read", "write", "execute"],
        )
    
    # For development, accept any token
    return User(
        user_id="dev-user",
        username="developer",
        email="dev@example.com",
        permissions=["read", "write", "execute", "admin"],
    )


async def require_permissions(
    required_permissions: list[str],
    user: Optional[User] = Depends(get_current_user),
) -> User:
    """
    Require specific permissions for access.
    
    Args:
        required_permissions: List of required permission strings
        user: Current user from dependency
        
    Returns:
        User object if authorized
        
    Raises:
        HTTPException: If user lacks required permissions
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user has all required permissions
    missing = [p for p in required_permissions if p not in user.permissions]
    if missing and "admin" not in user.permissions:
        logger.warning(
            "Permission denied",
            user_id=user.user_id,
            required=required_permissions,
            missing=missing,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permissions: {', '.join(missing)}",
        )
    
    return user


async def get_websocket_user(websocket: WebSocket) -> Optional[User]:
    """
    Get user from WebSocket connection.
    
    Args:
        websocket: WebSocket connection
        
    Returns:
        User object or None
    """
    # Stub: Extract token from query params or headers
    token = websocket.query_params.get("token")
    
    if token == "test-token":
        return User(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            permissions=["read", "write", "execute"],
        )
    
    # Allow anonymous connections for development
    return User(
        user_id="anonymous",
        username="anonymous",
        email="anonymous@example.com",
        permissions=["read"],
    )


# Common dependency aliases
require_auth = Depends(get_current_user)
require_write = Depends(lambda: require_permissions(["write"]))
require_execute = Depends(lambda: require_permissions(["execute"]))
require_admin = Depends(lambda: require_permissions(["admin"]))
