"""
Pytest configuration and fixtures for AI Software Factory tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
from datetime import datetime
import uuid


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
def mock_db_user():
    """Fixture for mocked database user."""
    user = Mock()
    user.id = f"user-test-{uuid.uuid4().hex[:8]}"
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = "$2b$12$test_hashed_password"
    user.permissions = ["read", "write", "execute"]
    user.is_active = True
    user.is_superuser = False
    user.first_name = "Test"
    user.last_name = "User"
    user.last_login = None
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    return user


@pytest.fixture
def mock_auth_service(mock_db_user):
    """Fixture for mocked auth service with database user support."""
    with patch('backend.services.auth_service.AsyncSessionLocal') as mock_session_local:
        # Create a mock session context manager
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session_local.return_value = mock_session
        
        # Mock the execute method to return our mock user
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_db_user)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.get = AsyncMock(return_value=mock_db_user)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        yield mock_session


@pytest.fixture
def test_client():
    """Fixture for FastAPI test client."""
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(mock_db_user):
    """Fixture for authentication headers with mocked DB user."""
    from backend.services.auth_service import AuthService
    
    # Create a valid token for testing using the mock user ID
    auth_service = AuthService()
    test_user_data = {
        "sub": mock_db_user.id,
        "username": mock_db_user.username,
        "permissions": mock_db_user.permissions
    }
    token = auth_service.create_access_token(test_user_data)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def authenticated_client(auth_headers, mock_auth_service, mock_db_user):
    """Fixture for authenticated test client with mocked DB."""
    from fastapi.testclient import TestClient
    from backend.main import app
    
    # Patch the auth service methods to use our mock
    with patch('backend.api.dependencies.get_auth_service') as mock_get_auth:
        from backend.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Mock the get_user_by_id method
        auth_service.get_user_by_id = AsyncMock(return_value=mock_db_user)
        mock_get_auth.return_value = auth_service
        
        client = TestClient(app)
        client.headers.update(auth_headers)
        yield client


@pytest.fixture
def mock_db_session():
    """Fixture for mocked database session."""
    session = AsyncMock()
    # Mock common session methods
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    session.add = Mock()
    return session


@pytest.fixture
def mock_project_service(mock_db_session):
    """Fixture for mocked project service."""
    
    # Create mock project
    mock_project = Mock()
    mock_project.id = "proj-test-123"
    mock_project.name = "Test Project"
    mock_project.description = "A test project"
    mock_project.status = "draft"
    mock_project.tech_stack = {}
    mock_project.current_phase = None
    mock_project.progress_percent = 0
    mock_project.owner_id = "user-test-001"
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
