"""
Deployment API Routes.

This module provides REST endpoints for deployment management.
Uses DeploymentService for in-memory deployment tracking.
"""


from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.dependencies import get_current_user
from backend.api.models import DeploymentRequest, DeploymentResponse
from backend.core.logging import get_logger
from backend.deployment.orchestrator import DeploymentEnvironment
from backend.services.deployment_service import DeploymentService

logger = get_logger(__name__)
router = APIRouter(prefix="/deployments", tags=["deployments"])

# Deployment service instance
_service = DeploymentService()


def _to_response(d: dict) -> DeploymentResponse:
    """Convert a DeploymentService dict to DeploymentResponse."""
    return DeploymentResponse(
        deployment_id=d["deployment_id"],
        project_id=d["project_id"],
        environment=d["environment"],
        version=d["version"],
        status=d["status"],
        steps=d.get("steps", []),
        started_at=d.get("started_at"),
        completed_at=d.get("completed_at"),
        error_message=d.get("error_message"),
        url=d.get("url"),
    )


@router.post(
    "",
    response_model=DeploymentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create deployment",
)
async def create_deployment(
    request: DeploymentRequest,
    user=Depends(get_current_user),
) -> DeploymentResponse:
    """
    Create a new deployment for a project.

    The deployment will be queued and executed asynchronously.
    """
    # Validate environment via the enum
    try:
        DeploymentEnvironment(request.environment)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid environment: {request.environment}",
        ) from exc

    result = await _service.create_deployment(
        project_id=request.project_id,
        environment=request.environment,
        version=request.version,
        config=request.config or {},
    )

    logger.info(
        "Deployment created",
        deployment_id=result["deployment_id"],
        project_id=request.project_id,
        environment=request.environment,
        user=user.user_id if user else "anonymous",
    )

    return _to_response(result)


@router.get(
    "",
    response_model=list[DeploymentResponse],
    summary="List deployments",
)
async def list_deployments(
    project_id: str = None,
    environment: str = None,
    user=Depends(get_current_user),
) -> list[DeploymentResponse]:
    """
    List deployments with optional filtering.
    """
    deployments = await _service.list_deployments(
        project_id=project_id,
        environment=environment,
    )
    return [_to_response(d) for d in deployments]


@router.get(
    "/{deployment_id}",
    response_model=DeploymentResponse,
    summary="Get deployment status",
)
async def get_deployment(
    deployment_id: str,
    user=Depends(get_current_user),
) -> DeploymentResponse:
    """
    Get detailed information about a deployment.
    """
    deployment = await _service.get_deployment(deployment_id)

    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )

    return _to_response(deployment)


@router.post(
    "/{deployment_id}/cancel",
    response_model=DeploymentResponse,
    summary="Cancel deployment",
)
async def cancel_deployment(
    deployment_id: str,
    user=Depends(get_current_user),
) -> DeploymentResponse:
    """
    Cancel a pending or in-progress deployment.
    """
    success = await _service.cancel_deployment(deployment_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found or already in terminal state",
        )

    deployment = await _service.get_deployment(deployment_id)

    logger.info(
        "Deployment cancelled",
        deployment_id=deployment_id,
        user=user.user_id if user else "anonymous",
    )

    return _to_response(deployment)


@router.get(
    "/environments/available",
    response_model=list[str],
    summary="Get available environments",
)
async def get_available_environments(
    user=Depends(get_current_user),
) -> list[str]:
    """
    Get list of available deployment environments.
    """
    return [e.value for e in DeploymentEnvironment]
