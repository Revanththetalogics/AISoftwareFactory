"""
Deployment service for AI Software Factory.

This module provides business logic for deployment management operations.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


class DeploymentService:
    """
    Service for managing deployments.

    This service handles deployment lifecycle, environment management,
    and integration with deployment engines.
    """

    def __init__(self):
        """Initialize the deployment service."""
        self._deployments: dict[str, dict[str, Any]] = {}
        self._logger = get_logger(__name__)

    async def create_deployment(
        self,
        project_id: str,
        environment: str,
        version: str,
        config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create a new deployment.

        Args:
            project_id: Project ID
            environment: Target environment (dev, staging, production)
            version: Deployment version
            config: Deployment configuration

        Returns:
            Created deployment data
        """
        deployment_id = str(uuid4())
        deployment = {
            "deployment_id": deployment_id,
            "project_id": project_id,
            "environment": environment,
            "version": version,
            "status": "pending",
            "steps": [],
            "started_at": datetime.now(UTC).isoformat(),
            "completed_at": None,
            "error_message": None,
            "url": None,
            "config": config or {}
        }

        self._deployments[deployment_id] = deployment
        self._logger.info(
            "Deployment created",
            deployment_id=deployment_id,
            project_id=project_id,
            environment=environment
        )

        return deployment

    async def get_deployment(self, deployment_id: str) -> dict[str, Any] | None:
        """
        Get a deployment by ID.

        Args:
            deployment_id: Deployment ID

        Returns:
            Deployment data or None if not found
        """
        return self._deployments.get(deployment_id)

    async def list_deployments(
        self,
        project_id: str | None = None,
        environment: str | None = None
    ) -> list[dict[str, Any]]:
        """
        List deployments with optional filtering.

        Args:
            project_id: Filter by project ID
            environment: Filter by environment

        Returns:
            List of deployment data
        """
        deployments = list(self._deployments.values())

        if project_id:
            deployments = [d for d in deployments if d["project_id"] == project_id]
        if environment:
            deployments = [d for d in deployments if d["environment"] == environment]

        return sorted(deployments, key=lambda d: d["started_at"], reverse=True)

    async def update_deployment_status(
        self,
        deployment_id: str,
        status: str,
        steps: list[dict[str, Any]] | None = None,
        error_message: str | None = None,
        url: str | None = None
    ) -> dict[str, Any] | None:
        """
        Update deployment status.

        Args:
            deployment_id: Deployment ID
            status: New status
            steps: Deployment steps
            error_message: Error message if failed
            url: Deployment URL

        Returns:
            Updated deployment data or None if not found
        """
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return None

        deployment["status"] = status
        if steps:
            deployment["steps"] = steps
        if error_message:
            deployment["error_message"] = error_message
        if url:
            deployment["url"] = url

        if status in ["success", "failed", "rolled_back"]:
            deployment["completed_at"] = datetime.now(UTC).isoformat()

        self._logger.info(
            "Deployment status updated",
            deployment_id=deployment_id,
            status=status
        )

        return deployment

    async def delete_deployment(self, deployment_id: str) -> bool:
        """
        Delete a deployment.

        Args:
            deployment_id: Deployment ID

        Returns:
            True if deleted, False if not found
        """
        if deployment_id in self._deployments:
            del self._deployments[deployment_id]
            self._logger.info("Deployment deleted", deployment_id=deployment_id)
            return True
        return False

    async def cancel_deployment(self, deployment_id: str) -> bool:
        """
        Cancel a pending or in-progress deployment.

        Args:
            deployment_id: Deployment ID

        Returns:
            True if cancelled, False if not found
        """
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False

        if deployment["status"] in ("success", "failed", "rolled_back", "cancelled"):
            return False

        deployment["status"] = "cancelled"
        deployment["completed_at"] = datetime.now(UTC).isoformat()
        self._logger.info("Deployment cancelled", deployment_id=deployment_id)
        return True
