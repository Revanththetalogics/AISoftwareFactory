"""
Tests for Projects API Routes.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestCreateProject:
    """Test cases for POST /projects."""
    
    def test_create_project_success(self, authenticated_client):
        """Test creating a project."""
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
    
    def test_list_projects(self, authenticated_client):
        """Test listing projects."""
        response = authenticated_client.get("/api/v1/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_projects_with_filter(self, authenticated_client):
        """Test filtering by status."""
        response = authenticated_client.get("/api/v1/projects?status=draft")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestGetProject:
    """Test cases for GET /projects/{id}."""
    
    def test_get_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        response = authenticated_client.get("/api/v1/projects/nonexistent")
        
        assert response.status_code == 404


class TestUpdateProject:
    """Test cases for PATCH /projects/{id}."""
    
    def test_update_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        response = authenticated_client.patch(
            "/api/v1/projects/nonexistent",
            json={"name": "Updated"},
        )
        
        assert response.status_code == 404


class TestDeleteProject:
    """Test cases for DELETE /projects/{id}."""
    
    def test_delete_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        response = authenticated_client.delete("/api/v1/projects/nonexistent")
        
        assert response.status_code == 404


class TestActivateProject:
    """Test cases for POST /projects/{id}/activate."""
    
    def test_activate_project_not_found(self, authenticated_client):
        """Test 404 for nonexistent project."""
        response = authenticated_client.post("/api/v1/projects/nonexistent/activate")
        
        assert response.status_code == 404
