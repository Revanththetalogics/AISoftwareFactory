"""
Comprehensive tests for API routes edge cases.

Covers edge cases and error paths for:
- agents.py
- deployments.py
- projects.py
- workflows.py
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# ==============================================================================
# Agent Routes Tests
# ==============================================================================

class TestAgentRoutes:
    """Tests for agent routes edge cases."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_agent_service(self):
        """Create mock agent service."""
        service = MagicMock()
        service.list_agents = AsyncMock(return_value=[])
        service.get_agent = AsyncMock(return_value=None)
        service.register_agent = AsyncMock()
        return service

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock()
        user.user_id = "test-user-123"
        return user

    @pytest.fixture
    def sample_agent(self):
        """Create sample agent."""
        agent = MagicMock()
        agent.id = "agent-123"
        agent.name = "Test Agent"
        agent.role = "backend_engineer"
        agent.capabilities = ["python", "testing"]
        agent.status = "idle"
        agent.current_task_id = None
        agent.last_active = datetime.now()
        agent.config = {"key": "value"}
        return agent

    @pytest.mark.asyncio
    async def test_list_agents_empty(self, mock_db, mock_agent_service, mock_user):
        """Test listing agents when none exist."""
        from backend.api.routes.agents import list_agents

        with patch('backend.api.routes.agents.get_current_user', return_value=mock_user):
            result = await list_agents(
                role=None,
                agent_status=None,
                user=mock_user,
                db=mock_db,
                agent_service=mock_agent_service
            )

        assert result == []
        mock_agent_service.list_agents.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_agents_with_filter(self, mock_db, mock_agent_service, mock_user, sample_agent):
        """Test listing agents with role filter."""
        from backend.api.routes.agents import list_agents

        mock_agent_service.list_agents.return_value = [sample_agent]

        with patch('backend.api.routes.agents.get_current_user', return_value=mock_user):
            result = await list_agents(
                role="backend_engineer",
                agent_status="idle",
                user=mock_user,
                db=mock_db,
                agent_service=mock_agent_service
            )

        assert len(result) == 1
        assert result[0].role == "backend_engineer"
        mock_agent_service.list_agents.assert_called_once_with(
            role="backend_engineer",
            status="idle",
            db=mock_db
        )

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, mock_db, mock_agent_service, mock_user):
        """Test getting non-existent agent."""
        from backend.api.routes.agents import get_agent

        mock_agent_service.get_agent.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_agent(
                agent_id="nonexistent-agent",
                user=mock_user,
                db=mock_db,
                agent_service=mock_agent_service
            )

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_agent_success(self, mock_db, mock_agent_service, mock_user, sample_agent):
        """Test getting existing agent."""
        from backend.api.routes.agents import get_agent

        mock_agent_service.get_agent.return_value = sample_agent

        result = await get_agent(
            agent_id="agent-123",
            user=mock_user,
            db=mock_db,
            agent_service=mock_agent_service
        )

        assert result.agent_id == "agent-123"
        assert result.name == "Test Agent"

    @pytest.mark.asyncio
    async def test_register_agent(self, mock_db, mock_agent_service, mock_user, sample_agent):
        """Test registering a new agent."""
        from backend.api.routes.agents import register_agent

        mock_agent_service.register_agent.return_value = sample_agent

        result = await register_agent(
            name="Test Agent",
            role="backend_engineer",
            capabilities=["python"],
            user=mock_user,
            db=mock_db,
            agent_service=mock_agent_service
        )

        assert result.name == "Test Agent"
        mock_agent_service.register_agent.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_task_agent_not_found(self, mock_db, mock_agent_service, mock_user):
        """Test assigning task to non-existent agent."""
        from backend.api.models import AgentTaskRequest
        from backend.api.routes.agents import assign_task

        mock_agent_service.get_agent.return_value = None
        request = AgentTaskRequest(task_type="test", description="Test task", context={})

        with pytest.raises(HTTPException) as exc_info:
            await assign_task(
                agent_id="nonexistent",
                request=request,
                user=mock_user,
                db=mock_db,
                agent_service=mock_agent_service
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_assign_task_agent_busy(self, mock_db, mock_agent_service, mock_user, sample_agent):
        """Test assigning task to busy agent."""
        from backend.api.models import AgentTaskRequest
        from backend.api.routes.agents import assign_task

        sample_agent.status = "busy"
        mock_agent_service.get_agent.return_value = sample_agent
        request = AgentTaskRequest(task_type="test", description="Test task", context={})

        with pytest.raises(HTTPException) as exc_info:
            await assign_task(
                agent_id="agent-123",
                request=request,
                user=mock_user,
                db=mock_db,
                agent_service=mock_agent_service
            )

        assert exc_info.value.status_code == 409
        assert "busy" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_assign_task_success(self, mock_db, mock_agent_service, mock_user, sample_agent):
        """Test successful task assignment."""
        from backend.api.models import AgentTaskRequest
        from backend.api.routes.agents import assign_task

        sample_agent.status = "idle"
        mock_agent_service.get_agent.return_value = sample_agent
        request = AgentTaskRequest(
            task_type="code_review",
            description="Review test.py",
            context={"file": "test.py"}
        )

        result = await assign_task(
            agent_id="agent-123",
            request=request,
            user=mock_user,
            db=mock_db,
            agent_service=mock_agent_service
        )

        assert result.agent_id == "agent-123"
        assert result.status == "accepted"
        assert "task-" in result.task_id

    @pytest.mark.asyncio
    async def test_get_available_roles(self, mock_user):
        """Test getting available roles."""
        from backend.api.routes.agents import get_available_roles

        result = await get_available_roles(user=mock_user)

        assert isinstance(result, list)
        assert "ceo" in result
        assert "backend_engineer" in result


# ==============================================================================
# Deployment Routes Tests
# ==============================================================================

class TestDeploymentRoutes:
    """Tests for deployment routes edge cases."""

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock()
        user.user_id = "test-user-123"
        return user

    @pytest.fixture
    def sample_deployment(self):
        """Create sample deployment."""
        from backend.deployment.orchestrator import DeploymentEnvironment, DeploymentStatus

        deployment = MagicMock()
        deployment.deployment_id = "deploy-123"
        deployment.project_name = "test-project"
        deployment.environment = DeploymentEnvironment.DEVELOPMENT
        deployment.status = DeploymentStatus.PENDING
        deployment.steps = []
        deployment.started_at = datetime.now()
        deployment.completed_at = None
        return deployment

    @pytest.mark.asyncio
    async def test_create_deployment_invalid_environment(self, mock_user):
        """Test creating deployment with invalid environment."""
        from backend.api.models import DeploymentRequest

        # DeploymentRequest validation happens at model level
        with pytest.raises(Exception):  # Pydantic ValidationError
            DeploymentRequest(
                project_id="test-project",
                environment="invalid_env",  # Invalid
                version="1.0.0"
            )

    @pytest.mark.asyncio
    async def test_create_deployment_success(self, mock_user):
        """Test successful deployment creation."""
        from backend.api.models import DeploymentRequest
        from backend.api.routes.deployments import create_deployment

        request = DeploymentRequest(
            project_id="test-project",
            environment="dev",  # Valid: dev, staging, or production
            version="1.0.0",
            config={"debug": True}
        )

        with patch('backend.api.routes.deployments._orchestrator') as mock_orch:
            mock_result = MagicMock()
            mock_result.deployment_id = "deploy-123"
            mock_result.project_name = "test-project"
            mock_result.environment.value = "development"
            mock_result.status.value = "pending"
            mock_result.steps = []
            mock_result.started_at = datetime.now()
            mock_result.completed_at = None
            mock_orch.create_deployment.return_value = mock_result

            result = await create_deployment(request=request, user=mock_user)

        assert result.deployment_id == "deploy-123"
        assert result.environment == "development"

    @pytest.mark.asyncio
    async def test_list_deployments_empty(self, mock_user):
        """Test listing deployments when none exist."""
        from backend.api.routes.deployments import list_deployments

        with patch('backend.api.routes.deployments._orchestrator') as mock_orch:
            mock_orch.list_deployments.return_value = []

            result = await list_deployments(
                project_id=None,
                environment=None,
                user=mock_user
            )

        assert result == []

    @pytest.mark.asyncio
    async def test_list_deployments_with_invalid_env_filter(self, mock_user):
        """Test listing deployments with invalid environment filter."""
        from backend.api.routes.deployments import list_deployments

        with patch('backend.api.routes.deployments._orchestrator') as mock_orch:
            mock_orch.list_deployments.return_value = []

            # Invalid environment should be ignored, not raise error
            result = await list_deployments(
                project_id=None,
                environment="invalid_env",
                user=mock_user
            )

        assert result == []

    @pytest.mark.asyncio
    async def test_get_deployment_not_found(self, mock_user):
        """Test getting non-existent deployment."""
        from backend.api.routes.deployments import get_deployment

        with patch('backend.api.routes.deployments._orchestrator') as mock_orch:
            mock_orch.get_deployment.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_deployment(deployment_id="nonexistent", user=mock_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_deployment_not_found(self, mock_user):
        """Test cancelling non-existent deployment."""
        from backend.api.routes.deployments import cancel_deployment

        with patch('backend.api.routes.deployments._orchestrator') as mock_orch:
            mock_orch.cancel_deployment.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await cancel_deployment(deployment_id="nonexistent", user=mock_user)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_available_environments(self, mock_user):
        """Test getting available environments."""
        from backend.api.routes.deployments import get_available_environments

        result = await get_available_environments(user=mock_user)

        assert isinstance(result, list)
        assert "dev" in result  # DeploymentEnvironment.DEVELOPMENT.value
        assert "staging" in result
        assert "prod" in result  # DeploymentEnvironment.PRODUCTION.value


# ==============================================================================
# Project Routes Tests
# ==============================================================================

class TestProjectRoutes:
    """Tests for project routes edge cases."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock()
        user.user_id = "test-user-123"
        user.permissions = []
        return user

    @pytest.fixture
    def mock_admin_user(self):
        """Create mock admin user."""
        user = MagicMock()
        user.user_id = "admin-user-123"
        user.permissions = ["admin"]
        return user

    @pytest.fixture
    def sample_project(self):
        """Create sample project."""
        project = MagicMock()
        project.id = "project-123"
        project.name = "Test Project"
        project.description = "A test project"
        project.requirements = "Build something cool"
        project.status = "draft"
        project.tech_stack = {"backend": "python", "framework": "fastapi"}
        project.current_phase = None
        project.progress_percent = 0
        project.owner_id = "test-user-123"
        project.created_at = datetime.now()
        project.updated_at = datetime.now()
        project.extra_metadata = {}
        project.metadata = {}
        return project

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, mock_db, mock_user):
        """Test getting non-existent project."""
        from backend.api.routes.projects import get_project

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await get_project(
                    project_id="nonexistent",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_project_forbidden(self, mock_db, mock_user, sample_project):
        """Test getting project without ownership."""
        from backend.api.routes.projects import get_project

        sample_project.owner_id = "other-user-123"

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)

            with pytest.raises(HTTPException) as exc_info:
                await get_project(
                    project_id="project-123",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 403
        assert "Not authorized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_project_admin_access(self, mock_db, mock_admin_user, sample_project):
        """Test admin can access any project."""
        from backend.api.routes.projects import get_project

        sample_project.owner_id = "other-user-123"

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)

            # Admin should have access even without ownership
            result = await get_project(
                project_id="project-123",
                user=mock_admin_user,
                db=mock_db
            )

        assert result.id == "project-123"

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, mock_db, mock_user):
        """Test updating non-existent project."""
        from backend.api.models import ProjectUpdate
        from backend.api.routes.projects import update_project

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)
            request = ProjectUpdate(name="New Name")

            with pytest.raises(HTTPException) as exc_info:
                await update_project(
                    project_id="nonexistent",
                    request=request,
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_project_forbidden(self, mock_db, mock_user, sample_project):
        """Test updating project without ownership."""
        from backend.api.models import ProjectUpdate
        from backend.api.routes.projects import update_project

        sample_project.owner_id = "other-user-123"

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)
            request = ProjectUpdate(name="New Name")

            with pytest.raises(HTTPException) as exc_info:
                await update_project(
                    project_id="project-123",
                    request=request,
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, mock_db, mock_user):
        """Test deleting non-existent project."""
        from backend.api.routes.projects import delete_project

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await delete_project(
                    project_id="nonexistent",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_forbidden(self, mock_db, mock_user, sample_project):
        """Test deleting project without ownership."""
        from backend.api.routes.projects import delete_project

        sample_project.owner_id = "other-user-123"

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)

            with pytest.raises(HTTPException) as exc_info:
                await delete_project(
                    project_id="project-123",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_project_failure(self, mock_db, mock_user, sample_project):
        """Test delete operation failure."""
        from backend.api.routes.projects import delete_project

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)
            mock_service.delete_project = AsyncMock(return_value=False)

            with pytest.raises(HTTPException) as exc_info:
                await delete_project(
                    project_id="project-123",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 500
        assert "Failed to delete" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_activate_project_not_found(self, mock_db, mock_user):
        """Test activating non-existent project."""
        from backend.api.routes.projects import activate_project

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=None)

            with pytest.raises(HTTPException) as exc_info:
                await activate_project(
                    project_id="nonexistent",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_activate_project_forbidden(self, mock_db, mock_user, sample_project):
        """Test activating project without ownership."""
        from backend.api.routes.projects import activate_project

        sample_project.owner_id = "other-user-123"

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)

            with pytest.raises(HTTPException) as exc_info:
                await activate_project(
                    project_id="project-123",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_activate_project_wrong_status(self, mock_db, mock_user, sample_project):
        """Test activating project with wrong status."""
        from backend.api.routes.projects import activate_project

        sample_project.status = "active"  # Already active

        with patch('backend.api.routes.projects.project_service') as mock_service:
            mock_service.get_project = AsyncMock(return_value=sample_project)

            with pytest.raises(HTTPException) as exc_info:
                await activate_project(
                    project_id="project-123",
                    user=mock_user,
                    db=mock_db
                )

        assert exc_info.value.status_code == 400
        assert "Cannot activate" in exc_info.value.detail


# ==============================================================================
# Workflow Routes Tests
# ==============================================================================

class TestWorkflowRoutes:
    """Tests for workflow routes edge cases."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = AsyncMock(spec=AsyncSession)
        return db

    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = MagicMock()
        user.user_id = "test-user-123"
        return user

    @pytest.fixture
    def mock_workflow_service(self):
        """Create mock workflow service."""
        service = MagicMock()
        service.create_workflow = AsyncMock()
        service.get_workflow = AsyncMock()
        service.update_workflow_status = AsyncMock()
        return service

    @pytest.fixture
    def sample_workflow(self):
        """Create sample workflow."""
        from backend.models.workflow import WorkflowStatus

        workflow = MagicMock()
        workflow.id = "workflow-123"
        workflow.project_id = "project-123"
        workflow.status = WorkflowStatus.PENDING
        workflow.steps = [{"id": "step1"}]
        workflow.completed_steps = []
        workflow.current_step_id = None
        workflow.started_at = datetime.now()
        workflow.completed_at = None
        workflow.context = {}
        return workflow

    @pytest.mark.asyncio
    async def test_get_workflow_not_found(self, mock_db, mock_user, mock_workflow_service):
        """Test getting non-existent workflow."""
        from backend.api.routes.workflows import get_workflow_status

        mock_workflow_service.get_workflow.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_workflow_status(
                workflow_id="nonexistent",
                user=mock_user,
                db=mock_db,
                workflow_service=mock_workflow_service
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_workflow_success(self, mock_db, mock_user, mock_workflow_service, sample_workflow):
        """Test getting existing workflow."""
        from backend.api.routes.workflows import get_workflow_status

        mock_workflow_service.get_workflow.return_value = sample_workflow

        result = await get_workflow_status(
            workflow_id="workflow-123",
            user=mock_user,
            db=mock_db,
            workflow_service=mock_workflow_service
        )

        assert result.workflow_id == "workflow-123"

    @pytest.mark.asyncio
    async def test_cancel_workflow_not_found(self, mock_db, mock_user, mock_workflow_service):
        """Test cancelling non-existent workflow."""
        from backend.api.routes.workflows import cancel_workflow

        mock_workflow_service.get_workflow.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await cancel_workflow(
                workflow_id="nonexistent",
                user=mock_user,
                db=mock_db,
                workflow_service=mock_workflow_service
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_workflow_wrong_status(self, mock_db, mock_user, mock_workflow_service, sample_workflow):
        """Test cancelling workflow with wrong status."""
        from backend.api.routes.workflows import cancel_workflow
        from backend.models.workflow import WorkflowStatus

        sample_workflow.status = WorkflowStatus.COMPLETED

        mock_workflow_service.get_workflow.return_value = sample_workflow

        with pytest.raises(HTTPException) as exc_info:
            await cancel_workflow(
                workflow_id="workflow-123",
                user=mock_user,
                db=mock_db,
                workflow_service=mock_workflow_service
            )

        assert exc_info.value.status_code == 400
        assert "Cannot cancel" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_cancel_workflow_success(self, mock_db, mock_user, mock_workflow_service, sample_workflow):
        """Test successful workflow cancellation."""
        from backend.api.routes.workflows import cancel_workflow
        from backend.models.workflow import WorkflowStatus

        sample_workflow.status = WorkflowStatus.RUNNING
        mock_workflow_service.get_workflow.return_value = sample_workflow

        cancelled_workflow = MagicMock()
        cancelled_workflow.id = "workflow-123"
        cancelled_workflow.project_id = "project-123"
        cancelled_workflow.status = WorkflowStatus.CANCELLED
        cancelled_workflow.steps = []
        cancelled_workflow.completed_steps = []
        cancelled_workflow.current_step_id = None
        cancelled_workflow.started_at = datetime.now()
        cancelled_workflow.completed_at = datetime.now()
        cancelled_workflow.context = {}

        mock_workflow_service.update_workflow_status.return_value = cancelled_workflow

        result = await cancel_workflow(
            workflow_id="workflow-123",
            user=mock_user,
            db=mock_db,
            workflow_service=mock_workflow_service
        )

        assert result.status == "cancelled"

    @pytest.mark.asyncio
    async def test_get_available_phases(self, mock_user):
        """Test getting available phases."""
        from backend.api.routes.workflows import get_available_phases

        result = await get_available_phases(user=mock_user)

        assert isinstance(result, list)
        assert len(result) > 0
        assert "complete" not in result
        assert "failed" not in result

    @pytest.mark.asyncio
    async def test_list_workflows_with_filters(self, mock_db, mock_user):
        """Test listing workflows with status filter."""
        from backend.api.routes.workflows import list_workflows

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Test with invalid status - should be ignored
        result = await list_workflows(
            project_id="project-123",
            workflow_status="invalid_status",
            user=mock_user,
            db=mock_db
        )

        assert result == []


# ==============================================================================
# Helper Function Tests
# ==============================================================================

class TestRouteHelpers:
    """Tests for route helper functions."""

    def test_db_agent_to_response(self):
        """Test agent database to response conversion."""
        from backend.api.routes.agents import _db_agent_to_response

        agent = MagicMock()
        agent.id = "agent-123"
        agent.name = "Test Agent"
        agent.role = "tester"
        agent.capabilities = ["test"]
        agent.status = "idle"
        agent.current_task_id = None
        agent.last_active = datetime.now()
        agent.config = {"key": "value"}

        result = _db_agent_to_response(agent)

        assert result.agent_id == "agent-123"
        assert result.name == "Test Agent"
        assert result.metadata == {"key": "value"}

    def test_db_workflow_to_response(self):
        """Test workflow database to response conversion."""
        from backend.api.routes.workflows import _db_workflow_to_response
        from backend.models.workflow import WorkflowStatus

        workflow = MagicMock()
        workflow.id = "workflow-123"
        workflow.project_id = "project-123"
        workflow.status = WorkflowStatus.RUNNING
        workflow.steps = [{"id": "s1"}, {"id": "s2"}]
        workflow.completed_steps = ["s1"]
        workflow.current_step_id = "s2"
        workflow.started_at = datetime.now()
        workflow.completed_at = None
        workflow.context = {"logs": ["Log 1"], "error_message": None}

        result = _db_workflow_to_response(workflow)

        assert result.workflow_id == "workflow-123"
        assert result.progress_percent == 50
        assert result.steps_completed == 1
        assert result.steps_total == 2

    def test_db_workflow_to_response_empty_steps(self):
        """Test workflow response with no steps."""
        from backend.api.routes.workflows import _db_workflow_to_response
        from backend.models.workflow import WorkflowStatus

        workflow = MagicMock()
        workflow.id = "workflow-123"
        workflow.project_id = "project-123"
        workflow.status = WorkflowStatus.PENDING
        workflow.steps = []
        workflow.completed_steps = None
        workflow.current_step_id = None
        workflow.started_at = None
        workflow.completed_at = None
        workflow.context = None

        result = _db_workflow_to_response(workflow)

        assert result.progress_percent == 0
        assert result.steps_total == 0
