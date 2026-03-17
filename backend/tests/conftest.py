"""
Pytest configuration and fixtures for AI Software Factory tests.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import asyncio


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
