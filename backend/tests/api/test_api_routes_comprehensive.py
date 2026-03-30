"""
Comprehensive tests for API routes to increase coverage.

This module provides integration tests for FastAPI route handlers
covering project management, authentication, and core services.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.db.session import get_db

# Import main app
from backend.main import app


# Create test client
@pytest.fixture
def client():
    """Create test client with mocked dependencies."""
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)

    # Mock current user
    mock_user = MagicMock(user_id="user_123", username="testuser")

    def override_get_db():
        yield mock_db

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class TestProjectRoutes:
    """Tests for project management routes."""

    @pytest.mark.asyncio
    async def test_create_project_success(self, client):
        """Test creating a project successfully."""
        project_data = {
            "name": "Test Project",
            "description": "A test project",
            "requirements": "Python, FastAPI",
            "tech_stack": ["Python", "FastAPI"]
        }

        # Mock the service method
        with patch('backend.services.database_services.project_service') as mock_service:
            mock_project = AsyncMock()
            mock_project.id = "proj_123"
            mock_project.name = "Test Project"
            mock_project.status = "draft"
            mock_project.description = "A test project"
            mock_project.requirements = "Python, FastAPI"
            mock_project.tech_stack = ["Python", "FastAPI"]
            mock_project.current_phase = None
            mock_project.progress_percent = 0
            mock_project.created_at = datetime.now(UTC)
            mock_project.updated_at = datetime.now(UTC)
            mock_project.extra_metadata = {}

            # Create async context manager mock
            mock_service.__aenter__ = AsyncMock(return_value=mock_service)
            mock_service.__aexit__ = AsyncMock(return_value=None)
            mock_service.create_project = AsyncMock(return_value=mock_project)

            response = client.post("/api/projects", json=project_data)

            assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_get_projects_list(self, client):
        """Test getting list of projects."""
        with patch('backend.services.database_services.project_service') as mock_service:
            mock_project1 = MagicMock(id="p1", name="Project 1", status="active")
            mock_project2 = MagicMock(id="p2", name="Project 2", status="draft")

            mock_service.__aenter__ = AsyncMock(return_value=mock_service)
            mock_service.__aexit__ = AsyncMock(return_value=None)
            mock_service.get_all_projects = AsyncMock(return_value=[mock_project1, mock_project2])

            response = client.get("/api/projects")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_project_by_id(self, client):
        """Test getting specific project."""
        with patch('backend.services.database_services.project_service') as mock_service:
            mock_project = MagicMock(
                id="proj_123",
                name="Test Project",
                description="Test Desc",
                status="active"
            )

            mock_service.__aenter__ = AsyncMock(return_value=mock_service)
            mock_service.__aexit__ = AsyncMock(return_value=None)
            mock_service.get_project = AsyncMock(return_value=mock_project)

            response = client.get("/api/projects/proj_123")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client):
        """Test getting non-existent project."""
        with patch('backend.services.database_services.project_service') as mock_service:
            mock_service.__aenter__ = AsyncMock(return_value=mock_service)
            mock_service.__aexit__ = AsyncMock(return_value=None)
            mock_service.get_project = AsyncMock(return_value=None)

            response = client.get("/api/projects/nonexistent")

            assert response.status_code == 404


class TestAuthRoutes:
    """Tests for authentication routes."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, client):
        """Test user registration."""
        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!"
        }

        with patch('backend.services.auth_service.AuthService.register_user') as mock_register:
            mock_user = MagicMock(
                id="user_123",
                username="newuser",
                email="new@example.com"
            )
            mock_register.return_value = mock_user

            response = client.post("/api/auth/register", json=user_data)

            assert response.status_code == 201
            data = response.json()
            assert data["username"] == "newuser"

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Test successful login."""
        login_data = {
            "username": "testuser",
            "password": "correct_password"
        }

        with patch('backend.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = MagicMock(id="user_123", username="testuser")

            with patch('backend.services.auth_service.AuthService.create_access_token') as mock_token:
                mock_token.return_value = "fake_jwt_token"

                response = client.post("/api/auth/login", json=login_data)

                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data

    @pytest.mark.asyncio
    async def test_login_failure_wrong_password(self, client):
        """Test login with wrong password."""
        login_data = {
            "username": "testuser",
            "password": "wrong_password"
        }

        with patch('backend.services.auth_service.AuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = None

            response = client.post("/api/auth/login", json=login_data)

            assert response.status_code == 401


class TestWorkflowRoutes:
    """Tests for workflow management routes."""

    @pytest.mark.asyncio
    async def test_create_workflow(self, client):
        """Test creating a workflow."""
        workflow_data = {
            "name": "CI/CD Pipeline",
            "description": "Automated deployment",
            "trigger": "manual"
        }

        with patch('backend.services.database_services.DatabaseWorkflowService.create_workflow') as mock_create:
            mock_workflow = MagicMock(
                id="wf_123",
                name="CI/CD Pipeline",
                status="pending"
            )
            mock_create.return_value = mock_workflow

            response = client.post("/api/workflows", json=workflow_data)

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "wf_123"

    @pytest.mark.asyncio
    async def test_execute_workflow(self, client):
        """Test executing a workflow."""
        with patch('backend.services.database_services.DatabaseWorkflowService.execute_workflow') as mock_execute:
            mock_execute.return_value = {"status": "started", "execution_id": "exec_123"}

            response = client.post("/api/workflows/wf_123/execute")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"


class TestAgentRoutes:
    """Tests for agent management routes."""

    @pytest.mark.asyncio
    async def test_list_agents(self, client):
        """Test listing all agents."""
        with patch('backend.services.agent_service.AgentService.list_agents') as mock_list:
            mock_agents = [
                MagicMock(id="agent_1", role="developer", status="idle"),
                MagicMock(id="agent_2", role="reviewer", status="busy")
            ]
            mock_list.return_value = mock_agents

            response = client.get("/api/agents")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_assign_task_to_agent(self, client):
        """Test assigning task to agent."""
        assignment_data = {
            "task_id": "task_123",
            "priority": "high"
        }

        with patch('backend.services.agent_service.AgentService.assign_task') as mock_assign:
            mock_assign.return_value = True

            response = client.post("/api/agents/agent_1/assign", json=assignment_data)

            assert response.status_code == 200


class TestAnalyticsRoutes:
    """Tests for analytics routes."""

    @pytest.mark.asyncio
    async def test_get_project_analytics(self, client):
        """Test getting project analytics."""
        with patch('backend.services.analytics_engine.AnalyticsEngine.generate_report') as mock_report:
            mock_report.return_value = {
                "total_projects": 10,
                "active_projects": 5,
                "completion_rate": 0.75
            }

            response = client.get("/api/analytics/projects")

            assert response.status_code == 200
            data = response.json()
            assert "total_projects" in data

    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, client):
        """Test getting performance metrics."""
        with patch('backend.services.analytics_engine.AnalyticsEngine.execute_query') as mock_query:
            mock_query.return_value = {
                "avg_response_time": 150,
                "requests_per_second": 100
            }

            response = client.get("/api/analytics/performance")

            assert response.status_code == 200


class TestHealthRoutes:
    """Tests for health check routes."""

    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_ready_check(self, client):
        """Test readiness probe."""
        response = client.get("/ready")

        assert response.status_code in [200, 503]


class TestCustomizationRoutes:
    """Tests for customization routes."""

    @pytest.mark.asyncio
    async def test_list_themes(self, client):
        """Test listing available themes."""
        with patch('backend.services.customization_service.CustomizationService.list_themes') as mock_list:
            mock_themes = [
                MagicMock(id="theme1", name="Dark Mode"),
                MagicMock(id="theme2", name="Light Mode")
            ]
            mock_list.return_value = mock_themes

            response = client.get("/api/customization/themes")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_apply_theme(self, client):
        """Test applying a theme."""
        with patch('backend.services.customization_service.CustomizationService.apply_theme') as mock_apply:
            mock_apply.return_value = True

            response = client.post("/api/customization/themes/theme1/apply", json={"user_id": "user_123"})

            assert response.status_code == 200


class TestCollaborationRoutes:
    """Tests for collaboration routes."""

    @pytest.mark.asyncio
    async def test_add_comment(self, client):
        """Test adding a comment."""
        comment_data = {
            "content": "Great work!",
            "entity_type": "project",
            "entity_id": "proj_123"
        }

        with patch('backend.services.collaboration_service.CollaborationService.create_comment') as mock_create:
            mock_comment = MagicMock(id="comment_123", content="Great work!")
            mock_create.return_value = mock_comment

            response = client.post("/api/collaboration/comments", json=comment_data)

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "comment_123"

    @pytest.mark.asyncio
    async def test_get_notifications(self, client):
        """Test getting user notifications."""
        with patch('backend.services.collaboration_service.CollaborationService.get_user_notifications') as mock_get:
            mock_notifications = [
                MagicMock(id="notif_1", message="New comment"),
                MagicMock(id="notif_2", message="Task assigned")
            ]
            mock_get.return_value = mock_notifications

            response = client.get("/api/collaboration/notifications/user_123")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestPluginRoutes:
    """Tests for plugin routes."""

    @pytest.mark.asyncio
    async def test_list_plugins(self, client):
        """Test listing installed plugins."""
        with patch('backend.services.plugin_service.PluginManager.list_plugins') as mock_list:
            mock_plugins = [
                MagicMock(id="plugin1", name="Code Formatter", enabled=True),
                MagicMock(id="plugin2", name="Linter", enabled=False)
            ]
            mock_list.return_value = mock_plugins

            response = client.get("/api/plugins")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_enable_plugin(self, client):
        """Test enabling a plugin."""
        with patch('backend.services.plugin_service.PluginManager.enable_plugin') as mock_enable:
            mock_enable.return_value = True

            response = client.post("/api/plugins/plugin1/enable")

            assert response.status_code == 200


class TestSchemaRoutes:
    """Tests for schema management routes."""

    @pytest.mark.asyncio
    async def test_list_migrations(self, client):
        """Test listing migrations."""
        with patch('backend.services.schema_management_service.SchemaManagementService.list_migrations') as mock_list:
            mock_migrations = [
                MagicMock(id="mig_001", name="Initial schema", applied=True),
                MagicMock(id="mig_002", name="Add users table", applied=False)
            ]
            mock_list.return_value = mock_migrations

            response = client.get("/api/schema/migrations")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_apply_migration(self, client):
        """Test applying a migration."""
        with patch('backend.services.schema_management_service.SchemaManagementService.apply_migration') as mock_apply:
            mock_apply.return_value = True

            response = client.post("/api/schema/migrations/mig_002/apply")

            assert response.status_code == 200


class TestDeploymentRoutes:
    """Tests for deployment routes."""

    @pytest.mark.asyncio
    async def test_create_deployment(self, client):
        """Test creating a deployment."""
        deployment_data = {
            "project_id": "proj_123",
            "environment": "production",
            "version": "1.0.0"
        }

        with patch('backend.services.deployment_service.DeploymentService.create_deployment') as mock_create:
            mock_deployment = MagicMock(
                id="deploy_123",
                status="pending",
                environment="production"
            )
            mock_create.return_value = mock_deployment

            response = client.post("/api/deployments", json=deployment_data)

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "deploy_123"


class TestArchitectureRoutes:
    """Tests for architecture visualization routes."""

    @pytest.mark.asyncio
    async def test_create_diagram(self, client):
        """Test creating architecture diagram."""
        diagram_data = {
            "name": "System Architecture",
            "diagram_type": "component",
            "nodes": [{"id": "n1", "label": "API"}],
            "relationships": []
        }

        with patch('backend.services.architecture_service.ArchitectureVisualizationService.create_diagram') as mock_create:
            mock_diagram = MagicMock(
                id="diag_123",
                name="System Architecture",
                diagram_type="component"
            )
            mock_create.return_value = mock_diagram

            response = client.post("/api/architecture/diagrams", json=diagram_data)

            assert response.status_code == 201
            data = response.json()
            assert data["id"] == "diag_123"


class TestGitRoutes:
    """Tests for Git integration routes."""

    @pytest.mark.asyncio
    async def test_clone_repository(self, client):
        """Test cloning a repository."""
        clone_data = {
            "repo_url": "https://github.com/user/repo.git",
            "destination": "my-repo"
        }

        with patch('backend.services.git_service.GitService.clone_repository') as mock_clone:
            mock_clone.return_value = {
                "success": True,
                "message": "Repository cloned"
            }

            response = client.post("/api/git/clone", json=clone_data)

            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
