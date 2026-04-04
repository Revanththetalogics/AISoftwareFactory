"""
Comprehensive tests for AuthService to increase coverage.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from backend.models.database import DBUser
from backend.services.auth_service import AuthService


class TestAuthService:
    """Comprehensive tests for AuthService."""

    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance."""
        return AuthService()

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = MagicMock()
        settings.SECRET_KEY = "test-secret-key"
        settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        return settings

    def test_init(self, auth_service):
        """Test AuthService initialization."""
        assert auth_service is not None
        assert hasattr(auth_service, "settings")
        assert hasattr(auth_service, "algorithm")
        assert auth_service.algorithm == "HS256"

    def test_verify_password_success(self, auth_service):
        """Test successful password verification."""
        # Hash a password first
        password = "test_password_123"
        hashed = auth_service.get_password_hash(password)

        # Verify the password
        result = auth_service.verify_password(password, hashed)
        assert result is True

    def test_verify_password_failure(self, auth_service):
        """Test failed password verification."""
        # Hash a password
        hashed = auth_service.get_password_hash("correct_password")

        # Try to verify with wrong password
        result = auth_service.verify_password("wrong_password", hashed)
        assert result is False

    def test_get_password_hash(self, auth_service):
        """Test password hashing."""
        password = "test_password"
        hashed = auth_service.get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be hashed, not plain text

    def test_create_access_token_default_expiry(self, auth_service, mock_settings):
        """Test creating access token with default expiry."""
        with patch.object(auth_service, "settings", mock_settings):
            data = {"sub": "user123", "username": "testuser"}
            token = auth_service.create_access_token(data)

            assert isinstance(token, str)
            assert len(token) > 0

            # Decode to verify structure
            decoded = auth_service.decode_token(token)
            assert decoded["sub"] == "user123"
            assert decoded["username"] == "testuser"
            assert "exp" in decoded
            assert "iat" in decoded

    def test_create_access_token_custom_expiry(self, auth_service, mock_settings):
        """Test creating access token with custom expiry."""
        with patch.object(auth_service, "settings", mock_settings):
            data = {"sub": "user123"}
            custom_expiry = timedelta(minutes=15)
            token = auth_service.create_access_token(data, custom_expiry)

            decoded = auth_service.decode_token(token)
            assert "exp" in decoded
            # Expiry should be approximately 15 minutes from now
            expected_expiry = datetime.utcnow() + custom_expiry
            actual_expiry = datetime.fromtimestamp(decoded["exp"])
            # Allow some tolerance for processing time
            assert abs((actual_expiry - expected_expiry).total_seconds()) < 5

    def test_decode_token_success(self, auth_service, mock_settings):
        """Test successful token decoding."""
        with patch.object(auth_service, "settings", mock_settings):
            # Create a token first
            data = {"sub": "user123", "test_claim": "test_value"}
            token = auth_service.create_access_token(data)

            # Decode the token
            decoded = auth_service.decode_token(token)

            assert decoded["sub"] == "user123"
            assert decoded["test_claim"] == "test_value"
            assert "exp" in decoded
            assert "iat" in decoded

    def test_decode_token_invalid(self, auth_service, mock_settings):
        """Test decoding invalid token."""
        with patch.object(auth_service, "settings", mock_settings):
            invalid_token = "invalid.token.string"

            with pytest.raises(Exception) as exc_info:  # JWTError or AuthenticationError
                auth_service.decode_token(invalid_token)

            # Should raise some kind of authentication/token error
            assert "Invalid" in str(exc_info.value) or "expired" in str(exc_info.value).lower()

    def test_decode_token_expired(self, auth_service, mock_settings):
        """Test decoding expired token."""
        with patch.object(auth_service, "settings", mock_settings):
            # Create token that expires immediately
            data = {"sub": "user123"}
            expired_token = auth_service.create_access_token(
                data,
                timedelta(seconds=-1),  # Expired 1 second ago
            )

            with pytest.raises(Exception) as exc_info:
                auth_service.decode_token(expired_token)

            assert "Invalid" in str(exc_info.value) or "expired" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, auth_service):
        """Test getting user by username."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result

            result = await auth_service.get_user_by_username("testuser")

            assert result is not None
            assert result.id == "user123"
            assert result.username == "testuser"
            assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, auth_service):
        """Test getting non-existent user by username."""
        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await auth_service.get_user_by_username("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_inactive(self, auth_service):
        """Test getting inactive user by username."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=False,  # Inactive user
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result

            result = await auth_service.get_user_by_username("testuser")

            # Should return None for inactive users
            assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, auth_service):
        """Test getting user by ID."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result

            result = await auth_service.get_user_by_id("user123")

            assert result is not None
            assert result.id == "user123"
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, auth_service):
        """Test getting user by email."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_session.execute.return_value = mock_result

            result = await auth_service.get_user_by_email("test@example.com")

            assert result is not None
            assert result.email == "test@example.com"
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_authenticate_user_success_username(self, auth_service):
        """Test successful user authentication by username."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password=auth_service.get_password_hash("correct_password"),
            is_active=True,
        )

        with patch.object(auth_service, "get_user_by_username", return_value=mock_user):
            with patch.object(auth_service, "get_user_by_email", return_value=None):
                with patch("backend.services.auth_service.AsyncSessionLocal"):
                    result = await auth_service.authenticate_user("testuser", "correct_password")

                    assert result is not None
                    assert result["user_id"] == "user123"
                    assert result["username"] == "testuser"
                    assert result["email"] == "test@example.com"
                    assert "permissions" in result
                    assert "is_superuser" in result

    @pytest.mark.asyncio
    async def test_authenticate_user_success_email(self, auth_service):
        """Test successful user authentication by email."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password=auth_service.get_password_hash("correct_password"),
            is_active=True,
        )

        with patch.object(auth_service, "get_user_by_username", return_value=None):
            with patch.object(auth_service, "get_user_by_email", return_value=mock_user):
                with patch("backend.services.auth_service.AsyncSessionLocal"):
                    result = await auth_service.authenticate_user("test@example.com", "correct_password")

                    assert result is not None
                    assert result["user_id"] == "user123"
                    assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service):
        """Test authentication with wrong password."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password=auth_service.get_password_hash("correct_password"),
            is_active=True,
        )

        with patch.object(auth_service, "get_user_by_username", return_value=mock_user):
            result = await auth_service.authenticate_user("testuser", "wrong_password")

            assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_user_not_found(self, auth_service):
        """Test authentication for non-existent user."""
        with patch.object(auth_service, "get_user_by_username", return_value=None):
            with patch.object(auth_service, "get_user_by_email", return_value=None):
                result = await auth_service.authenticate_user("nonexistent", "password")

                assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_user(self, auth_service):
        """Test authentication for inactive user."""
        mock_user = DBUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            hashed_password=auth_service.get_password_hash("correct_password"),
            is_active=False,  # Inactive user
        )

        with patch.object(auth_service, "get_user_by_username", return_value=mock_user):
            result = await auth_service.authenticate_user("testuser", "correct_password")

            assert result is None

    @pytest.mark.asyncio
    async def test_create_default_admin_success(self, auth_service):
        """Test creating default admin user."""
        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # No existing users
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await auth_service.create_default_admin()

            assert result is not None
            assert isinstance(result, DBUser)
            assert result.username == "admin"
            assert result.email == "admin@example.com"
            assert result.is_superuser is True
            assert result.is_active is True

    @pytest.mark.asyncio
    async def test_create_default_admin_users_exist(self, auth_service):
        """Test creating default admin when users already exist."""
        mock_existing_user = DBUser(
            id="user123",
            username="existinguser",
            email="existing@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # Existing user found
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_existing_user
            mock_session.execute.return_value = mock_result

            result = await auth_service.create_default_admin()

            assert result is None  # Should not create admin if users exist

    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_service):
        """Test creating new user."""
        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # No existing users with same username/email
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result

            result = await auth_service.create_user(
                username="newuser",
                email="newuser@example.com",
                password="secure_password_123",
                first_name="New",
                last_name="User",
                permissions=["read", "write"],
                is_superuser=False,
            )

            assert result is not None
            assert isinstance(result, DBUser)
            assert result.username == "newuser"
            assert result.email == "newuser@example.com"
            assert result.first_name == "New"
            assert result.last_name == "User"
            assert result.permissions == ["read", "write"]
            assert result.is_superuser is False
            assert result.is_active is True
            # Password should be hashed
            assert result.hashed_password != "secure_password_123"
            assert len(result.hashed_password) > 0

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, auth_service):
        """Test creating user with duplicate username."""
        mock_existing_user = DBUser(
            id="existing123",
            username="duplicateuser",
            email="other@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # Existing username found
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_existing_user
            mock_session.execute.return_value = mock_result

            with pytest.raises(ValueError) as exc_info:
                await auth_service.create_user(
                    username="duplicateuser",  # Same username
                    email="new@example.com",
                    password="password123",
                )

            assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, auth_service):
        """Test creating user with duplicate email."""
        mock_existing_user = DBUser(
            id="existing123",
            username="otheruser",
            email="duplicate@example.com",
            hashed_password="hashed_password",
            is_active=True,
        )

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # First check (username) returns None
            # Second check (email) returns existing user
            mock_result1 = MagicMock()
            mock_result1.scalar_one_or_none.return_value = None
            mock_result2 = MagicMock()
            mock_result2.scalar_one_or_none.return_value = mock_existing_user

            # Configure execute to return different results for different calls
            mock_session.execute.side_effect = [mock_result1, mock_result2]

            with pytest.raises(ValueError) as exc_info:
                await auth_service.create_user(
                    username="newuser",
                    email="duplicate@example.com",  # Same email
                    password="password123",
                )

            assert "already exists" in str(exc_info.value)

    def test_create_user_session(self, auth_service, mock_settings):
        """Test creating user session with tokens."""
        with patch.object(auth_service, "settings", mock_settings):
            user_data = {"user_id": "user123", "username": "testuser", "email": "test@example.com"}

            session_data = auth_service.create_user_session(user_data)

            assert "access_token" in session_data
            assert "refresh_token" in session_data
            assert "token_type" in session_data

            assert session_data["token_type"] == "bearer"
            assert isinstance(session_data["access_token"], str)
            assert isinstance(session_data["refresh_token"], str)
            assert len(session_data["access_token"]) > 0
            assert len(session_data["refresh_token"]) > 0

            # Verify tokens are different
            assert session_data["access_token"] != session_data["refresh_token"]

            # Verify access token structure
            access_payload = auth_service.decode_token(session_data["access_token"])
            assert access_payload["sub"] == "user123"
            assert access_payload["username"] == "testuser"
            assert "type" not in access_payload or access_payload.get("type") != "refresh"

            # Verify refresh token structure
            refresh_payload = auth_service.decode_token(session_data["refresh_token"])
            assert refresh_payload["sub"] == "user123"
            assert refresh_payload["username"] == "testuser"
            assert refresh_payload.get("type") == "refresh"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
