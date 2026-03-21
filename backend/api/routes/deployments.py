"""
Deployment API Routes.

This module provides REST endpoints for deployment management.

TODO: Wire to DatabaseDeploymentService once implemented in database_services.py.
Currently using DeploymentOrchestrator which uses in-memory storage.
"""

from typing import List
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, status

from backend.api.models import DeploymentRequest, DeploymentResponse
from backend.api.dependencies import get_current_user, require_permissions
from backend.deployment.orchestrator import DeploymentOrchestrator, DeploymentEnvironment
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/deployments", tags=["deployments"])

# Deployment orchestrator instance
_orchestrator = DeploymentOrchestrator()


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
    try:
        env = DeploymentEnvironment(request.environment)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid environment: {request.environment}",
        )
    
    result = _orchestrator.create_deployment(
        project_id=request.project_id,
        environment=env,
        version=request.version,
        config=request.config or {},
    )
    
    logger.info(
        "Deployment created",
        deployment_id=result.deployment_id,
        project_id=request.project_id,
        environment=request.environment,
        user=user.user_id if user else "anonymous",
    )
    
    return DeploymentResponse(
        deployment_id=result.deployment_id,
        project_id=result.project_name,
        environment=result.environment.value,
        version=request.version,
        status=result.status.value,
        steps=[step.to_dict() for step in result.steps],
        started_at=result.started_at,
        completed_at=result.completed_at,
        error_message=None,
        url=None,
    )


@router.get(
    "",
    response_model=List[DeploymentResponse],
    summary="List deployments",
)
async def list_deployments(
    project_id: str = None,
    environment: str = None,
    user=Depends(get_current_user),
) -> List[DeploymentResponse]:
    """
    List deployments with optional filtering.
    """
    env = None
    if environment:
        try:
            env = DeploymentEnvironment(environment)
        except ValueError:
            pass
    
    deployments = _orchestrator.list_deployments(
        project_name=project_id,
        environment=env,
    )
    
    return [
        DeploymentResponse(
            deployment_id=d.deployment_id,
            project_id=d.project_name,
            environment=d.environment.value,
            version="unknown",
            status=d.status.value,
            steps=[step.to_dict() for step in d.steps],
            started_at=d.started_at,
            completed_at=d.completed_at,
            error_message=None,
            url=None,
        )
        for d in deployments
    ]


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
    deployment = _orchestrator.get_deployment(deployment_id)
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    return DeploymentResponse(
        deployment_id=deployment.deployment_id,
        project_id=deployment.project_name,
        environment=deployment.environment.value,
        version="unknown",
        status=deployment.status.value,
        steps=[step.to_dict() for step in deployment.steps],
        started_at=deployment.started_at,
        completed_at=deployment.completed_at,
        error_message=None,
        url=None,
    )


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
    success = _orchestrator.cancel_deployment(deployment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deployment {deployment_id} not found",
        )
    
    deployment = _orchestrator.get_deployment(deployment_id)
    
    logger.info(
        "Deployment cancelled",
        deployment_id=deployment_id,
        user=user.user_id if user else "anonymous",
    )
    
    return DeploymentResponse(
        deployment_id=deployment.deployment_id,
        project_id=deployment.project_name,
        environment=deployment.environment.value,
        version="unknown",
        status=deployment.status.value,
        steps=[step.to_dict() for step in deployment.steps],
        started_at=deployment.started_at,
        completed_at=deployment.completed_at,
        error_message=None,
        url=None,
    )


@router.get(
    "/environments/available",
    response_model=List[str],
    summary="Get available environments",
)
async def get_available_environments(
    user=Depends(get_current_user),
) -> List[str]:
    """
    Get list of available deployment environments.
    """
    return [e.value for e in DeploymentEnvironment]
