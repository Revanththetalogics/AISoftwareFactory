"""
Authentication API Routes.

This module provides REST endpoints for user authentication including
login, logout, token refresh, and user management.

Features:
- httpOnly cookie-based authentication for enhanced security
- JWT tokens with configurable expiration
- CSRF protection via SameSite cookie attribute
"""

from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.api.dependencies import get_auth_service
from backend.services.auth_service import AuthService
from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

settings = get_settings()


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    request: Request
) -> None:
    """
    Set httpOnly authentication cookies on response.
    
    Args:
        response: FastAPI Response object
        access_token: JWT access token
        refresh_token: JWT refresh token
        request: FastAPI Request object for scheme detection
    """
    # Determine if we should set Secure flag (HTTPS only)
    is_secure = request.url.scheme == "https"
    
    # Set access token cookie
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/"
    )
    
    # Set refresh token cookie (longer lived)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/api/v1/auth"  # Only sent to auth endpoints
    )


def clear_auth_cookies(response: Response) -> None:
    """
    Clear authentication cookies from response.
    
    Args:
        response: FastAPI Response object
    """
    response.delete_cookie(key="auth_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")


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
    """Refresh token request model (optional - can use cookie instead)."""
    refresh_token: str | None = None


class TokenValidationResponse(BaseModel):
    """Token validation response model."""
    valid: bool
    user_id: str | None = None
    username: str | None = None
    expires_in: int | None = None


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return access tokens with httpOnly cookies"
)
async def login(
    request_data: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    """
    Authenticate user and generate JWT tokens.
    
    Sets httpOnly cookies for secure token storage and returns
    user data in JSON response body.
    
    Args:
        request_data: Login credentials
        request: FastAPI Request object
        auth_service: Authentication service instance
        
    Returns:
        JSONResponse: User info with httpOnly auth cookies set
        
    Raises:
        HTTPException: If authentication fails
    """
    logger.info("Login attempt", username=request_data.username)
    
    # Authenticate user
    user_data = await auth_service.authenticate_user(request_data.username, request_data.password)
    if not user_data:
        logger.warning("Login failed", username=request_data.username)
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
    
    # Create JSON response with user data
    response_data = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "email": user_data["email"],
        "permissions": user_data["permissions"],
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    
    response = JSONResponse(content=response_data)
    
    # Set httpOnly cookies
    set_auth_cookies(
        response=response,
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        request=request
    )
    
    return response


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token from cookie or request body"
)
async def refresh_token(
    request: Request,
    request_data: RefreshTokenRequest | None = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> JSONResponse:
    """
    Refresh access token using refresh token.
    
    Accepts refresh token from httpOnly cookie (preferred) or request body.
    Sets new httpOnly cookies on successful refresh.
    
    Args:
        request: FastAPI Request object
        request_data: Optional refresh token in body
        auth_service: Authentication service instance
        
    Returns:
        JSONResponse: New access token with updated cookies
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    # Get refresh token from cookie first, then from body
    token = request.cookies.get("refresh_token")
    if not token and request_data:
        token = request_data.refresh_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token not provided"
        )
    
    try:
        # Decode refresh token
        payload = auth_service.decode_token(token)
        
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
        
        # Get user from database to verify they still exist and are active
        user = await auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "permissions": user.permissions or []
        }
        tokens = auth_service.create_user_session(user_data)
        
        logger.info("Token refreshed", user_id=user_id)
        
        response_data = {
            "access_token": tokens["access_token"],
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
        response = JSONResponse(content=response_data)
        
        # Set new httpOnly cookies
        set_auth_cookies(
            response=response,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            request=request
        )
        
        return response
        
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
    description="Invalidate user session and clear httpOnly cookies"
)
async def logout(
    current_user = Depends(lambda: None),  # Will be set by auth middleware
) -> JSONResponse:
    """
    Logout user and clear authentication cookies.
    
    Clears httpOnly authentication cookies to invalidate the session.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        JSONResponse: Logout confirmation with cookies cleared
    """
    if current_user and current_user.user_id != "anonymous":
        logger.info("User logged out", user_id=current_user.user_id)
    
    response = JSONResponse(content={"message": "Logged out successfully"})
    
    # Clear httpOnly cookies
    clear_auth_cookies(response)
    
    return response


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
    
    SECURITY: This endpoint is only available when:
    - ENVIRONMENT == "development" AND
    - DEBUG == True
    
    In any other configuration, returns 404 Not Found.
    
    Returns:
        Dict: Test user credentials
    """
    # SECURITY: Only available in development mode with DEBUG enabled
    if not (settings.is_development and settings.DEBUG):
        # Return 404 to avoid revealing endpoint exists in production
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )
    
    logger.info("Test credentials requested (development mode)")
    
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