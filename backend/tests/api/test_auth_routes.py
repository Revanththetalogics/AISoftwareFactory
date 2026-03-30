"""
Comprehensive tests for authentication API routes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_auth_service():
    """Mock AuthService."""
    with patch("backend.api.routes.auth.AuthService") as mock:
        service_instance = AsyncMock()
        mock.return_value = service_instance
        yield service_instance


class TestAuthRoutes:
    """Tests for authentication API routes."""

    def test_login_success(self, client, mock_auth_service):
        """Test successful user login."""
        # Mock successful authentication
        mock_auth_service.authenticate_user.return_value = {
            "user": {
                "id": "user123",
                "email": "test@example.com",
                "username": "testuser",
                "role": "user"
            },
            "token": "fake-jwt-token",
            "expires_in": 3600
        }

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["token"] == "fake-jwt-token"
        assert data["data"]["user"]["email"] == "test@example.com"

    def test_login_invalid_credentials(self, client, mock_auth_service):
        """Test login with invalid credentials."""
        # Mock authentication failure
        mock_auth_service.authenticate_user.return_value = None

        response = client.post(
            "/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Invalid credentials" in data["message"]

    def test_register_success(self, client, mock_auth_service):
        """Test successful user registration."""
        mock_auth_service.register_user.return_value = {
            "id": "newuser123",
            "email": "newuser@example.com",
            "username": "newuser",
            "role": "user",
            "created_at": "2024-01-01T00:00:00Z"
        }

        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepassword123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["username"] == "newuser"

    def test_register_duplicate_email(self, client, mock_auth_service):
        """Test registration with duplicate email."""
        from backend.core.exceptions import ConflictError
        mock_auth_service.register_user.side_effect = ConflictError("Email already exists")

        response = client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User"
            }
        )

        assert response.status_code == 409
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["message"]

    def test_refresh_token_success(self, client, mock_auth_service):
        """Test successful token refresh."""
        mock_auth_service.refresh_token.return_value = {
            "token": "new-fake-jwt-token",
            "expires_in": 3600
        }

        response = client.post(
            "/auth/refresh",
            headers={"Authorization": "Bearer old-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["token"] == "new-fake-jwt-token"

    def test_refresh_token_invalid(self, client, mock_auth_service):
        """Test refresh with invalid token."""
        from backend.core.exceptions import AuthenticationError
        mock_auth_service.refresh_token.side_effect = AuthenticationError("Invalid token")

        response = client.post(
            "/auth/refresh",
            headers={"Authorization": "Bearer invalid-token"}
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    def test_logout_success(self, client, mock_auth_service):
        """Test successful logout."""
        mock_auth_service.logout_user.return_value = True

        response = client.post(
            "/auth/logout",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "logged out" in data["message"].lower()

    def test_forgot_password_success(self, client, mock_auth_service):
        """Test forgot password request."""
        mock_auth_service.initiate_password_reset.return_value = True

        response = client.post(
            "/auth/forgot-password",
            json={"email": "user@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reset instructions" in data["message"].lower()

    def test_reset_password_success(self, client, mock_auth_service):
        """Test password reset with valid token."""
        mock_auth_service.reset_password.return_value = True

        response = client.post(
            "/auth/reset-password",
            json={
                "token": "valid-reset-token",
                "new_password": "newsecurepassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "password reset" in data["message"].lower()

    def test_reset_password_invalid_token(self, client, mock_auth_service):
        """Test password reset with invalid token."""
        from backend.core.exceptions import ValidationError
        mock_auth_service.reset_password.side_effect = ValidationError("Invalid reset token")

        response = client.post(
            "/auth/reset-password",
            json={
                "token": "invalid-token",
                "new_password": "newpassword123"
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_get_current_user_success(self, client, mock_auth_service):
        """Test getting current user info."""
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.role = "user"
        mock_user.full_name = "Test User"
        mock_user.created_at = "2024-01-01T00:00:00Z"

        mock_auth_service.get_current_user.return_value = mock_user

        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "test@example.com"
        assert data["data"]["username"] == "testuser"

    def test_update_profile_success(self, client, mock_auth_service):
        """Test updating user profile."""
        mock_updated_user = MagicMock()
        mock_updated_user.id = "user123"
        mock_updated_user.email = "updated@example.com"
        mock_updated_user.username = "updateduser"
        mock_updated_user.full_name = "Updated User"

        mock_auth_service.update_user_profile.return_value = mock_updated_user

        response = client.put(
            "/auth/me",
            headers={"Authorization": "Bearer valid-token"},
            json={
                "full_name": "Updated User",
                "username": "updateduser"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["full_name"] == "Updated User"

    def test_change_password_success(self, client, mock_auth_service):
        """Test changing user password."""
        mock_auth_service.change_password.return_value = True

        response = client.put(
            "/auth/change-password",
            headers={"Authorization": "Bearer valid-token"},
            json={
                "current_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "password changed" in data["message"].lower()

    def test_change_password_wrong_current(self, client, mock_auth_service):
        """Test changing password with wrong current password."""
        from backend.core.exceptions import AuthenticationError
        mock_auth_service.change_password.side_effect = AuthenticationError("Current password is incorrect")

        response = client.put(
            "/auth/change-password",
            headers={"Authorization": "Bearer valid-token"},
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False

    def test_list_users_admin_only(self, client, mock_auth_service):
        """Test listing users (admin only)."""
        mock_users = [
            {"id": "user1", "email": "user1@example.com", "username": "user1"},
            {"id": "user2", "email": "user2@example.com", "username": "user2"}
        ]
        mock_auth_service.list_users.return_value = mock_users

        response = client.get(
            "/auth/users",
            headers={"Authorization": "Bearer admin-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2

    def test_get_user_by_id_success(self, client, mock_auth_service):
        """Test getting specific user by ID."""
        mock_user = {
            "id": "user123",
            "email": "user@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "role": "user",
            "created_at": "2024-01-01T00:00:00Z"
        }
        mock_auth_service.get_user_by_id.return_value = mock_user

        response = client.get(
            "/auth/users/user123",
            headers={"Authorization": "Bearer admin-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "user123"

    def test_update_user_admin_success(self, client, mock_auth_service):
        """Test admin updating user."""
        mock_updated_user = {
            "id": "user123",
            "email": "updated@example.com",
            "username": "updateduser",
            "role": "admin"
        }
        mock_auth_service.update_user.return_value = mock_updated_user

        response = client.put(
            "/auth/users/user123",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "role": "admin",
                "is_active": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["role"] == "admin"

    def test_delete_user_admin_success(self, client, mock_auth_service):
        """Test admin deleting user."""
        mock_auth_service.delete_user.return_value = True

        response = client.delete(
            "/auth/users/user123",
            headers={"Authorization": "Bearer admin-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
