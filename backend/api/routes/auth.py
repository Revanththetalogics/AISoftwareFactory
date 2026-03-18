"""
Authentication API Routes.

This module provides REST endpoints for user authentication including
login, logout, token refresh, and user management.
"""

from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from backend.api.dependencies import get_auth_service
from backend.services.auth_service import AuthService
from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

settings = get_settings()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    username: str
    email: str
    permissions: list[str]


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


class TokenValidationResponse(BaseModel):
    """Token validation response model."""
    valid: bool
    user_id: str | None = None
    username: str | None = None
    expires_in: int | None = None


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return access tokens"
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    """
    Authenticate user and generate JWT tokens.
    
    Args:
        request: Login credentials
        auth_service: Authentication service instance
        
    Returns:
        LoginResponse: Authentication tokens and user info
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info("Login attempt", username=request.username)
    
    # Authenticate user
    user_data = auth_service.authenticate_user(request.username, request.password)
    if not user_data:
        logger.warning("Login failed", username=request.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create user session
    tokens = auth_service.create_user_session(user_data)
    
    logger.info(
        "Login successful", 
        user_id=user_data["user_id"], 
        username=user_data["username"]
    )
    
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user_id=user_data["user_id"],
        username=user_data["username"],
        email=user_data["email"],
        permissions=user_data["permissions"]
    )


@router.post(
    "/refresh",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token
        auth_service: Authentication service instance
        
    Returns:
        Dict: New access token
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    try:
        # Decode refresh token
        payload = auth_service.decode_token(request.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token payload"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = auth_service.create_access_token(
            data={"sub": user_id, "username": username},
            expires_delta=access_token_expires
        )
        
        logger.info("Token refreshed", user_id=user_id)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except Exception as exc:
        logger.warning("Token refresh failed", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/validate",
    response_model=TokenValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate token",
    description="Check if JWT token is valid"
)
async def validate_token(
    auth_service: AuthService = Depends(get_auth_service),
    current_user = Depends(lambda: None),  # Will be set by middleware
) -> TokenValidationResponse:
    """
    Validate JWT token and return user information.
    
    This endpoint is protected and will only be reached if token is valid.
    
    Args:
        auth_service: Authentication service instance
        current_user: Current authenticated user
        
    Returns:
        TokenValidationResponse: Token validity and user info
    """
    # If we reach here, token is valid
    return TokenValidationResponse(
        valid=True,
        user_id=current_user.user_id if current_user else None,
        username=current_user.username if current_user else None,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Invalidate user session (client-side token removal)"
)
async def logout(
    current_user = Depends(lambda: None),  # Will be set by auth middleware
) -> Dict[str, str]:
    """
    Logout user (invalidate session).
    
    Note: This is a placeholder. In production, implement:
    - Token blacklisting/revocation
    - Session cleanup
    - Refresh token invalidation
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict: Logout confirmation
    """
    if current_user and current_user.user_id != "anonymous":
        logger.info("User logged out", user_id=current_user.user_id)
    
    return {"message": "Logged out successfully"}


# Test credentials for development
@router.get(
    "/test-credentials",
    status_code=status.HTTP_200_OK,
    summary="Get test credentials",
    description="Get valid test user credentials for development"
)
async def get_test_credentials() -> Dict[str, Any]:
    """
    Get test credentials for development environment.
    
    Returns:
        Dict: Test user credentials
    """
    if not settings.is_development:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test credentials only available in development"
        )
    
    return {
        "message": "Test credentials for development",
        "users": [
            {
                "username": "admin",
                "password": "admin123",
                "permissions": ["read", "write", "execute", "admin"]
            },
            {
                "username": "developer", 
                "password": "dev123",
                "permissions": ["read", "write", "execute"]
            }
        ]
    }