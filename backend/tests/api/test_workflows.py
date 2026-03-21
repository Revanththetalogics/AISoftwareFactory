"""
Tests for Workflows API Routes.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock, MagicMock
from datetime import datetime
from contextlib import asynccontextmanager

from backend.main import app
from backend.db.session import get_db
from backend.api.dependencies import get_current_user, get_workflow_service
from backend.services.auth_service import AuthService
from backend.models.workflow import WorkflowStatus


# Create mock db session
async def mock_get_db():
    """Mock database dependency."""
    mock_session = AsyncMock()
    
    # Create proper mock result for db.execute()
    mock_scalars = Mock()
    mock_scalars.all.return_value = []  # Return empty list
    
    mock_result = Mock()
    mock_result.scalars.return_value = mock_scalars
    
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
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


def get_auth_headers():
    """Generate authentication headers for tests."""
    auth_service = AuthService()
    token = auth_service.create_access_token({
        "sub": "user-dev-001",
        "username": "developer"
    })
    return {"Authorization": f"Bearer {token}"}


def create_mock_workflow(workflow_id="wf-test-123", project_id="proj-test-123", status=WorkflowStatus.PENDING):
    """Create a mock workflow object matching DBWorkflow structure."""
    workflow = Mock()
    workflow.id = workflow_id
    workflow.name = f"Workflow for {project_id}"
    workflow.project_id = project_id
    workflow.status = status
    workflow.steps = [
        {"id": "requirements", "name": "Requirements Analysis"},
        {"id": "design", "name": "System Design"},
    ]
    workflow.completed_steps = []
    workflow.current_step_id = None
    workflow.context = {}
    workflow.started_at = None
    workflow.completed_at = None
    workflow.created_at = datetime.utcnow()
    workflow.updated_at = datetime.utcnow()
    return workflow


def mock_get_workflow_service():
    """Mock workflow service dependency."""
    mock_service = AsyncMock()
    
    # Create workflow returns a mock workflow
    async def mock_create_workflow(name, project_id, steps, created_by=None, db=None):
        return create_mock_workflow(project_id=project_id)
    
    mock_service.create_workflow = mock_create_workflow
    mock_service.get_workflow = AsyncMock(return_value=None)  # Default to not found
    mock_service.update_workflow_status = AsyncMock()
    
    return mock_service


@asynccontextmanager
async def mock_get_db_context():
    """Mock database context manager for background tasks."""
    mock_session = AsyncMock()
    
    # Create proper mock result for db.execute()
    mock_scalars = Mock()
    mock_scalars.all.return_value = []  # Return empty list
    
    mock_result = Mock()
    mock_result.scalars.return_value = mock_scalars
    
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    yield mock_session


# Override the dependencies
app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_workflow_service] = mock_get_workflow_service

# Create authenticated client
client = TestClient(app)
# Add default auth headers to pass the global middleware check
_auth_headers = get_auth_headers()


@pytest.fixture
def mock_workflow():
    """Create a mock workflow."""
    return create_mock_workflow()


class TestExecuteWorkflow:
    """Test cases for POST /workflows/execute."""
    
    @patch("backend.db.session.get_db_context", new=mock_get_db_context)
    @patch("backend.services.database_services.get_db_context", new=mock_get_db_context)
    def test_execute_workflow(self):
        """Test executing a workflow."""
        response = client.post(
            "/api/v1/workflows/execute",
            json={
                "project_id": "proj-123",
                "phase": "implementation",
                "async_execution": True,
            },
            headers=_auth_headers,
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending"
        assert "workflow_id" in data


class TestGetWorkflowStatus:
    """Test cases for GET /workflows/{id}."""
    
    def test_get_workflow_not_found(self):
        """Test 404 for nonexistent workflow."""
        response = client.get("/api/v1/workflows/nonexistent", headers=_auth_headers)
        
        assert response.status_code == 404


class TestListWorkflows:
    """Test cases for GET /workflows."""
    
    def test_list_workflows(self):
        """Test listing workflows."""
        response = client.get("/api/v1/workflows", headers=_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCancelWorkflow:
    """Test cases for POST /workflows/{id}/cancel."""
    
    def test_cancel_workflow_not_found(self):
        """Test 404 for nonexistent workflow."""
        response = client.post("/api/v1/workflows/nonexistent/cancel", headers=_auth_headers)
        
        assert response.status_code == 404


class TestGetAvailablePhases:
    """Test cases for GET /workflows/phases/available."""
    
    def test_get_phases(self):
        """Test getting available phases."""
        response = client.get("/api/v1/workflows/phases/available", headers=_auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "requirements" in data
