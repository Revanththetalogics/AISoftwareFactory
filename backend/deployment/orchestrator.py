"""
Deployment Orchestrator for AI Software Factory.

This module provides deployment orchestration and management capabilities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class DeploymentStatus(StrEnum):
    """Deployment status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentEnvironment(StrEnum):
    """Deployment environments."""

    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"


@dataclass
class DeploymentStep:
    """
    Deployment step.

    Attributes:
        name: Step name
        status: Step status
        message: Step message
        started_at: Start timestamp
        completed_at: Completion timestamp
    """

    name: str
    status: DeploymentStatus = DeploymentStatus.PENDING
    message: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class DeploymentResult:
    """
    Deployment result.

    Attributes:
        deployment_id: Deployment identifier
        project_name: Project name
        environment: Target environment
        status: Overall status
        steps: Deployment steps
        started_at: Start timestamp
        completed_at: Completion timestamp
        metadata: Additional metadata
    """

    deployment_id: str
    project_name: str
    environment: DeploymentEnvironment
    status: DeploymentStatus = DeploymentStatus.PENDING
    steps: list[DeploymentStep] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """Get deployment duration in seconds."""
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    @property
    def success(self) -> bool:
        """Check if deployment was successful."""
        return self.status == DeploymentStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "deployment_id": self.deployment_id,
            "project_name": self.project_name,
            "environment": self.environment.value,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "metadata": self.metadata,
        }


class DeploymentOrchestrator:
    """
    Deployment orchestrator.

    This class provides:
    - Deployment planning and execution
    - Step-by-step deployment management
    - Rollback capabilities
    - Deployment history tracking

    Example:
        >>> orchestrator = DeploymentOrchestrator()
        >>> result = await orchestrator.deploy(
        ...     project_name="myproject",
        ...     environment=DeploymentEnvironment.STAGING
        ... )
    """

    def __init__(self):
        """Initialize the deployment orchestrator."""
        self._logger = get_logger(__name__)
        self._deployments: dict[str, DeploymentResult] = {}

    async def deploy(
        self,
        project_name: str,
        environment: DeploymentEnvironment,
        deployment_id: str | None = None,
    ) -> DeploymentResult:
        """
        Execute a deployment.

        Args:
            project_name: Project name
            environment: Target environment
            deployment_id: Optional deployment ID

        Returns:
            DeploymentResult
        """
        import uuid

        deployment_id = deployment_id or str(uuid.uuid4())[:8]

        result = DeploymentResult(
            deployment_id=deployment_id,
            project_name=project_name,
            environment=environment,
            status=DeploymentStatus.IN_PROGRESS,
        )

        self._deployments[deployment_id] = result

        self._logger.info(
            "Starting deployment",
            deployment_id=deployment_id,
            project=project_name,
            environment=environment.value,
        )

        try:
            # Build step
            build_step = DeploymentStep(name="Build")
            build_step.started_at = datetime.now()
            result.steps.append(build_step)

            # Simulate build
            await self._simulate_step("Building application")
            build_step.status = DeploymentStatus.SUCCESS
            build_step.completed_at = datetime.now()
            build_step.message = "Build completed successfully"

            # Test step
            test_step = DeploymentStep(name="Test")
            test_step.started_at = datetime.now()
            result.steps.append(test_step)

            # Simulate tests
            await self._simulate_step("Running tests")
            test_step.status = DeploymentStatus.SUCCESS
            test_step.completed_at = datetime.now()
            test_step.message = "All tests passed"

            # Infrastructure step
            infra_step = DeploymentStep(name="Infrastructure")
            infra_step.started_at = datetime.now()
            result.steps.append(infra_step)

            # Simulate infrastructure provisioning
            await self._simulate_step("Provisioning infrastructure")
            infra_step.status = DeploymentStatus.SUCCESS
            infra_step.completed_at = datetime.now()
            infra_step.message = "Infrastructure ready"

            # Deploy step
            deploy_step = DeploymentStep(name="Deploy")
            deploy_step.started_at = datetime.now()
            result.steps.append(deploy_step)

            # Simulate deployment
            await self._simulate_step("Deploying application")
            deploy_step.status = DeploymentStatus.SUCCESS
            deploy_step.completed_at = datetime.now()
            deploy_step.message = "Application deployed"

            # Verify step
            verify_step = DeploymentStep(name="Verify")
            verify_step.started_at = datetime.now()
            result.steps.append(verify_step)

            # Simulate verification
            await self._simulate_step("Verifying deployment")
            verify_step.status = DeploymentStatus.SUCCESS
            verify_step.completed_at = datetime.now()
            verify_step.message = "Deployment verified"

            # Mark overall success
            result.status = DeploymentStatus.SUCCESS
            result.completed_at = datetime.now()

            self._logger.info(
                "Deployment completed successfully",
                deployment_id=deployment_id,
                duration=result.duration_seconds,
            )

        except Exception as exc:
            result.status = DeploymentStatus.FAILED
            result.completed_at = datetime.now()

            # Mark current step as failed
            if result.steps:
                current_step = result.steps[-1]
                current_step.status = DeploymentStatus.FAILED
                current_step.message = str(exc)

            self._logger.error(
                "Deployment failed",
                deployment_id=deployment_id,
                error=str(exc),
            )

        return result

    async def _simulate_step(self, message: str, duration: float = 0.5) -> None:
        """
        Simulate a deployment step.

        Args:
            message: Step message
            duration: Step duration in seconds
        """
        import asyncio

        self._logger.info(f"Step: {message}")
        await asyncio.sleep(duration)

    async def rollback(
        self,
        deployment_id: str,
    ) -> DeploymentResult:
        """
        Rollback a deployment.

        Args:
            deployment_id: Deployment ID to rollback

        Returns:
            Rollback result
        """

        original = self._deployments.get(deployment_id)

        if not original:
            raise ValueError(f"Deployment {deployment_id} not found")

        rollback_id = f"rollback-{deployment_id}"

        result = DeploymentResult(
            deployment_id=rollback_id,
            project_name=original.project_name,
            environment=original.environment,
            status=DeploymentStatus.IN_PROGRESS,
            metadata={"original_deployment": deployment_id},
        )

        self._logger.info(
            "Starting rollback",
            rollback_id=rollback_id,
            original_deployment=deployment_id,
        )

        try:
            # Rollback step
            rollback_step = DeploymentStep(name="Rollback")
            rollback_step.started_at = datetime.now()
            result.steps.append(rollback_step)

            await self._simulate_step("Rolling back deployment")
            rollback_step.status = DeploymentStatus.SUCCESS
            rollback_step.completed_at = datetime.now()
            rollback_step.message = "Rollback completed"

            # Verify rollback
            verify_step = DeploymentStep(name="Verify Rollback")
            verify_step.started_at = datetime.now()
            result.steps.append(verify_step)

            await self._simulate_step("Verifying rollback")
            verify_step.status = DeploymentStatus.SUCCESS
            verify_step.completed_at = datetime.now()
            verify_step.message = "Rollback verified"

            result.status = DeploymentStatus.ROLLED_BACK
            result.completed_at = datetime.now()

            # Update original deployment status
            original.status = DeploymentStatus.ROLLED_BACK

            self._logger.info(
                "Rollback completed",
                rollback_id=rollback_id,
            )

        except Exception as exc:
            result.status = DeploymentStatus.FAILED
            result.completed_at = datetime.now()

            if result.steps:
                current_step = result.steps[-1]
                current_step.status = DeploymentStatus.FAILED
                current_step.message = str(exc)

            self._logger.error(
                "Rollback failed",
                rollback_id=rollback_id,
                error=str(exc),
            )

        return result

    def get_deployment(self, deployment_id: str) -> DeploymentResult | None:
        """
        Get a deployment by ID.

        Args:
            deployment_id: Deployment ID

        Returns:
            DeploymentResult or None
        """
        return self._deployments.get(deployment_id)

    def list_deployments(
        self,
        project_name: str | None = None,
        environment: DeploymentEnvironment | None = None,
    ) -> list[DeploymentResult]:
        """
        List deployments.

        Args:
            project_name: Filter by project
            environment: Filter by environment

        Returns:
            List of deployments
        """
        results = []

        for deployment in self._deployments.values():
            if project_name and deployment.project_name != project_name:
                continue
            if environment and deployment.environment != environment:
                continue
            results.append(deployment)

        # Sort by start time (newest first)
        results.sort(key=lambda d: d.started_at, reverse=True)

        return results
