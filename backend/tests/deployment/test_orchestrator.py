"""
Tests for Deployment Orchestrator.
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from backend.deployment.orchestrator import (
    DeploymentEnvironment,
    DeploymentOrchestrator,
    DeploymentResult,
    DeploymentStatus,
    DeploymentStep,
)


class TestDeploymentStep:
    """Test cases for DeploymentStep."""

    def test_step_creation(self):
        """Test creating a step."""
        step = DeploymentStep(
            name="Build",
            status=DeploymentStatus.PENDING,
        )

        assert step.name == "Build"
        assert step.status == DeploymentStatus.PENDING

    def test_step_to_dict(self):
        """Test converting step to dict."""
        step = DeploymentStep(
            name="Deploy",
            status=DeploymentStatus.SUCCESS,
            message="Deployed successfully",
        )

        data = step.to_dict()

        assert data["name"] == "Deploy"
        assert data["status"] == "success"


class TestDeploymentResult:
    """Test cases for DeploymentResult."""

    def test_result_creation(self):
        """Test creating result."""
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.SUCCESS,
        )

        assert result.deployment_id == "dep-123"
        assert result.project_name == "myproject"
        assert result.environment == DeploymentEnvironment.PRODUCTION

    def test_result_with_steps(self):
        """Test result with steps."""
        steps = [
            DeploymentStep(name="Build", status=DeploymentStatus.SUCCESS),
            DeploymentStep(name="Test", status=DeploymentStatus.SUCCESS),
        ]
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.STAGING,
            steps=steps,
        )

        assert len(result.steps) == 2


class TestDeploymentOrchestrator:
    """Test cases for DeploymentOrchestrator."""

    def setup_method(self):
        """Create fresh orchestrator for each test."""
        self.orchestrator = DeploymentOrchestrator()

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator is not None

    def test_get_deployment_nonexistent(self):
        """Test getting nonexistent deployment."""
        deployment = self.orchestrator.get_deployment("nonexistent-id")

        assert deployment is None

    def test_list_deployments_empty(self):
        """Test listing deployments when empty."""
        deployments = self.orchestrator.list_deployments()

        assert len(deployments) == 0


class TestDeploymentResultProperties:
    """Test cases for DeploymentResult properties."""

    def test_duration_seconds_without_completed_at(self):
        """Test duration_seconds when deployment is ongoing (lines 89-90)."""
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.STAGING,
            status=DeploymentStatus.IN_PROGRESS,
            started_at=datetime.now(),
            completed_at=None,
        )

        duration = result.duration_seconds
        assert duration >= 0

    def test_duration_seconds_with_completed_at(self):
        """Test duration_seconds when deployment is completed."""
        started = datetime(2024, 1, 1, 10, 0, 0)
        completed = datetime(2024, 1, 1, 10, 0, 30)
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.STAGING,
            started_at=started,
            completed_at=completed,
        )

        duration = result.duration_seconds
        assert duration == 30.0

    def test_success_property_true(self):
        """Test success property when status is SUCCESS (line 95)."""
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.SUCCESS,
        )

        assert result.success is True

    def test_success_property_false(self):
        """Test success property when status is not SUCCESS."""
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.FAILED,
        )

        assert result.success is False

    def test_to_dict(self):
        """Test to_dict method (line 99)."""
        started = datetime(2024, 1, 1, 10, 0, 0)
        completed = datetime(2024, 1, 1, 10, 0, 30)
        steps = [
            DeploymentStep(
                name="Build",
                status=DeploymentStatus.SUCCESS,
                message="Done",
                started_at=started,
                completed_at=completed,
            )
        ]
        result = DeploymentResult(
            deployment_id="dep-123",
            project_name="myproject",
            environment=DeploymentEnvironment.PRODUCTION,
            status=DeploymentStatus.SUCCESS,
            steps=steps,
            started_at=started,
            completed_at=completed,
            metadata={"key": "value"},
        )

        data = result.to_dict()

        assert data["deployment_id"] == "dep-123"
        assert data["project_name"] == "myproject"
        assert data["environment"] == "prod"
        assert data["status"] == "success"
        assert len(data["steps"]) == 1
        assert data["started_at"] == started.isoformat()
        assert data["completed_at"] == completed.isoformat()
        assert data["duration_seconds"] == 30.0
        assert data["success"] is True
        assert data["metadata"] == {"key": "value"}


class TestDeploymentOrchestratorAsync:
    """Async test cases for DeploymentOrchestrator."""

    def setup_method(self):
        """Create fresh orchestrator for each test."""
        self.orchestrator = DeploymentOrchestrator()

    @pytest.mark.asyncio
    async def test_deploy_success(self):
        """Test successful deployment (lines 153-255)."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock) as mock_simulate:
            result = await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.STAGING,
                deployment_id="test-dep-123",
            )

            assert result.deployment_id == "test-dep-123"
            assert result.project_name == "myproject"
            assert result.environment == DeploymentEnvironment.STAGING
            assert result.status == DeploymentStatus.SUCCESS
            assert len(result.steps) == 5  # Build, Test, Infrastructure, Deploy, Verify
            assert result.completed_at is not None

            # All steps should be successful
            for step in result.steps:
                assert step.status == DeploymentStatus.SUCCESS

            # Should call simulate_step 5 times
            assert mock_simulate.call_count == 5

    @pytest.mark.asyncio
    async def test_deploy_auto_generates_id(self):
        """Test deploy auto-generates deployment_id if not provided."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock):
            result = await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.DEVELOPMENT,
            )

            assert result.deployment_id is not None
            assert len(result.deployment_id) == 8  # UUID[:8]

    @pytest.mark.asyncio
    async def test_deploy_failure_marks_step_failed(self):
        """Test deploy failure marks current step as failed (lines 239-254)."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock) as mock_simulate:
            # Fail on the 3rd call (Infrastructure step)
            mock_simulate.side_effect = [None, None, Exception("Infra error"), None, None]

            result = await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.PRODUCTION,
            )

            assert result.status == DeploymentStatus.FAILED
            assert result.completed_at is not None
            # The last step (Infrastructure) should be failed
            last_step = result.steps[-1]
            assert last_step.status == DeploymentStatus.FAILED
            assert "Infra error" in last_step.message

    @pytest.mark.asyncio
    async def test_simulate_step(self):
        """Test _simulate_step method (lines 265-268)."""
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            await self.orchestrator._simulate_step("Test message", duration=0.1)
            mock_sleep.assert_called_once_with(0.1)

    @pytest.mark.asyncio
    async def test_rollback_success(self):
        """Test successful rollback (lines 284-352)."""
        # First, create a deployment
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock):
            deploy_result = await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.STAGING,
                deployment_id="orig-dep-123",
            )
            assert deploy_result.status == DeploymentStatus.SUCCESS

            # Now rollback
            rollback_result = await self.orchestrator.rollback(deployment_id="orig-dep-123")

            assert rollback_result.deployment_id == "rollback-orig-dep-123"
            assert rollback_result.project_name == "myproject"
            assert rollback_result.environment == DeploymentEnvironment.STAGING
            assert rollback_result.status == DeploymentStatus.ROLLED_BACK
            assert rollback_result.metadata["original_deployment"] == "orig-dep-123"
            assert len(rollback_result.steps) == 2  # Rollback, Verify Rollback

            # Original deployment should also be marked as rolled back
            original = self.orchestrator.get_deployment("orig-dep-123")
            assert original.status == DeploymentStatus.ROLLED_BACK

    @pytest.mark.asyncio
    async def test_rollback_deployment_not_found(self):
        """Test rollback raises error for nonexistent deployment."""
        with pytest.raises(ValueError) as exc_info:
            await self.orchestrator.rollback(deployment_id="nonexistent")

        assert "Deployment nonexistent not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rollback_failure(self):
        """Test rollback failure handling (lines 337-350)."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock) as mock_simulate:
            # Create deployment first
            await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.STAGING,
                deployment_id="orig-dep-456",
            )

            # Make rollback fail
            mock_simulate.side_effect = Exception("Rollback error")

            rollback_result = await self.orchestrator.rollback(deployment_id="orig-dep-456")

            assert rollback_result.status == DeploymentStatus.FAILED
            assert rollback_result.completed_at is not None
            # Last step should be failed
            if rollback_result.steps:
                last_step = rollback_result.steps[-1]
                assert last_step.status == DeploymentStatus.FAILED
                assert "Rollback error" in last_step.message

    @pytest.mark.asyncio
    async def test_list_deployments_with_project_filter(self):
        """Test list_deployments with project_name filter (lines 384-388)."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock):
            await self.orchestrator.deploy(
                project_name="project_a",
                environment=DeploymentEnvironment.DEVELOPMENT,
            )
            await self.orchestrator.deploy(
                project_name="project_b",
                environment=DeploymentEnvironment.DEVELOPMENT,
            )

            # Filter by project_a
            results = self.orchestrator.list_deployments(project_name="project_a")

            assert len(results) == 1
            assert results[0].project_name == "project_a"

    @pytest.mark.asyncio
    async def test_list_deployments_with_environment_filter(self):
        """Test list_deployments with environment filter."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock):
            await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.DEVELOPMENT,
            )
            await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.PRODUCTION,
            )

            # Filter by production
            results = self.orchestrator.list_deployments(environment=DeploymentEnvironment.PRODUCTION)

            assert len(results) == 1
            assert results[0].environment == DeploymentEnvironment.PRODUCTION

    @pytest.mark.asyncio
    async def test_list_deployments_sorted_by_start_time(self):
        """Test list_deployments returns results sorted by start time (newest first)."""
        with patch.object(self.orchestrator, "_simulate_step", new_callable=AsyncMock):
            await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.DEVELOPMENT,
                deployment_id="dep-1",
            )
            await self.orchestrator.deploy(
                project_name="myproject",
                environment=DeploymentEnvironment.STAGING,
                deployment_id="dep-2",
            )

            results = self.orchestrator.list_deployments()

            # Newest first
            assert results[0].deployment_id == "dep-2"
            assert results[1].deployment_id == "dep-1"
