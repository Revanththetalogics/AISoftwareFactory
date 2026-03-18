"""
Authentication Service for AI Software Factory.

This module provides JWT-based authentication with secure token generation,
validation, and user management.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.core.exceptions import AuthenticationError, AuthorizationError

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Authentication service handling JWT tokens and user authentication.
    
    Features:
    - Secure JWT token generation and validation
    - Password hashing and verification
    - Token refresh capabilities
    - User session management
    """
    
    def __init__(self):
        """Initialize authentication service."""
        self.settings = get_settings()
        self.algorithm = "HS256"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            bool: True if password matches
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password for storage.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            expires_delta: Token expiration time
            
        Returns:
            str: Encoded JWT token
            
        Example:
            >>> auth_service = AuthService()
            >>> token = auth_service.create_access_token({"sub": "user123"})
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.settings.SECRET_KEY, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Dict: Decoded token payload
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token, 
                self.settings.SECRET_KEY, 
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError as exc:
            logger.warning("Invalid token", error=str(exc))
            raise AuthenticationError("Invalid or expired token")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials.
        
        This is a simplified version. In production, this would:
        - Query database for user
        - Verify password hash
        - Check user status (active/banned)
        - Return user data if valid
        
        Args:
            username: Username/email
            password: Plain text password
            
        Returns:
            Dict: User data if authenticated, None otherwise
        """
        # Mock user data - replace with database query in production
        mock_users = {
            "admin": {
                "user_id": "user-admin-001",
                "username": "admin",
                "email": "admin@example.com",
                "hashed_password": self.get_password_hash("admin123"),
                "permissions": ["read", "write", "execute", "admin"],
                "is_active": True
            },
            "developer": {
                "user_id": "user-dev-001", 
                "username": "developer",
                "email": "dev@example.com",
                "hashed_password": self.get_password_hash("dev123"),
                "permissions": ["read", "write", "execute"],
                "is_active": True
            }
        }
        
        user = mock_users.get(username)
        if not user:
            logger.warning("User not found", username=username)
            return None
            
        if not user["is_active"]:
            logger.warning("Inactive user attempted login", username=username)
            return None
            
        if not self.verify_password(password, user["hashed_password"]):
            logger.warning("Invalid password", username=username)
            return None
            
        # Return user data without sensitive information
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "permissions": user["permissions"]
        }
    
    def create_user_session(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create user session with access and refresh tokens.
        
        Args:
            user_data: Authenticated user data
            
        Returns:
            Dict: Session tokens (access_token, refresh_token)
        """
        # Create access token
        access_token_expires = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user_data["user_id"], "username": user_data["username"]},
            expires_delta=access_token_expires
        )
        
        # Create refresh token (longer lived)
        refresh_token_expires = timedelta(days=7)
        refresh_token = self.create_access_token(
            data={
                "sub": user_data["user_id"], 
                "username": user_data["username"],
                "type": "refresh"
            },
            expires_delta=refresh_token_expires
        )
        
        logger.info("User session created", user_id=user_data["user_id"])
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


# Global auth service instance
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """
    Get authentication service instance.
    
    Returns:
        AuthService: Singleton auth service instance
    """
    return auth_service