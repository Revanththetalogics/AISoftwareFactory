"""
Workflow Execution API Routes.

This module provides REST endpoints for workflow management and execution.
Uses DatabaseWorkflowService for database-backed workflow persistence.
"""

from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.models import (
    WorkflowExecuteRequest,
    WorkflowStatusResponse,
)
from backend.api.dependencies import get_current_user, require_permissions, get_workflow_service
from backend.services.database_services import DatabaseWorkflowService
from backend.db.session import get_db
from backend.workflows.state_machine import ProjectPhase
from backend.workflows.workflow_engine import WorkflowEngine
from backend.models.workflow import WorkflowStatus
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])


def _db_workflow_to_response(workflow) -> WorkflowStatusResponse:
    """Convert a DBWorkflow to WorkflowStatusResponse."""
    # Calculate steps completed and total from workflow data
    steps = workflow.steps or []
    completed_steps = workflow.completed_steps or []
    
    return WorkflowStatusResponse(
        workflow_id=workflow.id,
        project_id=workflow.project_id,
        status=workflow.status.value if hasattr(workflow.status, 'value') else str(workflow.status),
        current_phase=workflow.current_step_id,
        progress_percent=int((len(completed_steps) / max(len(steps), 1)) * 100) if steps else 0,
        steps_completed=len(completed_steps),
        steps_total=len(steps),
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        error_message=workflow.context.get("error_message") if workflow.context else None,
        logs=workflow.context.get("logs", []) if workflow.context else [],
    )


async def _execute_workflow_real(workflow_id: str, project_id: str, phase: Optional[str]):
    """
    Execute workflow using the real LangGraph engine.
    
    This function runs as a background task and manages its own database session.
    """
    workflow_service = DatabaseWorkflowService()
    
    try:
        # Update workflow to running status
        workflow = await workflow_service.update_workflow_status(
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            current_step_id=phase or "requirements"
        )
        
        if not workflow:
            logger.error("Workflow not found for execution", workflow_id=workflow_id)
            return
        
        logger.info(
            "Starting workflow execution",
            workflow_id=workflow_id,
            project_id=project_id,
            phase=phase,
        )
        
        # Initialize and run the real workflow engine
        engine = WorkflowEngine()
        
        # Create initial state
        from backend.workflows.state_machine import WorkflowState
        initial_state = WorkflowState(
            project_id=project_id,
            current_phase=ProjectPhase(phase) if phase else ProjectPhase.IDEA,
        )
        
        # Run the workflow (this will execute all phases via LangGraph)
        final_state = await engine.run(initial_state)
        
        # Update workflow with final status
        if final_state.current_phase == ProjectPhase.FAILED:
            await workflow_service.update_workflow_status(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                current_step_id=final_state.current_phase.value
            )
        else:
            await workflow_service.update_workflow_status(
                workflow_id=workflow_id,
                status=WorkflowStatus.COMPLETED,
                current_step_id=final_state.current_phase.value
            )
        
        logger.info(
            "Workflow execution completed",
            workflow_id=workflow_id,
            project_id=project_id,
            final_phase=final_state.current_phase.value,
        )
        
    except Exception as exc:
        logger.error(
            "Workflow execution failed",
            workflow_id=workflow_id,
            project_id=project_id,
            error=str(exc),
        )
        # Update workflow to failed status
        await workflow_service.update_workflow_status(
            workflow_id=workflow_id,
            status=WorkflowStatus.FAILED
        )


@router.post(
    "/execute",
    response_model=WorkflowStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute workflow",
)
async def execute_workflow(
    request: WorkflowExecuteRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    workflow_service: DatabaseWorkflowService = Depends(get_workflow_service),
) -> WorkflowStatusResponse:
    """
    Execute a workflow for a project.
    
    The workflow will run asynchronously. Use the returned workflow_id
    to check status via GET /workflows/{workflow_id}.
    """
    # Define workflow steps based on request
    steps = [
        {"id": "requirements", "name": "Requirements Analysis"},
        {"id": "design", "name": "System Design"},
        {"id": "implementation", "name": "Implementation"},
        {"id": "testing", "name": "Testing"},
        {"id": "deployment", "name": "Deployment"},
    ]
    
    # Create workflow in database
    workflow = await workflow_service.create_workflow(
        name=f"Workflow for {request.project_id}",
        project_id=request.project_id,
        steps=steps,
        created_by=user.user_id if user else None,
        db=db
    )
    
    logger.info(
        "Workflow created",
        workflow_id=workflow.id,
        project_id=request.project_id,
        phase=request.phase,
        user=user.user_id if user else "anonymous",
    )
    
    # Start execution in background
    if request.async_execution:
        background_tasks.add_task(
            _execute_workflow_real,
            workflow.id,
            request.project_id,
            request.phase,
        )
    else:
        await _execute_workflow_real(workflow.id, request.project_id, request.phase)
    
    return _db_workflow_to_response(workflow)


@router.get(
    "/{workflow_id}",
    response_model=WorkflowStatusResponse,
    summary="Get workflow status",
)
async def get_workflow_status(
    workflow_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    workflow_service: DatabaseWorkflowService = Depends(get_workflow_service),
) -> WorkflowStatusResponse:
    """
    Get the current status of a workflow execution.
    """
    workflow = await workflow_service.get_workflow(workflow_id, db=db)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    
    return _db_workflow_to_response(workflow)


@router.get(
    "",
    response_model=List[WorkflowStatusResponse],
    summary="List workflows",
)
async def list_workflows(
    project_id: Optional[str] = None,
    workflow_status: Optional[str] = None,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[WorkflowStatusResponse]:
    """
    List workflow executions with optional filtering.
    """
    # Use direct database query for listing with filters
    from sqlalchemy import select
    from backend.models.database import DBWorkflow
    
    stmt = select(DBWorkflow)
    
    if project_id:
        stmt = stmt.where(DBWorkflow.project_id == project_id)
    
    if workflow_status:
        try:
            status_enum = WorkflowStatus(workflow_status)
            stmt = stmt.where(DBWorkflow.status == status_enum)
        except ValueError:
            pass  # Invalid status, ignore filter
    
    stmt = stmt.order_by(DBWorkflow.created_at.desc())
    
    result = await db.execute(stmt)
    workflows = list(result.scalars().all())
    
    return [_db_workflow_to_response(w) for w in workflows]


@router.post(
    "/{workflow_id}/cancel",
    response_model=WorkflowStatusResponse,
    summary="Cancel workflow",
)
async def cancel_workflow(
    workflow_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    workflow_service: DatabaseWorkflowService = Depends(get_workflow_service),
) -> WorkflowStatusResponse:
    """
    Cancel a running workflow.
    """
    workflow = await workflow_service.get_workflow(workflow_id, db=db)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    
    # Check if workflow can be cancelled
    if workflow.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel workflow with status {workflow.status.value}",
        )
    
    # Update to cancelled status
    updated_workflow = await workflow_service.update_workflow_status(
        workflow_id=workflow_id,
        status=WorkflowStatus.CANCELLED,
        db=db
    )
    
    logger.info(
        "Workflow cancelled",
        workflow_id=workflow_id,
        user=user.user_id if user else "anonymous",
    )
    
    return _db_workflow_to_response(updated_workflow)


@router.get(
    "/phases/available",
    response_model=List[str],
    summary="Get available workflow phases",
)
async def get_available_phases(
    user=Depends(get_current_user),
) -> List[str]:
    """
    Get list of available workflow phases.
    """
    return [p.value for p in ProjectPhase if p not in [ProjectPhase.COMPLETE, ProjectPhase.FAILED]]
