"""
Project Management API Routes.

This module provides REST endpoints for project CRUD operations.
"""

from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, Query, status

from backend.api.models import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectStatus,
)
from backend.api.dependencies import get_current_user, require_permissions
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])

# In-memory project store (stub)
_projects: dict[str, dict] = {}


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    request: ProjectCreate,
    user=Depends(get_current_user),
) -> ProjectResponse:
    """
    Create a new software factory project.
    
    The project will be initialized in DRAFT status and can then be
    activated to start the AI-driven development workflow.
    """
    project_id = f"proj-{uuid4().hex[:12]}"
    
    project = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "requirements": request.requirements,
        "status": ProjectStatus.DRAFT,
        "tech_stack": request.tech_stack or {},
        "current_phase": None,
        "progress_percent": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "metadata": {
            "created_by": user.user_id if user else "anonymous",
        },
    }
    
    _projects[project_id] = project
    
    logger.info(
        "Project created",
        project_id=project_id,
        name=request.name,
        user=user.user_id if user else "anonymous",
    )
    
    return ProjectResponse(**project)


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
) -> List[ProjectResponse]:
    """
    List all projects with optional filtering.
    
    Supports pagination and status filtering.
    """
    projects = list(_projects.values())
    
    if status:
        projects = [p for p in projects if p["status"] == status]
    
    # Sort by creation date (newest first)
    projects.sort(key=lambda p: p["created_at"], reverse=True)
    
    # Apply pagination
    projects = projects[skip : skip + limit]
    
    logger.info(
        "Projects listed",
        count=len(projects),
        filter_status=status,
        user=user.user_id if user else "anonymous",
    )
    
    return [ProjectResponse(**p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
async def get_project(
    project_id: str,
    user=Depends(get_current_user),
) -> ProjectResponse:
    """
    Get detailed information about a specific project.
    """
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    logger.info(
        "Project retrieved",
        project_id=project_id,
        user=user.user_id if user else "anonymous",
    )
    
    return ProjectResponse(**_projects[project_id])


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project",
)
async def update_project(
    project_id: str,
    request: ProjectUpdate,
    user=Depends(get_current_user),
) -> ProjectResponse:
    """
    Update project information.
    
    Only provided fields will be updated.
    """
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    project = _projects[project_id]
    
    # Update only provided fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        project[field] = value
    
    project["updated_at"] = datetime.now()
    
    logger.info(
        "Project updated",
        project_id=project_id,
        updated_fields=list(update_data.keys()),
        user=user.user_id if user else "anonymous",
    )
    
    return ProjectResponse(**project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
async def delete_project(
    project_id: str,
    user=Depends(get_current_user),
) -> None:
    """
    Delete a project and all associated data.
    
    This action cannot be undone.
    """
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    del _projects[project_id]
    
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
) -> ProjectResponse:
    """
    Activate a project to start the AI development workflow.
    
    Changes status from DRAFT to ACTIVE and begins the first phase.
    """
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    project = _projects[project_id]
    
    if project["status"] != ProjectStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot activate project with status {project['status']}",
        )
    
    project["status"] = ProjectStatus.ACTIVE
    project["current_phase"] = "requirements"
    project["updated_at"] = datetime.now()
    
    logger.info(
        "Project activated",
        project_id=project_id,
        user=user.user_id if user else "anonymous",
    )
    
    return ProjectResponse(**project)
