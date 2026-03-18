"""
API Dependencies for AI Software Factory.

This module provides dependency injection for authentication, authorization,
and common services.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.core.logging import get_logger
from backend.services.auth_service import get_auth_service, AuthService
from backend.core.exceptions import AuthenticationError, AuthorizationError

logger = get_logger(__name__)
security = HTTPBearer(auto_error=True)


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
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Get current authenticated user by validating JWT token.
    
    Args:
        credentials: HTTP authorization credentials containing JWT token
        auth_service: Authentication service instance
        
    Returns:
        User object for authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Decode and validate the JWT token
        payload = auth_service.decode_token(credentials.credentials)
        
        # Extract user information from token
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            logger.warning("Token missing required fields")
            raise AuthenticationError("Invalid token format")
        
        # In production, fetch user from database
        # For now, create mock user based on token data
        mock_users = {
            "user-admin-001": {
                "user_id": "user-admin-001",
                "username": "admin",
                "email": "admin@example.com",
                "permissions": ["read", "write", "execute", "admin"],
                "is_active": True
            },
            "user-dev-001": {
                "user_id": "user-dev-001",
                "username": "developer",
                "email": "dev@example.com", 
                "permissions": ["read", "write", "execute"],
                "is_active": True
            }
        }
        
        user_data = mock_users.get(user_id)
        if not user_data:
            logger.warning("User not found", user_id=user_id)
            raise AuthenticationError("User not found")
            
        if not user_data["is_active"]:
            logger.warning("Inactive user", user_id=user_id)
            raise AuthenticationError("Account is inactive")
        
        logger.info("User authenticated", user_id=user_id, username=username)
        
        return User(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            permissions=user_data["permissions"],
            is_active=user_data["is_active"]
        )
        
    except AuthenticationError as exc:
        logger.warning("Authentication failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_permissions(
    required_permissions: list[str],
    user: User = Depends(get_current_user),
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
    # Admin users bypass permission checks
    if "admin" in user.permissions:
        return user
    
    # Check if user has all required permissions
    missing = [p for p in required_permissions if p not in user.permissions]
    if missing:
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


async def get_websocket_user(
    websocket: WebSocket,
    auth_service: AuthService = Depends(get_auth_service),
) -> Optional[User]:
    """
    Get user from WebSocket connection.
    
    Args:
        websocket: WebSocket connection
        auth_service: Authentication service instance
        
    Returns:
        User object or None for anonymous connections
    """
    # Extract token from query parameters or headers
    token = websocket.query_params.get("token") or websocket.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        # Allow anonymous connections for public endpoints
        logger.debug("Anonymous WebSocket connection")
        return User(
            user_id="anonymous",
            username="anonymous",
            email="anonymous@example.com",
            permissions=["read"],
        )
    
    try:
        # Validate token
        payload = auth_service.decode_token(token)
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if user_id and username:
            # Return authenticated user
            return User(
                user_id=user_id,
                username=username,
                email=f"{username}@example.com",
                permissions=["read", "write", "execute"],
            )
    except AuthenticationError:
        logger.warning("Invalid WebSocket token")
        # Fall through to anonymous user
    
    # Return anonymous user for invalid tokens
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
