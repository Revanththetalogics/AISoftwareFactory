"""
Comprehensive tests for API dependencies module.

Tests for authentication, authorization, and service dependency injection.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from backend.api.dependencies import (
    User,
    get_agent_service,
    get_current_user,
    get_project_service,
    get_websocket_user,
    get_workflow_service,
    require_permissions,
)
from backend.core.exceptions import AuthenticationError
from backend.services.database_services import (
    DatabaseAgentService,
    DatabaseProjectService,
    DatabaseWorkflowService,
)


class TestUser:
    """Tests for User class."""

    def test_user_initialization(self):
        """Test User initialization with all fields."""
        user = User(
            user_id="user-123",
            username="testuser",
            email="test@example.com",
            permissions=["read", "write"],
            is_active=True,
            is_superuser=False,
        )

        assert user.user_id == "user-123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.permissions == ["read", "write"]
        assert user.is_active is True
        assert user.is_superuser is False

    def test_user_default_values(self):
        """Test User initialization with default values."""
        user = User(user_id="user-123", username="testuser", email="test@example.com", permissions=[])

        assert user.is_active is True
        assert user.is_superuser is False


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock()
        request.cookies = {}
        return request

    @pytest.fixture
    def mock_credentials(self):
        """Create mock credentials."""
        credentials = Mock()
        credentials.credentials = "valid-token"
        return credentials

    @pytest.fixture
    def mock_db_user(self):
        """Create mock database user."""
        user = Mock()
        user.id = "user-123"
        user.username = "testuser"
        user.email = "test@example.com"
        user.permissions = ["read", "write"]
        user.is_active = True
        user.is_superuser = False
        return user

    @pytest.fixture
    def mock_auth_service(self):
        """Create mock auth service."""
        return Mock()

    @pytest.mark.asyncio
    async def test_get_current_user_with_bearer_token(
        self, mock_request, mock_credentials, mock_db_user, mock_auth_service
    ):
        """Test authentication with bearer token."""
        mock_auth_service.decode_token = Mock(return_value={"sub": "user-123", "username": "testuser"})
        mock_auth_service.get_user_by_id = AsyncMock(return_value=mock_db_user)

        user = await get_current_user(
            request=mock_request, credentials=mock_credentials, auth_service=mock_auth_service
        )

        assert user.user_id == "user-123"
        assert user.username == "testuser"
        mock_auth_service.decode_token.assert_called_once_with("valid-token")

    @pytest.mark.asyncio
    async def test_get_current_user_with_cookie_token(self, mock_request, mock_db_user, mock_auth_service):
        """Test authentication with cookie token fallback."""
        mock_request.cookies = {"auth_token": "cookie-token"}
        mock_auth_service.decode_token = Mock(return_value={"sub": "user-123", "username": "testuser"})
        mock_auth_service.get_user_by_id = AsyncMock(return_value=mock_db_user)

        user = await get_current_user(request=mock_request, credentials=None, auth_service=mock_auth_service)

        assert user.user_id == "user-123"
        mock_auth_service.decode_token.assert_called_once_with("cookie-token")

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, mock_request, mock_auth_service):
        """Test authentication failure when no token provided."""
        mock_request.cookies = {}

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=None, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401
        assert "Authentication required" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_empty_credentials(self, mock_request, mock_auth_service):
        """Test authentication failure with empty credentials."""
        mock_request.cookies = {}
        credentials = Mock()
        credentials.credentials = None

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=credentials, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token_format(self, mock_request, mock_credentials, mock_auth_service):
        """Test authentication failure with invalid token format (missing fields)."""
        mock_auth_service.decode_token = Mock(
            return_value={
                "sub": "user-123"
                # Missing username
            }
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=mock_credentials, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self, mock_request, mock_credentials, mock_auth_service):
        """Test authentication failure when token missing sub claim."""
        mock_auth_service.decode_token = Mock(
            return_value={
                "username": "testuser"
                # Missing sub
            }
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=mock_credentials, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, mock_request, mock_credentials, mock_auth_service):
        """Test authentication failure when user not found in database."""
        mock_auth_service.decode_token = Mock(return_value={"sub": "user-123", "username": "testuser"})
        mock_auth_service.get_user_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=mock_credentials, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(
        self, mock_request, mock_credentials, mock_db_user, mock_auth_service
    ):
        """Test authentication failure when user is inactive."""
        mock_db_user.is_active = False
        mock_auth_service.decode_token = Mock(return_value={"sub": "user-123", "username": "testuser"})
        mock_auth_service.get_user_by_id = AsyncMock(return_value=mock_db_user)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=mock_credentials, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401
        assert "Account is inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_token_decode_error(self, mock_request, mock_credentials, mock_auth_service):
        """Test authentication failure when token decoding fails."""
        mock_auth_service.decode_token = Mock(side_effect=AuthenticationError("Invalid token"))

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request=mock_request, credentials=mock_credentials, auth_service=mock_auth_service)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail


class TestRequirePermissions:
    """Tests for require_permissions dependency."""

    @pytest.mark.asyncio
    async def test_require_permissions_admin_bypass(self):
        """Test admin users bypass permission checks."""
        user = User(user_id="admin-123", username="admin", email="admin@example.com", permissions=["admin"])

        result = await require_permissions(required_permissions=["delete", "execute"], user=user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_permissions_user_has_permissions(self):
        """Test user with required permissions passes."""
        user = User(
            user_id="user-123", username="testuser", email="test@example.com", permissions=["read", "write", "execute"]
        )

        result = await require_permissions(required_permissions=["read", "write"], user=user)

        assert result == user

    @pytest.mark.asyncio
    async def test_require_permissions_missing_permissions(self):
        """Test user without required permissions fails."""
        user = User(user_id="user-123", username="testuser", email="test@example.com", permissions=["read"])

        with pytest.raises(HTTPException) as exc_info:
            await require_permissions(required_permissions=["write", "execute"], user=user)

        assert exc_info.value.status_code == 403
        assert "Missing permissions" in exc_info.value.detail
        assert "write" in exc_info.value.detail
        assert "execute" in exc_info.value.detail


class TestGetWebsocketUser:
    """Tests for get_websocket_user dependency."""

    @pytest.fixture
    def mock_websocket(self):
        """Create mock websocket."""
        websocket = Mock()
        websocket.query_params = {}
        websocket.headers = {}
        websocket.client = Mock()
        websocket.client.host = "127.0.0.1"
        return websocket

    @pytest.fixture
    def mock_auth_service(self):
        """Create mock auth service."""
        return Mock()

    @pytest.fixture
    def mock_db_user(self):
        """Create mock database user for websocket auth."""
        user = Mock()
        user.id = "user-123"
        user.username = "testuser"
        user.email = "testuser@example.com"
        user.permissions = ["read", "write", "execute"]
        user.is_active = True
        user.is_superuser = False
        return user

    @pytest.mark.asyncio
    async def test_websocket_user_with_query_token(self, mock_websocket, mock_auth_service, mock_db_user):
        """Test WebSocket authentication with query parameter token."""
        mock_websocket.query_params = {"token": "valid-token"}
        mock_auth_service.decode_token = Mock(return_value={"sub": "user-123", "username": "testuser"})
        mock_auth_service.get_user_by_id = AsyncMock(return_value=mock_db_user)

        user = await get_websocket_user(websocket=mock_websocket, auth_service=mock_auth_service)

        assert user is not None
        assert user.user_id == "user-123"
        assert user.username == "testuser"
        assert user.email == "testuser@example.com"
        assert user.permissions == ["read", "write", "execute"]

    @pytest.mark.asyncio
    async def test_websocket_user_with_header_token(self, mock_websocket, mock_auth_service, mock_db_user):
        """Test WebSocket authentication with Authorization header."""
        mock_websocket.headers = {"Authorization": "Bearer valid-token"}
        mock_auth_service.decode_token = Mock(return_value={"sub": "user-123", "username": "testuser"})
        mock_auth_service.get_user_by_id = AsyncMock(return_value=mock_db_user)

        user = await get_websocket_user(websocket=mock_websocket, auth_service=mock_auth_service)

        assert user is not None
        assert user.user_id == "user-123"

    @pytest.mark.asyncio
    async def test_websocket_user_no_token(self, mock_websocket, mock_auth_service):
        """Test WebSocket authentication failure with no token."""
        user = await get_websocket_user(websocket=mock_websocket, auth_service=mock_auth_service)

        assert user is None

    @pytest.mark.asyncio
    async def test_websocket_user_invalid_token_payload(self, mock_websocket, mock_auth_service):
        """Test WebSocket authentication failure with invalid token payload."""
        mock_websocket.query_params = {"token": "valid-token"}
        mock_auth_service.decode_token = Mock(
            return_value={
                "sub": "user-123"
                # Missing username
            }
        )

        user = await get_websocket_user(websocket=mock_websocket, auth_service=mock_auth_service)

        assert user is None

    @pytest.mark.asyncio
    async def test_websocket_user_missing_sub(self, mock_websocket, mock_auth_service):
        """Test WebSocket authentication failure when missing sub."""
        mock_websocket.query_params = {"token": "valid-token"}
        mock_auth_service.decode_token = Mock(
            return_value={
                "username": "testuser"
                # Missing sub
            }
        )

        user = await get_websocket_user(websocket=mock_websocket, auth_service=mock_auth_service)

        assert user is None

    @pytest.mark.asyncio
    async def test_websocket_user_token_decode_error(self, mock_websocket, mock_auth_service):
        """Test WebSocket authentication failure on decode error."""
        mock_websocket.query_params = {"token": "invalid-token"}
        mock_auth_service.decode_token = Mock(side_effect=AuthenticationError("Invalid token"))

        user = await get_websocket_user(websocket=mock_websocket, auth_service=mock_auth_service)

        assert user is None

    @pytest.mark.asyncio
    async def test_websocket_user_no_client(self, mock_auth_service):
        """Test WebSocket authentication with no client info."""
        websocket = Mock()
        websocket.query_params = {}
        websocket.headers = {}
        websocket.client = None

        user = await get_websocket_user(websocket=websocket, auth_service=mock_auth_service)

        assert user is None


class TestServiceDependencies:
    """Tests for service dependency functions."""

    def test_get_project_service(self):
        """Test get_project_service returns correct type."""
        service = get_project_service()
        assert isinstance(service, DatabaseProjectService)

    def test_get_workflow_service(self):
        """Test get_workflow_service returns correct type."""
        service = get_workflow_service()
        assert isinstance(service, DatabaseWorkflowService)

    def test_get_agent_service(self):
        """Test get_agent_service returns correct type."""
        service = get_agent_service()
        assert isinstance(service, DatabaseAgentService)

    def test_services_are_new_instances(self):
        """Test that factory functions create new instances."""
        service1 = get_project_service()
        service2 = get_project_service()
        # They should be separate instances
        assert service1 is not service2
