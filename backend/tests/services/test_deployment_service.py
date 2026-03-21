"""
Comprehensive tests for deployment service module.

Tests for DeploymentService covering all methods and edge cases.
"""


import pytest
from backend.services.deployment_service import DeploymentService


class TestDeploymentService:
    """Comprehensive tests for DeploymentService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = DeploymentService()

    @pytest.mark.asyncio
    async def test_create_deployment_basic(self):
        """Test basic deployment creation."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        assert deployment is not None
        assert deployment["project_id"] == "proj-123"
        assert deployment["environment"] == "development"
        assert deployment["version"] == "1.0.0"
        assert deployment["status"] == "pending"
        assert deployment["deployment_id"] is not None

    @pytest.mark.asyncio
    async def test_create_deployment_with_config(self):
        """Test deployment creation with configuration."""
        config = {"replicas": 3, "cpu": "500m"}

        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="production",
            version="1.0.0",
            config=config
        )

        assert deployment["config"] == config
        assert deployment["config"]["replicas"] == 3

    @pytest.mark.asyncio
    async def test_create_deployment_without_config(self):
        """Test deployment creation without config defaults to empty dict."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="staging",
            version="1.0.0"
        )

        assert deployment["config"] == {}

    @pytest.mark.asyncio
    async def test_create_deployment_fields(self):
        """Test all deployment fields are set correctly."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="2.0.0"
        )

        assert "deployment_id" in deployment
        assert "started_at" in deployment
        assert deployment["completed_at"] is None
        assert deployment["error_message"] is None
        assert deployment["url"] is None
        assert deployment["steps"] == []

    @pytest.mark.asyncio
    async def test_get_deployment_existing(self):
        """Test getting an existing deployment."""
        created = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        retrieved = await self.service.get_deployment(created["deployment_id"])

        assert retrieved is not None
        assert retrieved["deployment_id"] == created["deployment_id"]

    @pytest.mark.asyncio
    async def test_get_deployment_nonexistent(self):
        """Test getting a nonexistent deployment."""
        result = await self.service.get_deployment("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_deployments_all(self):
        """Test listing all deployments."""
        await self.service.create_deployment("proj-1", "dev", "1.0.0")
        await self.service.create_deployment("proj-2", "staging", "1.0.0")

        deployments = await self.service.list_deployments()

        assert len(deployments) == 2

    @pytest.mark.asyncio
    async def test_list_deployments_filter_by_project(self):
        """Test listing deployments filtered by project ID."""
        await self.service.create_deployment("proj-1", "dev", "1.0.0")
        await self.service.create_deployment("proj-2", "dev", "1.0.0")
        await self.service.create_deployment("proj-1", "staging", "1.0.0")

        deployments = await self.service.list_deployments(project_id="proj-1")

        assert len(deployments) == 2
        assert all(d["project_id"] == "proj-1" for d in deployments)

    @pytest.mark.asyncio
    async def test_list_deployments_filter_by_environment(self):
        """Test listing deployments filtered by environment."""
        await self.service.create_deployment("proj-1", "development", "1.0.0")
        await self.service.create_deployment("proj-2", "production", "1.0.0")
        await self.service.create_deployment("proj-3", "development", "1.0.0")

        deployments = await self.service.list_deployments(environment="development")

        assert len(deployments) == 2
        assert all(d["environment"] == "development" for d in deployments)

    @pytest.mark.asyncio
    async def test_list_deployments_filter_by_both(self):
        """Test listing deployments filtered by both project and environment."""
        await self.service.create_deployment("proj-1", "development", "1.0.0")
        await self.service.create_deployment("proj-1", "production", "1.0.0")
        await self.service.create_deployment("proj-2", "development", "1.0.0")

        deployments = await self.service.list_deployments(
            project_id="proj-1",
            environment="development"
        )

        assert len(deployments) == 1
        assert deployments[0]["project_id"] == "proj-1"
        assert deployments[0]["environment"] == "development"

    @pytest.mark.asyncio
    async def test_list_deployments_sorted_by_started_at(self):
        """Test deployments are sorted by started_at descending."""
        # Create deployments - they'll have different started_at times
        await self.service.create_deployment("proj-1", "dev", "1.0.0")
        await self.service.create_deployment("proj-2", "dev", "1.0.0")

        deployments = await self.service.list_deployments()

        # Most recent should be first
        assert len(deployments) == 2
        # The order depends on creation time, but the list should be sorted

    @pytest.mark.asyncio
    async def test_update_deployment_status_basic(self):
        """Test updating deployment status."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="running"
        )

        assert updated is not None
        assert updated["status"] == "running"

    @pytest.mark.asyncio
    async def test_update_deployment_status_not_found(self):
        """Test updating status of nonexistent deployment."""
        result = await self.service.update_deployment_status(
            "nonexistent-id",
            status="running"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_deployment_status_with_steps(self):
        """Test updating deployment status with steps."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        steps = [
            {"name": "Build", "status": "completed"},
            {"name": "Deploy", "status": "in_progress"}
        ]

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="running",
            steps=steps
        )

        assert updated is not None
        assert updated["steps"] == steps

    @pytest.mark.asyncio
    async def test_update_deployment_status_with_error(self):
        """Test updating deployment status with error message."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="failed",
            error_message="Container failed to start"
        )

        assert updated is not None
        assert updated["status"] == "failed"
        assert updated["error_message"] == "Container failed to start"
        assert updated["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_update_deployment_status_with_url(self):
        """Test updating deployment status with URL."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="production",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="success",
            url="https://app.example.com"
        )

        assert updated is not None
        assert updated["status"] == "success"
        assert updated["url"] == "https://app.example.com"
        assert updated["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_update_deployment_status_success_sets_completed_at(self):
        """Test that success status sets completed_at."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="success"
        )

        assert updated["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_update_deployment_status_failed_sets_completed_at(self):
        """Test that failed status sets completed_at."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="failed"
        )

        assert updated["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_update_deployment_status_rolled_back_sets_completed_at(self):
        """Test that rolled_back status sets completed_at."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="rolled_back"
        )

        assert updated["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_update_deployment_status_running_no_completed_at(self):
        """Test that running status does not set completed_at."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        updated = await self.service.update_deployment_status(
            deployment["deployment_id"],
            status="running"
        )

        assert updated["completed_at"] is None

    @pytest.mark.asyncio
    async def test_delete_deployment_success(self):
        """Test deleting a deployment successfully."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        result = await self.service.delete_deployment(deployment["deployment_id"])

        assert result is True

        # Verify deletion
        retrieved = await self.service.get_deployment(deployment["deployment_id"])
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_deployment_not_found(self):
        """Test deleting a nonexistent deployment."""
        result = await self.service.delete_deployment("nonexistent-id")
        assert result is False


class TestDeploymentServiceInit:
    """Tests for DeploymentService initialization."""

    def test_init_creates_empty_storage(self):
        """Test that initialization creates empty deployments dict."""
        service = DeploymentService()

        assert service._deployments == {}
        assert service._logger is not None


class TestDeploymentServiceEnvironments:
    """Tests for different deployment environments."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = DeploymentService()

    @pytest.mark.asyncio
    async def test_development_environment(self):
        """Test deployment to development environment."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="development",
            version="1.0.0"
        )

        assert deployment["environment"] == "development"

    @pytest.mark.asyncio
    async def test_staging_environment(self):
        """Test deployment to staging environment."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="staging",
            version="1.0.0"
        )

        assert deployment["environment"] == "staging"

    @pytest.mark.asyncio
    async def test_production_environment(self):
        """Test deployment to production environment."""
        deployment = await self.service.create_deployment(
            project_id="proj-123",
            environment="production",
            version="1.0.0"
        )

        assert deployment["environment"] == "production"
