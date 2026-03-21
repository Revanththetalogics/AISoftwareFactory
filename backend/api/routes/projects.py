"""
Project Management API Routes.

This module provides REST endpoints for project CRUD operations.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.api.models import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdate,
)
from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.services.database_services import get_project_service

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])

# Get service instance
project_service = get_project_service()


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    request: ProjectCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    Create a new software factory project.

    The project will be initialized in DRAFT status and can then be
    activated to start the AI-driven development workflow.
    """
    project = await project_service.create_project(
        name=request.name,
        description=request.description,
        requirements=request.requirements,
        tech_stack=request.tech_stack,
        owner_id=user.user_id if user else "anonymous",
        db=db
    )

    logger.info(
        "Project created",
        project_id=project.id,
        name=request.name,
        user=user.user_id if user else "anonymous",
    )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        requirements=project.requirements,
        status=ProjectStatus(project.status),
        tech_stack=project.tech_stack,
        current_phase=project.current_phase,
        progress_percent=project.progress_percent,
        created_at=project.created_at,
        updated_at=project.updated_at,
        metadata=project.extra_metadata
    )


@router.get(
    "",
    response_model=List[ProjectResponse],
    summary="List all projects",
)
async def list_projects(
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProjectResponse]:
    """
    List all projects with optional filtering.

    Supports pagination and status filtering.
    """
    projects = await project_service.list_projects(
        owner_id=user.user_id if user else None,
        status=status.value if status else None,
        skip=skip,
        limit=limit,
        db=db
    )

    logger.info(
        "Projects listed",
        count=len(projects),
        filter_status=status,
        user=user.user_id if user else "anonymous",
    )

    return [
        ProjectResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            requirements=p.requirements,
            status=ProjectStatus(p.status),
            tech_stack=p.tech_stack,
            current_phase=p.current_phase,
            progress_percent=p.progress_percent,
            created_at=p.created_at,
            updated_at=p.updated_at,
            metadata=p.metadata
        )
        for p in projects
    ]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
async def get_project(
    project_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    Get detailed information about a specific project.
    """
    project = await project_service.get_project(project_id, db=db)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Check ownership/permissions
    # Allow access if user owns the project or has admin permissions
    user_id = user.user_id if user else "anonymous"
    is_owner = project.owner_id == user_id
    is_admin = hasattr(user, 'permissions') and "admin" in user.permissions

    if not is_owner and not is_admin:
        logger.warning(
            "Access denied: user does not own project",
            project_id=project_id,
            user_id=user_id,
            owner_id=project.owner_id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    logger.info(
        "Project retrieved",
        project_id=project_id,
        user=user.user_id if user else "anonymous",
    )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        requirements=project.requirements,
        status=ProjectStatus(project.status),
        tech_stack=project.tech_stack,
        current_phase=project.current_phase,
        progress_percent=project.progress_percent,
        created_at=project.created_at,
        updated_at=project.updated_at,
        metadata=project.extra_metadata
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
)
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    Update project information.

    Only provided fields will be updated.
    """
    project = await project_service.get_project(project_id, db=db)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Check ownership/permissions
    if project.owner_id != (user.user_id if user else "anonymous"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project"
        )

    # Prepare updates
    update_data = request.model_dump(exclude_unset=True)
    if "status" in update_data:
        update_data["status"] = update_data["status"].value

    updated_project = await project_service.update_project(
        project_id=project_id,
        updates=update_data,
        db=db
    )

    logger.info(
        "Project updated",
        project_id=project_id,
        updated_fields=list(update_data.keys()),
        user=user.user_id if user else "anonymous",
    )

    return ProjectResponse(
        id=updated_project.id,
        name=updated_project.name,
        description=updated_project.description,
        requirements=updated_project.requirements,
        status=ProjectStatus(updated_project.status),
        tech_stack=updated_project.tech_stack,
        current_phase=updated_project.current_phase,
        progress_percent=updated_project.progress_percent,
        created_at=updated_project.created_at,
        updated_at=updated_project.updated_at,
        metadata=updated_project.metadata
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
async def delete_project(
    project_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a project and all associated data.

    This action cannot be undone.
    """
    project = await project_service.get_project(project_id, db=db)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Check ownership/permissions
    if project.owner_id != (user.user_id if user else "anonymous"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )

    success = await project_service.delete_project(project_id, db=db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

    logger.info(
        "Project deleted",
        project_id=project_id,
        user=user.user_id if user else "anonymous",
    )


@router.post(
    "/{project_id}/activate",
    response_model=ProjectResponse,
    summary="Activate project",
)
async def activate_project(
    project_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """
    Activate a project to start the AI development workflow.

    Changes status from DRAFT to ACTIVE and begins the first phase.
    """
    project = await project_service.get_project(project_id, db=db)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )

    # Check ownership/permissions
    if project.owner_id != (user.user_id if user else "anonymous"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to activate this project"
        )

    if project.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot activate project with status {project.status}"
        )

    updated_project = await project_service.update_project(
        project_id=project_id,
        updates={
            "status": "active",
            "current_phase": "requirements"
        },
        db=db
    )

    logger.info(
        "Project activated",
        project_id=project_id,
        user=user.user_id if user else "anonymous",
    )

    return ProjectResponse(
        id=updated_project.id,
        name=updated_project.name,
        description=updated_project.description,
        requirements=updated_project.requirements,
        status=ProjectStatus(updated_project.status),
        tech_stack=updated_project.tech_stack,
        current_phase=updated_project.current_phase,
        progress_percent=updated_project.progress_percent,
        created_at=updated_project.created_at,
        updated_at=updated_project.updated_at,
        metadata=updated_project.metadata
    )
