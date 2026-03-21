"""
Authentication Service for AI Software Factory.

This module provides JWT-based authentication with secure token generation,
validation, and database-backed user management.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select

from backend.core.config import get_settings
from backend.core.exceptions import AuthenticationError
from backend.core.logging import get_logger
from backend.db.session import AsyncSessionLocal
from backend.models.database import DBUser

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

    async def get_user_by_username(self, username: str) -> Optional[DBUser]:
        """
        Get user by username from database.

        Args:
            username: User's username

        Returns:
            DBUser: User record if found and active, None otherwise
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DBUser).where(
                    DBUser.username == username,
                    DBUser.is_active
                )
            )
            return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> Optional[DBUser]:
        """
        Get user by ID from database.

        Args:
            user_id: User's unique ID

        Returns:
            DBUser: User record if found and active, None otherwise
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DBUser).where(
                    DBUser.id == user_id,
                    DBUser.is_active
                )
            )
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[DBUser]:
        """
        Get user by email from database.

        Args:
            email: User's email address

        Returns:
            DBUser: User record if found and active, None otherwise
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DBUser).where(
                    DBUser.email == email,
                    DBUser.is_active
                )
            )
            return result.scalar_one_or_none()

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials against database.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Dict: User data if authenticated, None otherwise
        """
        # Try to find user by username or email
        user = await self.get_user_by_username(username)
        if not user:
            user = await self.get_user_by_email(username)

        if not user:
            logger.warning("User not found", username=username)
            return None

        if not user.is_active:
            logger.warning("Inactive user attempted login", username=username)
            return None

        if not self.verify_password(password, user.hashed_password):
            logger.warning("Invalid password", username=username)
            return None

        # Update last login timestamp
        async with AsyncSessionLocal() as session:
            user_in_session = await session.get(DBUser, user.id)
            if user_in_session:
                user_in_session.last_login = datetime.now(timezone.utc)
                await session.commit()

        # Return user data without sensitive information
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "permissions": user.permissions or [],
            "is_superuser": user.is_superuser
        }

    async def create_default_admin(self) -> Optional[DBUser]:
        """
        Create default admin user if no users exist in database.

        This is called during application startup to ensure at least
        one admin user exists for initial access.

        Returns:
            DBUser: Created admin user, or None if users already exist
        """
        async with AsyncSessionLocal() as session:
            # Check if any users exist
            result = await session.execute(select(DBUser).limit(1))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.debug("Users already exist, skipping default admin creation")
                return None

            # Create default admin user
            admin_user = DBUser(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@example.com",
                hashed_password=self.get_password_hash("admin123"),
                first_name="System",
                last_name="Administrator",
                is_active=True,
                is_superuser=True,
                permissions=["read", "write", "execute", "admin"],
            )

            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)

            logger.info(
                "Default admin user created",
                user_id=admin_user.id,
                username=admin_user.username,
                email=admin_user.email
            )

            return admin_user

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        permissions: list = None,
        is_superuser: bool = False
    ) -> DBUser:
        """
        Create a new user in the database.

        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
            first_name: User's first name
            last_name: User's last name
            permissions: List of permission strings
            is_superuser: Whether user has superuser privileges

        Returns:
            DBUser: Created user record

        Raises:
            ValueError: If username or email already exists
        """
        async with AsyncSessionLocal() as session:
            # Check for existing username
            existing = await session.execute(
                select(DBUser).where(DBUser.username == username)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Username '{username}' already exists")

            # Check for existing email
            existing = await session.execute(
                select(DBUser).where(DBUser.email == email)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Email '{email}' already exists")

            # Create new user
            new_user = DBUser(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                hashed_password=self.get_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_superuser=is_superuser,
                permissions=permissions or ["read"],
            )

            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            logger.info("User created", user_id=new_user.id, username=new_user.username)

            return new_user

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
