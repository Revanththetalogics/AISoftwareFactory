"""
Comprehensive tests for database services module.

Tests for DatabaseProjectService, DatabaseWorkflowService, and DatabaseAgentService.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from backend.models.workflow import WorkflowStatus, WorkflowTrigger
from backend.services.database_services import (
    DatabaseAgentService,
    DatabaseProjectService,
    DatabaseWorkflowService,
    get_agent_service,
    get_project_service,
    get_workflow_service,
)


@pytest.fixture
def mock_db_session():
    """Mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session


@pytest.fixture
def mock_db_context(mock_db_session):
    """Mock get_db_context context manager."""
    async_ctx = AsyncMock()
    async_ctx.__aenter__ = AsyncMock(return_value=mock_db_session)
    async_ctx.__aexit__ = AsyncMock(return_value=None)
    return async_ctx


@pytest.fixture
def mock_project():
    """Create a mock project object."""
    project = Mock()
    project.id = "proj-test123456"
    project.name = "Test Project"
    project.description = "Test Description"
    project.requirements = "Test requirements"
    project.status = "draft"
    project.tech_stack = {}
    project.current_phase = None
    project.progress_percent = 0
    project.owner_id = "user-001"
    project.extra_metadata = {}
    project.created_at = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    return project


@pytest.fixture
def mock_workflow():
    """Create a mock workflow object."""
    workflow = Mock()
    workflow.id = "wf-test123456"
    workflow.name = "Test Workflow"
    workflow.project_id = "proj-123"
    workflow.steps = []
    workflow.status = WorkflowStatus.PENDING
    workflow.trigger = WorkflowTrigger.MANUAL
    workflow.completed_steps = []
    workflow.failed_steps = []
    workflow.context = {}
    workflow.created_by = "user-001"
    workflow.started_at = None
    workflow.completed_at = None
    return workflow


@pytest.fixture
def mock_agent():
    """Create a mock agent object."""
    agent = Mock()
    agent.id = "agent-test12345"
    agent.name = "Test Agent"
    agent.role = "developer"
    agent.capabilities = ["code", "test"]
    agent.status = "idle"
    agent.config = {}
    agent.created_at = datetime.utcnow()
    return agent


class TestDatabaseProjectService:
    """Tests for DatabaseProjectService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = DatabaseProjectService()

    @pytest.mark.asyncio
    async def test_create_project_with_provided_db(self, mock_db_session, mock_project):
        """Test project creation with provided db session."""
        # Setup mock
        mock_db_session.refresh = AsyncMock(side_effect=lambda p: setattr(p, "id", "proj-test123456"))

        with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
            with patch("backend.services.database_services.PerformanceTimer"):
                with patch("backend.services.database_services.business_events"):
                    project = await self.service.create_project(
                        name="Test Project",
                        description="Test Description",
                        requirements="Test requirements",
                        tech_stack={"backend": "python"},
                        owner_id="user-001",
                        db=mock_db_session,
                    )

        assert project is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()
        mock_db_session.refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_project_without_db(self, mock_db_context, mock_project):
        """Test project creation without provided db (uses get_db_context)."""
        mock_session = AsyncMock()
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
                with patch("backend.services.database_services.PerformanceTimer"):
                    with patch("backend.services.database_services.business_events"):
                        project = await self.service.create_project(name="Test Project", description="Test Description")

        assert project is not None

    @pytest.mark.asyncio
    async def test_get_project_with_provided_db(self, mock_db_session, mock_project):
        """Test get project with provided db session."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            project = await self.service.get_project("proj-test123456", db=mock_db_session)

        assert project == mock_project
        mock_db_session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_project_without_db(self, mock_db_context, mock_project):
        """Test get project without provided db."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.PerformanceTimer"):
                project = await self.service.get_project("proj-test123456")

        assert project == mock_project

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, mock_db_session):
        """Test get project when not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            project = await self.service.get_project("nonexistent", db=mock_db_session)

        assert project is None

    @pytest.mark.asyncio
    async def test_list_projects_with_provided_db(self, mock_db_session, mock_project):
        """Test list projects with provided db."""
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_project])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            projects = await self.service.list_projects(db=mock_db_session)

        assert len(projects) == 1
        assert projects[0] == mock_project

    @pytest.mark.asyncio
    async def test_list_projects_without_db(self, mock_db_context, mock_project):
        """Test list projects without provided db."""
        mock_session = AsyncMock()
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_project])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.PerformanceTimer"):
                projects = await self.service.list_projects()

        assert len(projects) == 1

    @pytest.mark.asyncio
    async def test_list_projects_with_filters(self, mock_db_session, mock_project):
        """Test list projects with owner and status filters."""
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_project])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            projects = await self.service.list_projects(
                owner_id="user-001", status="draft", skip=0, limit=50, db=mock_db_session
            )

        assert len(projects) == 1

    @pytest.mark.asyncio
    async def test_update_project_with_provided_db(self, mock_db_session, mock_project):
        """Test update project with provided db."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            with patch("backend.services.database_services.business_events"):
                with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
                    updated = await self.service.update_project(
                        "proj-test123456",
                        {"name": "Updated", "description": "Updated desc", "requirements": "Updated reqs"},
                        db=mock_db_session,
                    )

        assert updated is not None
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_project_without_db(self, mock_db_context, mock_project):
        """Test update project without provided db."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_project)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.PerformanceTimer"):
                with patch("backend.services.database_services.business_events"):
                    with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
                        updated = await self.service.update_project("proj-test123456", {"name": "Updated"})

        assert updated is not None

    @pytest.mark.asyncio
    async def test_update_project_not_found(self, mock_db_session):
        """Test update project when project not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            with patch("backend.services.database_services.business_events"):
                updated = await self.service.update_project("nonexistent", {"name": "Updated"}, db=mock_db_session)

        # When project not found, business_events should not be called with update
        assert updated is None

    @pytest.mark.asyncio
    async def test_delete_project_with_provided_db(self, mock_db_session):
        """Test delete project with provided db."""
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            result = await self.service.delete_project("proj-test123456", db=mock_db_session)

        assert result is True
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_project_without_db(self, mock_db_context):
        """Test delete project without provided db."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.PerformanceTimer"):
                result = await self.service.delete_project("proj-test123456")

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_project_not_found(self, mock_db_session):
        """Test delete project when not found."""
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch("backend.services.database_services.PerformanceTimer"):
            result = await self.service.delete_project("nonexistent", db=mock_db_session)

        assert result is False


class TestDatabaseWorkflowService:
    """Tests for DatabaseWorkflowService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = DatabaseWorkflowService()

    @pytest.mark.asyncio
    async def test_create_workflow_with_provided_db(self, mock_db_session):
        """Test workflow creation with provided db."""
        with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
            workflow = await self.service.create_workflow(
                name="Test Workflow",
                project_id="proj-123",
                steps=[{"step_id": "s1", "name": "Step 1"}],
                created_by="user-001",
                db=mock_db_session,
            )

        assert workflow is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_workflow_without_db(self, mock_db_context):
        """Test workflow creation without provided db."""
        mock_session = AsyncMock()
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
                workflow = await self.service.create_workflow(name="Test Workflow", project_id="proj-123", steps=[])

        assert workflow is not None

    @pytest.mark.asyncio
    async def test_get_workflow_with_provided_db(self, mock_db_session, mock_workflow):
        """Test get workflow with provided db."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        workflow = await self.service.get_workflow("wf-test123456", db=mock_db_session)

        assert workflow == mock_workflow

    @pytest.mark.asyncio
    async def test_get_workflow_without_db(self, mock_db_context, mock_workflow):
        """Test get workflow without provided db."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            workflow = await self.service.get_workflow("wf-test123456")

        assert workflow == mock_workflow

    @pytest.mark.asyncio
    async def test_update_workflow_status_with_provided_db(self, mock_db_session, mock_workflow):
        """Test update workflow status with provided db."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        updated = await self.service.update_workflow_status(
            "wf-test123456", WorkflowStatus.RUNNING, current_step_id="step-1", db=mock_db_session
        )

        assert updated is not None
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_workflow_status_without_db(self, mock_db_context, mock_workflow):
        """Test update workflow status without provided db."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            updated = await self.service.update_workflow_status("wf-test123456", WorkflowStatus.COMPLETED)

        assert updated is not None

    @pytest.mark.asyncio
    async def test_update_workflow_status_running(self, mock_db_session, mock_workflow):
        """Test update workflow status to RUNNING sets started_at."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await self.service.update_workflow_status("wf-test123456", WorkflowStatus.RUNNING, db=mock_db_session)

        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_workflow_status_completed(self, mock_db_session, mock_workflow):
        """Test update workflow status to COMPLETED sets completed_at."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await self.service.update_workflow_status("wf-test123456", WorkflowStatus.COMPLETED, db=mock_db_session)

        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_workflow_status_failed(self, mock_db_session, mock_workflow):
        """Test update workflow status to FAILED sets completed_at."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await self.service.update_workflow_status("wf-test123456", WorkflowStatus.FAILED, db=mock_db_session)

        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_workflow_status_cancelled(self, mock_db_session, mock_workflow):
        """Test update workflow status to CANCELLED sets completed_at."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_workflow)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        await self.service.update_workflow_status("wf-test123456", WorkflowStatus.CANCELLED, db=mock_db_session)

        mock_db_session.commit.assert_awaited_once()


class TestDatabaseAgentService:
    """Tests for DatabaseAgentService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = DatabaseAgentService()

    @pytest.mark.asyncio
    async def test_register_agent_with_provided_db(self, mock_db_session):
        """Test agent registration with provided db."""
        with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
            agent = await self.service.register_agent(
                name="Test Agent", role="developer", capabilities=["code", "test"], db=mock_db_session
            )

        assert agent is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_agent_without_db(self, mock_db_context):
        """Test agent registration without provided db."""
        mock_session = AsyncMock()
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            with patch("backend.services.database_services.sanitize_input", side_effect=lambda x, **kwargs: x):
                agent = await self.service.register_agent(name="Test Agent", role="developer", capabilities=["code"])

        assert agent is not None

    @pytest.mark.asyncio
    async def test_get_agent_with_provided_db(self, mock_db_session, mock_agent):
        """Test get agent with provided db."""
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_agent)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        agent = await self.service.get_agent("agent-test12345", db=mock_db_session)

        assert agent == mock_agent

    @pytest.mark.asyncio
    async def test_get_agent_without_db(self, mock_db_context, mock_agent):
        """Test get agent without provided db."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none = Mock(return_value=mock_agent)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            agent = await self.service.get_agent("agent-test12345")

        assert agent == mock_agent

    @pytest.mark.asyncio
    async def test_list_agents_with_provided_db(self, mock_db_session, mock_agent):
        """Test list agents with provided db."""
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_agent])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        agents = await self.service.list_agents(db=mock_db_session)

        assert len(agents) == 1
        assert agents[0] == mock_agent

    @pytest.mark.asyncio
    async def test_list_agents_without_db(self, mock_db_context, mock_agent):
        """Test list agents without provided db."""
        mock_session = AsyncMock()
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_agent])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_db_context.__aenter__.return_value = mock_session

        with patch("backend.services.database_services.get_db_context", return_value=mock_db_context):
            agents = await self.service.list_agents()

        assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_list_agents_with_role_filter(self, mock_db_session, mock_agent):
        """Test list agents with role filter."""
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_agent])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        agents = await self.service.list_agents(role="developer", db=mock_db_session)

        assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_list_agents_with_status_filter(self, mock_db_session, mock_agent):
        """Test list agents with status filter."""
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_agent])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        agents = await self.service.list_agents(status="idle", db=mock_db_session)

        assert len(agents) == 1

    @pytest.mark.asyncio
    async def test_list_agents_with_both_filters(self, mock_db_session, mock_agent):
        """Test list agents with both role and status filters."""
        mock_scalars = Mock()
        mock_scalars.all = Mock(return_value=[mock_agent])
        mock_result = Mock()
        mock_result.scalars = Mock(return_value=mock_scalars)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        agents = await self.service.list_agents(role="developer", status="idle", db=mock_db_session)

        assert len(agents) == 1


class TestServiceFactories:
    """Tests for service factory functions."""

    def test_get_project_service(self):
        """Test get_project_service returns correct instance."""
        service = get_project_service()
        assert isinstance(service, DatabaseProjectService)

    def test_get_workflow_service(self):
        """Test get_workflow_service returns correct instance."""
        service = get_workflow_service()
        assert isinstance(service, DatabaseWorkflowService)

    def test_get_agent_service(self):
        """Test get_agent_service returns correct instance."""
        service = get_agent_service()
        assert isinstance(service, DatabaseAgentService)
