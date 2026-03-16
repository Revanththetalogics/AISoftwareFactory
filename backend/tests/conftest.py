"""
Pytest configuration and fixtures for AI Software Factory backend tests.

This module provides shared fixtures and configuration for all tests.
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Set testing environment before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["SECRET_KEY"] = "test-secret-key"

from backend.main import app


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI application.
    
    This fixture provides a TestClient instance that can be used
    to make requests to the application in tests.
    
    Yields:
        TestClient: FastAPI test client
        
    Example:
        >>> def test_health(client):
        ...     response = client.get("/api/v1/health")
        ...     assert response.status_code == 200
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def reset_correlation_id():
    """Reset correlation ID before each test."""
    from backend.core.logging import clear_correlation_id
    clear_correlation_id()
    yield


@pytest.fixture(autouse=True)
def reset_agent_registry_fixture():
    """Reset agent registry before each test."""
    from backend.agents.agent_registry import reset_agent_registry
    reset_agent_registry()
    yield
