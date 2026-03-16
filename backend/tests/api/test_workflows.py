"""
Tests for Workflows API Routes.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestExecuteWorkflow:
    """Test cases for POST /workflows/execute."""
    
    def test_execute_workflow(self):
        """Test executing a workflow."""
        response = client.post(
            "/api/v1/workflows/execute",
            json={
                "project_id": "proj-123",
                "phase": "implementation",
                "async_execution": True,
            },
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending"
        assert "workflow_id" in data


class TestGetWorkflowStatus:
    """Test cases for GET /workflows/{id}."""
    
    def test_get_workflow_not_found(self):
        """Test 404 for nonexistent workflow."""
        response = client.get("/api/v1/workflows/nonexistent")
        
        assert response.status_code == 404


class TestListWorkflows:
    """Test cases for GET /workflows."""
    
    def test_list_workflows(self):
        """Test listing workflows."""
        response = client.get("/api/v1/workflows")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCancelWorkflow:
    """Test cases for POST /workflows/{id}/cancel."""
    
    def test_cancel_workflow_not_found(self):
        """Test 404 for nonexistent workflow."""
        response = client.post("/api/v1/workflows/nonexistent/cancel")
        
        assert response.status_code == 404


class TestGetAvailablePhases:
    """Test cases for GET /workflows/phases/available."""
    
    def test_get_phases(self):
        """Test getting available phases."""
        response = client.get("/api/v1/workflows/phases/available")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "requirements" in data
