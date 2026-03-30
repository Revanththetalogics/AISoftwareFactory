"""
Comprehensive tests for projects API routes.
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_project_service():
    """Mock ProjectService."""
    with patch("backend.api.routes.projects.ProjectService") as mock:
        service_instance = AsyncMock()
        mock.return_value = service_instance
        yield service_instance


@pytest.fixture
def sample_project():
    """Sample project data."""
    return {
        "id": "proj123",
        "name": "Test Project",
        "description": "A test project",
        "owner_id": "user123",
        "status": "active",
        "visibility": "private",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


class TestProjectRoutes:
    """Tests for project API routes."""

    def test_create_project_success(self, client, mock_project_service, sample_project):
        """Test successful project creation."""
        mock_project_service.create_project.return_value = sample_project

        response = client.post(
            "/projects",
            json={
                "name": "Test Project",
                "description": "A test project",
                "visibility": "private"
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Project"
        assert data["data"]["visibility"] == "private"

    def test_create_project_validation_error(self, client, mock_project_service):
        """Test project creation with validation errors."""
        response = client.post(
            "/projects",
            json={
                "name": "",  # Empty name should fail validation
                "description": "A test project"
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 422  # Validation error

    def test_list_projects_success(self, client, mock_project_service):
        """Test listing projects."""
        mock_projects = [
            {
                "id": "proj1",
                "name": "Project 1",
                "description": "First project",
                "owner_id": "user123",
                "status": "active"
            },
            {
                "id": "proj2",
                "name": "Project 2",
                "description": "Second project",
                "owner_id": "user123",
                "status": "active"
            }
        ]
        mock_project_service.list_projects.return_value = mock_projects

        response = client.get(
            "/projects",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Project 1"

    def test_get_project_success(self, client, mock_project_service, sample_project):
        """Test getting specific project."""
        mock_project_service.get_project.return_value = sample_project

        response = client.get(
            "/projects/proj123",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "proj123"
        assert data["data"]["name"] == "Test Project"

    def test_get_project_not_found(self, client, mock_project_service):
        """Test getting non-existent project."""
        from backend.core.exceptions import NotFoundError
        mock_project_service.get_project.side_effect = NotFoundError("Project not found")

        response = client.get(
            "/projects/nonexistent",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()

    def test_update_project_success(self, client, mock_project_service, sample_project):
        """Test updating project."""
        updated_project = sample_project.copy()
        updated_project["name"] = "Updated Project Name"
        updated_project["description"] = "Updated description"
        mock_project_service.update_project.return_value = updated_project

        response = client.put(
            "/projects/proj123",
            json={
                "name": "Updated Project Name",
                "description": "Updated description",
                "visibility": "public"
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Updated Project Name"

    def test_update_project_partial(self, client, mock_project_service, sample_project):
        """Test partial project update."""
        updated_project = sample_project.copy()
        updated_project["name"] = "Partially Updated Name"
        mock_project_service.update_project.return_value = updated_project

        # Only update name, keep other fields
        response = client.patch(
            "/projects/proj123",
            json={"name": "Partially Updated Name"},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Partially Updated Name"

    def test_delete_project_success(self, client, mock_project_service):
        """Test deleting project."""
        mock_project_service.delete_project.return_value = True

        response = client.delete(
            "/projects/proj123",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted" in data["message"].lower()

    def test_delete_project_not_found(self, client, mock_project_service):
        """Test deleting non-existent project."""
        from backend.core.exceptions import NotFoundError
        mock_project_service.delete_project.side_effect = NotFoundError("Project not found")

        response = client.delete(
            "/projects/nonexistent",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 404

    def test_archive_project_success(self, client, mock_project_service, sample_project):
        """Test archiving project."""
        archived_project = sample_project.copy()
        archived_project["status"] = "archived"
        mock_project_service.archive_project.return_value = archived_project

        response = client.post(
            "/projects/proj123/archive",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "archived"

    def test_unarchive_project_success(self, client, mock_project_service, sample_project):
        """Test unarchiving project."""
        active_project = sample_project.copy()
        active_project["status"] = "active"
        mock_project_service.unarchive_project.return_value = active_project

        response = client.post(
            "/projects/proj123/unarchive",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "active"

    def test_list_project_members_success(self, client, mock_project_service):
        """Test listing project members."""
        mock_members = [
            {
                "user_id": "user1",
                "username": "member1",
                "role": "developer",
                "joined_at": "2024-01-01T00:00:00Z"
            },
            {
                "user_id": "user2",
                "username": "member2",
                "role": "viewer",
                "joined_at": "2024-01-02T00:00:00Z"
            }
        ]
        mock_project_service.list_project_members.return_value = mock_members

        response = client.get(
            "/projects/proj123/members",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["role"] == "developer"

    def test_add_project_member_success(self, client, mock_project_service):
        """Test adding member to project."""
        mock_member = {
            "user_id": "newuser123",
            "username": "newmember",
            "role": "developer",
            "joined_at": "2024-01-03T00:00:00Z"
        }
        mock_project_service.add_project_member.return_value = mock_member

        response = client.post(
            "/projects/proj123/members",
            json={
                "user_id": "newuser123",
                "role": "developer"
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == "newuser123"
        assert data["data"]["role"] == "developer"

    def test_remove_project_member_success(self, client, mock_project_service):
        """Test removing member from project."""
        mock_project_service.remove_project_member.return_value = True

        response = client.delete(
            "/projects/proj123/members/user123",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removed" in data["message"].lower()

    def test_update_member_role_success(self, client, mock_project_service):
        """Test updating member role."""
        mock_updated_member = {
            "user_id": "user123",
            "username": "member",
            "role": "admin",
            "joined_at": "2024-01-01T00:00:00Z"
        }
        mock_project_service.update_member_role.return_value = mock_updated_member

        response = client.put(
            "/projects/proj123/members/user123",
            json={"role": "admin"},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["role"] == "admin"

    def test_get_project_stats_success(self, client, mock_project_service):
        """Test getting project statistics."""
        mock_stats = {
            "total_members": 5,
            "total_workflows": 12,
            "total_agents": 8,
            "created_at": "2024-01-01T00:00:00Z",
            "last_activity": "2024-01-15T10:30:00Z"
        }
        mock_project_service.get_project_statistics.return_value = mock_stats

        response = client.get(
            "/projects/proj123/stats",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_members"] == 5
        assert data["data"]["total_workflows"] == 12

    def test_search_projects_success(self, client, mock_project_service):
        """Test searching projects."""
        mock_projects = [
            {
                "id": "proj1",
                "name": "Search Result 1",
                "description": "Matches search term",
                "owner_id": "user123"
            }
        ]
        mock_project_service.search_projects.return_value = mock_projects

        response = client.get(
            "/projects/search?q=search+term",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert "search" in data["data"][0]["name"].lower()

    def test_list_user_projects_success(self, client, mock_project_service):
        """Test listing projects for specific user."""
        mock_projects = [
            {"id": "proj1", "name": "User Project 1", "owner_id": "specific-user"},
            {"id": "proj2", "name": "User Project 2", "owner_id": "specific-user"}
        ]
        mock_project_service.list_user_projects.return_value = mock_projects

        response = client.get(
            "/projects/user/specific-user",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert all(p["owner_id"] == "specific-user" for p in data["data"])

    def test_duplicate_project_success(self, client, mock_project_service, sample_project):
        """Test duplicating project."""
        duplicated_project = sample_project.copy()
        duplicated_project["id"] = "new-proj-id"
        duplicated_project["name"] = "Copy of Test Project"
        mock_project_service.duplicate_project.return_value = duplicated_project

        response = client.post(
            "/projects/proj123/duplicate",
            json={"name": "Copy of Test Project"},
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Copy of Test Project"
        assert data["data"]["id"] != "proj123"  # Should have new ID

    def test_export_project_success(self, client, mock_project_service):
        """Test exporting project."""
        mock_export_data = {
            "project": {"id": "proj123", "name": "Test Project"},
            "workflows": [],
            "agents": [],
            "exported_at": "2024-01-15T10:30:00Z"
        }
        mock_project_service.export_project.return_value = mock_export_data

        response = client.get(
            "/projects/proj123/export",
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "project" in data["data"]
        assert "exported_at" in data["data"]

    def test_import_project_success(self, client, mock_project_service, sample_project):
        """Test importing project."""
        mock_project_service.import_project.return_value = sample_project

        # Mock file upload
        response = client.post(
            "/projects/import",
            json={
                "project_data": {
                    "name": "Imported Project",
                    "description": "Imported from export"
                }
            },
            headers={"Authorization": "Bearer valid-token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Project"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
