"""
Project Management API Routes.

This module provides REST endpoints for project CRUD operations.
"""


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user, get_workflow_service
from backend.api.models import (
    ProjectCreate,
    ProjectResponse,
    ProjectStatus,
    ProjectUpdate,
    QuickStartRequest,
    QuickStartResponse,
)
from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.models.workflow import WorkflowStatus
from backend.services.database_services import DatabaseWorkflowService, get_project_service

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
        owner_id=user.user_id,
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
    response_model=list[ProjectResponse],
    summary="List all projects",
)
async def list_projects(
    status: ProjectStatus | None = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
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
            metadata=p.extra_metadata
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
        metadata=updated_project.extra_metadata
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
        metadata=updated_project.extra_metadata
    )


@router.post(
    "/quickstart",
    response_model=QuickStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create and start project from a single prompt",
)
async def quickstart_project(
    request: QuickStartRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    workflow_service: DatabaseWorkflowService = Depends(get_workflow_service),
) -> QuickStartResponse:
    """
    Create a new project and immediately start the AI development workflow.

    This is the single-prompt SaaS creation endpoint. It:
    1. Creates a project from the user's idea/prompt
    2. Activates the project
    3. Starts the LangGraph workflow in the background
    4. Returns immediately with project and workflow IDs

    The workflow will execute all phases: Requirements → Architecture →
    Implementation → Testing → Deployment
    """
    # Import here to avoid circular imports
    from backend.workflows.state_machine import ProjectPhase, WorkflowState
    from backend.workflows.workflow_engine import WorkflowEngine

    # Step 1: Create project from the prompt
    project = await project_service.create_project(
        name=request.idea[:50] + "..." if len(request.idea) > 50 else request.idea,
        description=request.idea,
        requirements={
            "prompt": request.idea,
            "template": request.template or "custom",
            "auto_start": True,
        },
        tech_stack=request.tech_stack or {},
        owner_id=user.user_id if user else None,
        db=db
    )

    logger.info(
        "QuickStart project created",
        project_id=project.id,
        template=request.template,
        user=user.user_id if user else "anonymous",
    )

    # Step 2: Activate the project
    await project_service.update_project(
        project_id=project.id,
        updates={
            "status": "active",
            "current_phase": "requirements"
        },
        db=db
    )

    # Step 3: Create workflow
    steps = [
        {"id": "requirements", "name": "Requirements Analysis"},
        {"id": "architecture", "name": "System Design"},
        {"id": "implementation", "name": "Implementation"},
        {"id": "testing", "name": "Testing"},
        {"id": "deployment", "name": "Deployment"},
    ]

    workflow = await workflow_service.create_workflow(
        name=f"Auto-generated workflow for {project.name}",
        project_id=project.id,
        steps=steps,
        created_by=user.user_id if user else None,
        db=db
    )

    # Step 4: Start workflow execution in background
    async def execute_full_workflow():
        """Execute the complete workflow pipeline."""
        try:
            await workflow_service.update_workflow_status(
                workflow_id=workflow.id,
                status=WorkflowStatus.RUNNING,
                current_step_id="requirements"
            )

            # Initialize and run the workflow engine
            engine = WorkflowEngine()
            initial_state = WorkflowState(
                project_id=project.id,
                current_phase=ProjectPhase.IDEA,
                context={
                    "prompt": request.idea,
                    "template": request.template,
                    "tech_stack": request.tech_stack,
                }
            )

            final_state = await engine.run(initial_state)

            # Update final status
            if final_state.current_phase == ProjectPhase.FAILED:
                await workflow_service.update_workflow_status(
                    workflow_id=workflow.id,
                    status=WorkflowStatus.FAILED,
                    current_step_id=final_state.current_phase.value
                )
            else:
                await workflow_service.update_workflow_status(
                    workflow_id=workflow.id,
                    status=WorkflowStatus.COMPLETED,
                    current_step_id=final_state.current_phase.value
                )

        except Exception as exc:
            logger.error(
                "QuickStart workflow execution failed",
                project_id=project.id,
                workflow_id=workflow.id,
                error=str(exc),
            )
            await workflow_service.update_workflow_status(
                workflow_id=workflow.id,
                status=WorkflowStatus.FAILED
            )

    background_tasks.add_task(execute_full_workflow)

    logger.info(
        "QuickStart workflow started",
        project_id=project.id,
        workflow_id=workflow.id,
        user=user.user_id if user else "anonymous",
    )

    return QuickStartResponse(
        project_id=project.id,
        workflow_id=workflow.id,
        message="Project created and workflow started. Monitor progress via SSE events.",
        status="started",
    )
