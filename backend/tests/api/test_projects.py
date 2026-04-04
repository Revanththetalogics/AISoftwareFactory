"""
Tests for Projects API Routes.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from backend.db.session import get_db
from backend.main import app


# Create mock db session
async def mock_get_db():
    """Mock database dependency."""
    mock_session = AsyncMock()
    yield mock_session


# Override the dependency
app.dependency_overrides[get_db] = mock_get_db

client = TestClient(app)


@pytest.fixture
def mock_project():
    """Create a mock project."""
    project = Mock()
    project.id = "proj-test-123"
    project.name = "Test Project"
    project.description = "A test project"
    project.requirements = "Test requirements"
    project.status = "draft"
    project.tech_stack = {}
    project.current_phase = None
    project.progress_percent = 0
    project.owner_id = "user-dev-001"
    project.extra_metadata = {}
    project.created_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    return project


class TestCreateProject:
    """Test cases for POST /projects."""

    def test_create_project_success(self, authenticated_client, mock_project):
        """Test creating a project."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.create_project = AsyncMock(return_value=mock_project)

            response = authenticated_client.post(
                "/api/v1/projects",
                json={
                    "name": "Test Project",
                    "description": "A test project",
                    "requirements": "API, Auth",
                },
            )

            assert response.status_code == 201
            data = response.json()
            assert data["name"] == "Test Project"
            assert data["status"] == "draft"
            assert "id" in data

    def test_create_project_validation_error(self, authenticated_client):
        """Test validation error."""
        response = authenticated_client.post(
            "/api/v1/projects",
            json={"name": "", "description": "Test"},
        )

        assert response.status_code == 422


class TestListProjects:
    """Test cases for GET /projects."""

    def test_list_projects(self, authenticated_client, mock_project):
        """Test listing projects."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.list_projects = AsyncMock(return_value=[mock_project])

            response = authenticated_client.get("/api/v1/projects")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_list_projects_with_filter(self, authenticated_client, mock_project):
        """Test filtering by status."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.list_projects = AsyncMock(return_value=[mock_project])

            response = authenticated_client.get("/api/v1/projects?status=draft")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestGetProject:
    """Test cases for GET /projects/{id}."""

    def test_get_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            response = authenticated_client.get("/api/v1/projects/nonexistent")

            assert response.status_code == 404


class TestUpdateProject:
    """Test cases for PATCH /projects/{id}."""

    def test_update_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            response = authenticated_client.patch(
                "/api/v1/projects/nonexistent",
                json={"name": "Updated"},
            )

            assert response.status_code == 404


class TestDeleteProject:
    """Test cases for DELETE /projects/{id}."""

    def test_delete_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            response = authenticated_client.delete("/api/v1/projects/nonexistent")

            assert response.status_code == 404


class TestActivateProject:
    """Test cases for POST /projects/{id}/activate."""

    def test_activate_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        with patch("backend.api.routes.projects.project_service") as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            response = authenticated_client.post("/api/v1/projects/nonexistent/activate")

            assert response.status_code == 404
