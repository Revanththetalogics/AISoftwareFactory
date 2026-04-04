"""
Extended tests for authentication service (backend/services/auth_service.py).

Tests cover:
- authenticate_user() with various credential scenarios
- get_user_by_username() / get_user_by_id() / get_user_by_email()
- create_default_admin() behavior
- Token generation and validation
- Password hashing and verification
- User session creation
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.core.exceptions import AuthenticationError
from backend.services.auth_service import AuthService, auth_service, get_auth_service


# Fixture to mock passlib's pwd_context to avoid bcrypt backend issues
@pytest.fixture(autouse=True)
def mock_pwd_context():
    """Mock the password context to avoid bcrypt backend issues."""
    with patch("backend.services.auth_service.pwd_context") as mock_context:
        # Simple hash function for testing
        mock_context.hash = lambda password: f"$2b$12$hashed_{password}"
        mock_context.verify = lambda plain, hashed: hashed == f"$2b$12$hashed_{plain}"
        yield mock_context


class TestAuthServicePasswordMethods:
    """Tests for password hashing and verification methods."""

    def test_get_password_hash_returns_string(self):
        """Test get_password_hash returns a string."""
        service = AuthService()
        password = "test_password"

        hashed = service.get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 10

    def test_get_password_hash_produces_hash_format(self):
        """Test hash is produced (mocked bcrypt format)."""
        service = AuthService()
        password = "test_password"

        hashed = service.get_password_hash(password)

        # With our mock, hashes start with $2b$12$
        assert hashed.startswith("$2b$12$")

    def test_different_passwords_different_hashes(self):
        """Test different passwords produce different hashes."""
        service = AuthService()

        hash1 = service.get_password_hash("password1")
        hash2 = service.get_password_hash("password2")

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verify_password returns True for correct password."""
        service = AuthService()
        password = "my_secret_password"
        hashed = service.get_password_hash(password)

        result = service.verify_password(password, hashed)

        assert result is True

    def test_verify_password_incorrect(self):
        """Test verify_password returns False for incorrect password."""
        service = AuthService()
        password = "my_secret_password"
        hashed = service.get_password_hash(password)

        result = service.verify_password("wrong_password", hashed)

        assert result is False

    def test_verify_password_empty(self):
        """Test verify_password handles empty password."""
        service = AuthService()
        hashed = service.get_password_hash("")

        assert service.verify_password("", hashed) is True
        assert service.verify_password("notempty", hashed) is False


class TestTokenGeneration:
    """Tests for JWT token generation and validation."""

    def test_create_access_token_returns_string(self):
        """Test create_access_token returns a JWT string."""
        service = AuthService()
        data = {"sub": "user123", "username": "testuser"}

        token = service.create_access_token(data)

        assert isinstance(token, str)
        # JWT tokens have three parts separated by dots
        assert len(token.split(".")) == 3

    def test_create_access_token_contains_data(self):
        """Test token contains the provided data."""
        service = AuthService()
        data = {"sub": "user123", "username": "testuser"}

        token = service.create_access_token(data)
        payload = service.decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"

    def test_create_access_token_includes_expiry(self):
        """Test token includes expiry claim."""
        service = AuthService()
        data = {"sub": "user123"}

        token = service.create_access_token(data)
        payload = service.decode_token(token)

        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiry(self):
        """Test token with custom expiry delta."""
        service = AuthService()
        data = {"sub": "user123"}
        expires = timedelta(hours=1)

        token = service.create_access_token(data, expires_delta=expires)
        payload = service.decode_token(token)

        # Verify expiry is approximately 1 hour from now
        exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
        now = datetime.now(UTC)
        delta = exp_time - now

        assert timedelta(minutes=55) < delta < timedelta(minutes=65)

    def test_decode_token_valid(self):
        """Test decode_token with valid token."""
        service = AuthService()
        data = {"sub": "user123", "role": "admin"}
        token = service.create_access_token(data)

        payload = service.decode_token(token)

        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"

    def test_decode_token_invalid_raises_error(self):
        """Test decode_token raises error for invalid token."""
        service = AuthService()

        with pytest.raises(AuthenticationError) as exc_info:
            service.decode_token("invalid.token.here")

        assert "invalid" in str(exc_info.value).lower() or "expired" in str(exc_info.value).lower()

    def test_decode_token_expired_raises_error(self):
        """Test decode_token raises error for expired token."""
        service = AuthService()
        data = {"sub": "user123"}
        # Create token that expires immediately
        token = service.create_access_token(data, expires_delta=timedelta(seconds=-1))

        with pytest.raises(AuthenticationError):
            service.decode_token(token)

    def test_decode_token_tampered_raises_error(self):
        """Test decode_token raises error for tampered token."""
        service = AuthService()
        data = {"sub": "user123"}
        token = service.create_access_token(data)

        # Tamper with the token
        parts = token.split(".")
        tampered_token = parts[0] + ".tampered." + parts[2]

        with pytest.raises(AuthenticationError):
            service.decode_token(tampered_token)


class TestUserSessionCreation:
    """Tests for create_user_session method."""

    def test_create_user_session_returns_tokens(self):
        """Test create_user_session returns access and refresh tokens."""
        service = AuthService()
        user_data = {
            "user_id": "user-123",
            "username": "testuser",
            "email": "test@example.com",
        }

        session = service.create_user_session(user_data)

        assert "access_token" in session
        assert "refresh_token" in session
        assert "token_type" in session
        assert session["token_type"] == "bearer"

    def test_create_user_session_access_token_valid(self):
        """Test access token from session is valid."""
        service = AuthService()
        user_data = {
            "user_id": "user-123",
            "username": "testuser",
        }

        session = service.create_user_session(user_data)
        payload = service.decode_token(session["access_token"])

        assert payload["sub"] == "user-123"
        assert payload["username"] == "testuser"

    def test_create_user_session_refresh_token_has_type(self):
        """Test refresh token contains type claim."""
        service = AuthService()
        user_data = {
            "user_id": "user-123",
            "username": "testuser",
        }

        session = service.create_user_session(user_data)
        payload = service.decode_token(session["refresh_token"])

        assert payload.get("type") == "refresh"

    def test_create_user_session_refresh_token_longer_expiry(self):
        """Test refresh token has longer expiry than access token."""
        service = AuthService()
        user_data = {
            "user_id": "user-123",
            "username": "testuser",
        }

        session = service.create_user_session(user_data)
        access_payload = service.decode_token(session["access_token"])
        refresh_payload = service.decode_token(session["refresh_token"])

        # Refresh token should expire later than access token
        assert refresh_payload["exp"] > access_payload["exp"]


class TestGetUserByUsername:
    """Tests for get_user_by_username method."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user object."""
        user = Mock()
        user.id = "user-test-123"
        user.username = "testuser"
        user.email = "test@example.com"
        user.hashed_password = "$2b$12$somehash"
        user.is_active = True
        user.is_superuser = False
        user.permissions = ["read", "write"]
        return user

    @pytest.mark.asyncio
    async def test_get_user_by_username_found(self, mock_user):
        """Test get_user_by_username returns user when found."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=mock_user)
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await service.get_user_by_username("testuser")

            assert result is not None
            assert result.username == "testuser"

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self):
        """Test get_user_by_username returns None when not found."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await service.get_user_by_username("nonexistent")

            assert result is None


class TestGetUserById:
    """Tests for get_user_by_id method."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user object."""
        user = Mock()
        user.id = "user-test-123"
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self, mock_user):
        """Test get_user_by_id returns user when found."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=mock_user)
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await service.get_user_by_id("user-test-123")

            assert result is not None
            assert result.id == "user-test-123"

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test get_user_by_id returns None when not found."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await service.get_user_by_id("nonexistent-id")

            assert result is None


class TestAuthenticateUser:
    """Tests for authenticate_user method."""

    @pytest.fixture
    def mock_active_user(self):
        """Create a mock active user."""
        user = Mock()
        user.id = "user-test-123"
        user.username = "testuser"
        user.email = "test@example.com"
        user.is_active = True
        user.is_superuser = False
        user.permissions = ["read", "write"]
        user.last_login = None
        return user

    @pytest.mark.asyncio
    async def test_authenticate_user_valid_credentials(self, mock_active_user):
        """Test authenticate_user with valid credentials returns tokens."""
        service = AuthService()
        password = "correct_password"
        mock_active_user.hashed_password = service.get_password_hash(password)

        with patch.object(service, "get_user_by_username", new_callable=AsyncMock) as mock_get_user:
            with patch.object(service, "get_user_by_email", new_callable=AsyncMock) as mock_get_email:
                with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
                    mock_get_user.return_value = mock_active_user
                    mock_get_email.return_value = None

                    mock_session = AsyncMock()
                    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_session.__aexit__ = AsyncMock(return_value=None)
                    mock_session.get = AsyncMock(return_value=mock_active_user)
                    mock_session.commit = AsyncMock()
                    mock_session_local.return_value = mock_session

                    result = await service.authenticate_user("testuser", password)

                    assert result is not None
                    assert result["user_id"] == "user-test-123"
                    assert result["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, mock_active_user):
        """Test authenticate_user with wrong password returns None."""
        service = AuthService()
        mock_active_user.hashed_password = service.get_password_hash("correct_password")

        with patch.object(service, "get_user_by_username", new_callable=AsyncMock) as mock_get_user:
            with patch.object(service, "get_user_by_email", new_callable=AsyncMock) as mock_get_email:
                mock_get_user.return_value = mock_active_user
                mock_get_email.return_value = None

                result = await service.authenticate_user("testuser", "wrong_password")

                assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent_user(self):
        """Test authenticate_user with nonexistent user returns None."""
        service = AuthService()

        with patch.object(service, "get_user_by_username", new_callable=AsyncMock) as mock_get_user:
            with patch.object(service, "get_user_by_email", new_callable=AsyncMock) as mock_get_email:
                mock_get_user.return_value = None
                mock_get_email.return_value = None

                result = await service.authenticate_user("nonexistent", "password")

                assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_user(self):
        """Test authenticate_user with inactive user returns None."""
        service = AuthService()

        inactive_user = Mock()
        inactive_user.id = "user-inactive"
        inactive_user.username = "inactiveuser"
        inactive_user.is_active = False
        inactive_user.hashed_password = service.get_password_hash("password")

        with patch.object(service, "get_user_by_username", new_callable=AsyncMock) as mock_get_user:
            with patch.object(service, "get_user_by_email", new_callable=AsyncMock) as mock_get_email:
                mock_get_user.return_value = inactive_user
                mock_get_email.return_value = None

                result = await service.authenticate_user("inactiveuser", "password")

                assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_by_email(self, mock_active_user):
        """Test authenticate_user can authenticate by email."""
        service = AuthService()
        password = "correct_password"
        mock_active_user.hashed_password = service.get_password_hash(password)

        with patch.object(service, "get_user_by_username", new_callable=AsyncMock) as mock_get_user:
            with patch.object(service, "get_user_by_email", new_callable=AsyncMock) as mock_get_email:
                with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
                    mock_get_user.return_value = None  # Not found by username
                    mock_get_email.return_value = mock_active_user  # Found by email

                    mock_session = AsyncMock()
                    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                    mock_session.__aexit__ = AsyncMock(return_value=None)
                    mock_session.get = AsyncMock(return_value=mock_active_user)
                    mock_session.commit = AsyncMock()
                    mock_session_local.return_value = mock_session

                    result = await service.authenticate_user("test@example.com", password)

                    assert result is not None


class TestCreateDefaultAdmin:
    """Tests for create_default_admin method."""

    @pytest.mark.asyncio
    async def test_create_default_admin_no_users_exist(self):
        """Test create_default_admin creates admin when no users exist."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            # No existing users
            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.add = Mock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            await service.create_default_admin()

            # Should have called add to create user
            mock_session.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_default_admin_users_already_exist(self):
        """Test create_default_admin skips when users already exist."""
        service = AuthService()

        existing_user = Mock()
        existing_user.id = "existing-user"

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            # Existing user found
            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=existing_user)
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.add = Mock()

            result = await service.create_default_admin()

            # Should NOT have called add
            mock_session.add.assert_not_called()
            assert result is None


class TestCreateUser:
    """Tests for create_user method."""

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test create_user creates new user successfully."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            # No existing user with same username/email
            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.add = Mock()
            mock_session.commit = AsyncMock()
            mock_session.refresh = AsyncMock()

            await service.create_user(
                username="newuser",
                email="new@example.com",
                password="password123",
                first_name="New",
                last_name="User",
            )

            mock_session.add.assert_called_once()
            mock_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username_raises_error(self):
        """Test create_user raises error for duplicate username."""
        service = AuthService()

        existing_user = Mock()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            # First execute returns existing user (username exists)
            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=existing_user)
            mock_session.execute = AsyncMock(return_value=mock_result)

            with pytest.raises(ValueError) as exc_info:
                await service.create_user(
                    username="existinguser",
                    email="new@example.com",
                    password="password123",
                )

            assert "already exists" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_error(self):
        """Test create_user raises error for duplicate email."""
        service = AuthService()

        existing_user = Mock()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            # First execute returns None (username doesn't exist)
            # Second execute returns existing user (email exists)
            call_count = [0]

            def execute_side_effect(*args, **kwargs):
                call_count[0] += 1
                mock_result = Mock()
                if call_count[0] == 1:
                    # Username check - not found
                    mock_result.scalar_one_or_none = Mock(return_value=None)
                else:
                    # Email check - found (duplicate)
                    mock_result.scalar_one_or_none = Mock(return_value=existing_user)
                return mock_result

            mock_session.execute = AsyncMock(side_effect=execute_side_effect)

            with pytest.raises(ValueError) as exc_info:
                await service.create_user(
                    username="newuser",
                    email="existing@example.com",
                    password="password123",
                )

            assert "email" in str(exc_info.value).lower()
            assert "already exists" in str(exc_info.value).lower()


class TestGetUserByEmail:
    """Tests for get_user_by_email method."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self):
        """Test get_user_by_email returns user when found."""
        service = AuthService()
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.is_active = True

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=mock_user)
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await service.get_user_by_email("test@example.com")

            assert result == mock_user
            mock_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """Test get_user_by_email returns None when not found."""
        service = AuthService()

        with patch("backend.services.auth_service.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_local.return_value = mock_session

            mock_result = Mock()
            mock_result.scalar_one_or_none = Mock(return_value=None)
            mock_session.execute = AsyncMock(return_value=mock_result)

            result = await service.get_user_by_email("nonexistent@example.com")

            assert result is None


class TestGetAuthService:
    """Tests for get_auth_service function."""

    def test_get_auth_service_returns_singleton(self):
        """Test get_auth_service returns the singleton instance."""
        service1 = get_auth_service()
        service2 = get_auth_service()

        assert service1 is service2
        assert service1 is auth_service

    def test_get_auth_service_returns_auth_service_type(self):
        """Test get_auth_service returns AuthService instance."""
        service = get_auth_service()

        assert isinstance(service, AuthService)
