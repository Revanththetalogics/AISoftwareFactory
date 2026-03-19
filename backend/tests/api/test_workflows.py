"""
Tests for Workflows API Routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock
from datetime import datetime

from backend.main import app
from backend.db.session import get_db
from backend.api.dependencies import get_current_user


# Create mock db session
async def mock_get_db():
    """Mock database dependency."""
    mock_session = AsyncMock()
    yield mock_session


# Create mock user
async def mock_get_current_user():
    """Mock current user dependency."""
    from backend.api.dependencies import User
    return User(
        user_id="user-dev-001",
        username="developer",
        email="dev@example.com",
        permissions=["read", "write", "execute"],
    )


# Override the dependencies
app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)


@pytest.fixture
def mock_workflow():
    """Create a mock workflow."""
    workflow = Mock()
    workflow.id = "wf-test-123"
    workflow.name = "Test Workflow"
    workflow.project_id = "proj-test-123"
    workflow.status = "pending"
    workflow.steps = []
    workflow.created_at = datetime.utcnow()
    workflow.updated_at = datetime.utcnow()
    return workflow


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
