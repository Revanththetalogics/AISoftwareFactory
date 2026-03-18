"""
Pytest configuration and fixtures for AI Software Factory tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import asyncio
from datetime import datetime


@pytest.fixture
def mock_llm():
    """Fixture for mocked LLM provider."""
    llm = Mock()
    llm.generate = AsyncMock(return_value="Test response")
    llm.generate_stream = AsyncMock(return_value=["Test", " response"])
    return llm


@pytest.fixture
def mock_vector_store():
    """Fixture for mocked vector store."""
    store = Mock()
    store.add = AsyncMock(return_value=["id1", "id2"])
    store.search = AsyncMock(return_value=[
        {"id": "1", "text": "test", "score": 0.9}
    ])
    return store


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_project_data():
    """Fixture for sample project data."""
    return {
        "name": "Test Project",
        "description": "A test project",
        "tech_stack": ["python", "fastapi"]
    }


@pytest.fixture
def sample_workflow_data():
    """Fixture for sample workflow data."""
    return {
        "name": "Test Workflow",
        "steps": ["step1", "step2"],
        "status": "pending"
    }


@pytest.fixture
def test_client():
    """Fixture for FastAPI test client."""
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Fixture for authentication headers."""
    from backend.services.auth_service import AuthService
    
    # Create a valid token for testing using existing user ID
    auth_service = AuthService()
    test_user_data = {
        "sub": "user-dev-001",  # Use existing user ID
        "username": "developer",
        "permissions": ["read", "write", "execute"]
    }
    token = auth_service.create_access_token(test_user_data)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def authenticated_client(auth_headers):
    """Fixture for authenticated test client."""
    from fastapi.testclient import TestClient
    from backend.main import app
    
    client = TestClient(app)
    # Add default authentication headers
    client.headers.update(auth_headers)
    return client


@pytest.fixture
def mock_db_session():
    """Fixture for mocked database session."""
    session = AsyncMock()
    # Mock common session methods
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_project_service(mock_db_session):
    """Fixture for mocked project service."""
    from unittest.mock import patch
    
    # Create mock project
    mock_project = Mock()
    mock_project.id = "proj-test-123"
    mock_project.name = "Test Project"
    mock_project.description = "A test project"
    mock_project.status = "draft"
    mock_project.tech_stack = {}
    mock_project.current_phase = None
    mock_project.progress_percent = 0
    mock_project.owner_id = "user-dev-001"
    mock_project.extra_metadata = {}
    mock_project.created_at = datetime.utcnow()
    mock_project.updated_at = datetime.utcnow()
    
    # Mock the service
    with patch('backend.services.database_services.get_project_service') as mock_get_service:
        service = AsyncMock()
        service.create_project = AsyncMock(return_value=mock_project)
        service.get_project = AsyncMock(return_value=mock_project)
        service.list_projects = AsyncMock(return_value=[mock_project])
        service.update_project = AsyncMock(return_value=mock_project)
        service.delete_project = AsyncMock(return_value=True)
        
        mock_get_service.return_value = service
        yield service
