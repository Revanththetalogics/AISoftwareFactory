"""
Tests for API Models.
"""

from datetime import datetime

import pytest

from backend.api.models import (
    AgentResponse,
    DeploymentRequest,
    DeploymentResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectStatus,
    WorkflowExecuteRequest,
    WorkflowStatusResponse,
)


class TestProjectCreate:
    """Test cases for ProjectCreate model."""

    def test_valid_creation(self):
        """Test creating valid project."""
        project = ProjectCreate(
            name="Test Project",
            description="A test project",
            requirements="User auth, API",
        )

        assert project.name == "Test Project"
        assert project.description == "A test project"

    def test_name_validation(self):
        """Test name length validation."""
        with pytest.raises(ValueError):
            ProjectCreate(name="", description="Test")

    def test_optional_requirements(self):
        """Test requirements is optional."""
        project = ProjectCreate(
            name="Test",
            description="Test project",
        )

        assert project.requirements is None


class TestProjectResponse:
    """Test cases for ProjectResponse model."""

    def test_response_creation(self):
        """Test creating response."""
        response = ProjectResponse(
            id="proj-123",
            name="Test",
            description="Test project",
            status=ProjectStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert response.id == "proj-123"
        assert response.progress_percent == 0


class TestWorkflowExecuteRequest:
    """Test cases for WorkflowExecuteRequest."""

    def test_valid_request(self):
        """Test valid execution request."""
        request = WorkflowExecuteRequest(
            project_id="proj-123",
            phase="implementation",
        )

        assert request.project_id == "proj-123"
        assert request.phase == "implementation"
        assert request.async_execution is True


class TestWorkflowStatusResponse:
    """Test cases for WorkflowStatusResponse."""

    def test_response_creation(self):
        """Test creating workflow status response."""
        response = WorkflowStatusResponse(
            workflow_id="wf-123",
            project_id="proj-123",
            status="running",
            progress_percent=50,
        )

        assert response.workflow_id == "wf-123"
        assert response.progress_percent == 50


class TestAgentResponse:
    """Test cases for AgentResponse."""

    def test_response_creation(self):
        """Test creating agent response."""
        response = AgentResponse(
            agent_id="agent-123",
            name="Test Agent",
            role="engineer",
            capabilities=["coding"],
            status="idle",
        )

        assert response.agent_id == "agent-123"
        assert response.status == "idle"


class TestDeploymentRequest:
    """Test cases for DeploymentRequest."""

    def test_valid_request(self):
        """Test valid deployment request."""
        request = DeploymentRequest(
            project_id="proj-123",
            environment="staging",
            version="1.0.0",
        )

        assert request.project_id == "proj-123"
        assert request.environment == "staging"

    def test_invalid_environment(self):
        """Test invalid environment validation."""
        with pytest.raises(ValueError):
            DeploymentRequest(
                project_id="proj-123",
                environment="invalid",
                version="1.0.0",
            )


class TestDeploymentResponse:
    """Test cases for DeploymentResponse."""

    def test_response_creation(self):
        """Test creating deployment response."""
        response = DeploymentResponse(
            deployment_id="dep-123",
            project_id="proj-123",
            environment="staging",
            version="1.0.0",
            status="running",
        )

        assert response.deployment_id == "dep-123"
        assert response.status == "running"
