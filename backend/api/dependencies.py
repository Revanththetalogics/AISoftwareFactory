"""
API Dependencies for AI Software Factory.

This module provides dependency injection for authentication, authorization,
and common services with database-backed user management.
"""


from fastapi import Depends, HTTPException, Request, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.exceptions import AuthenticationError
from backend.core.logging import get_logger
from backend.services.auth_service import AuthService, get_auth_service
from backend.services.database_services import (
    DatabaseAgentService,
    DatabaseProjectService,
    DatabaseWorkflowService,
)

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)  # Don't auto error - we'll handle cookie auth too


class User:
    """User model for authentication."""
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        permissions: list[str],
        is_active: bool = True,
        is_superuser: bool = False,
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.permissions = permissions
        self.is_active = is_active
        self.is_superuser = is_superuser


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """
    Get current authenticated user by validating JWT token.

    Supports both Bearer token in Authorization header and
    httpOnly cookie-based authentication.

    Args:
        request: FastAPI Request object for cookie access
        credentials: Optional HTTP authorization credentials
        auth_service: Authentication service instance

    Returns:
        User object for authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    token = None

    # Try to get token from Authorization header first
    if credentials and credentials.credentials:
        token = credentials.credentials

    # Fall back to httpOnly cookie
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        logger.warning("No authentication token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and validate the JWT token
        payload = auth_service.decode_token(token)

        # Extract user information from token
        user_id: str = payload.get("sub")
        username: str = payload.get("username")

        if user_id is None or username is None:
            logger.warning("Token missing required fields")
            raise AuthenticationError("Invalid token format")

        # Fetch user from database
        user_record = await auth_service.get_user_by_id(user_id)

        if not user_record:
            logger.warning("User not found in database", user_id=user_id)
            raise AuthenticationError("User not found")

        if not user_record.is_active:
            logger.warning("Inactive user", user_id=user_id)
            raise AuthenticationError("Account is inactive")

        logger.debug("User authenticated", user_id=user_id, username=username)

        return User(
            user_id=user_record.id,
            username=user_record.username,
            email=user_record.email,
            permissions=user_record.permissions or [],
            is_active=user_record.is_active,
            is_superuser=user_record.is_superuser,
        )

    except AuthenticationError as exc:
        logger.warning("Authentication failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


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
) -> User | None:
    """
    Get user from WebSocket connection.

    SECURITY: This function now requires authentication for WebSocket connections.
    Anonymous connections are no longer allowed.

    Args:
        websocket: WebSocket connection
        auth_service: Authentication service instance

    Returns:
        User object if authenticated, None if authentication fails.
        Caller MUST check for None and close connection with code 4001.
    """
    # Extract token from query parameters or headers
    token = websocket.query_params.get("token") or websocket.headers.get("Authorization", "").replace("Bearer ", "")

    if not token:
        # No token provided - authentication required
        logger.warning(
            "WebSocket connection rejected: no token provided",
            client=websocket.client.host if websocket.client else "unknown",
        )
        return None

    try:
        # Validate token
        payload = auth_service.decode_token(token)
        user_id = payload.get("sub")
        username = payload.get("username")

        if not user_id or not username:
            logger.warning(
                "WebSocket connection rejected: invalid token payload",
                client=websocket.client.host if websocket.client else "unknown",
            )
            return None

        logger.debug(
            "WebSocket user authenticated",
            user_id=user_id,
            username=username,
        )

        # Return authenticated user
        return User(
            user_id=user_id,
            username=username,
            email=f"{username}@example.com",
            permissions=["read", "write", "execute"],
        )

    except AuthenticationError as exc:
        logger.warning(
            "WebSocket connection rejected: invalid token",
            error=str(exc),
            client=websocket.client.host if websocket.client else "unknown",
        )
        return None


# Common dependency aliases
require_auth = Depends(get_current_user)
require_write = Depends(lambda: require_permissions(["write"]))
require_execute = Depends(lambda: require_permissions(["execute"]))
require_admin = Depends(lambda: require_permissions(["admin"]))


# ============================================================================
# Database Service Dependencies
# ============================================================================
# These provide database-backed service instances with proper session scoping.
# Routes inject these to get services wired to the request's database session.

def get_project_service() -> DatabaseProjectService:
    """Get project service instance for database operations."""
    return DatabaseProjectService()


def get_workflow_service() -> DatabaseWorkflowService:
    """Get workflow service instance for database operations."""
    return DatabaseWorkflowService()


def get_agent_service() -> DatabaseAgentService:
    """Get agent service instance for database operations."""
    return DatabaseAgentService()

