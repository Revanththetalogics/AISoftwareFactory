"""
Workflow Execution API Routes.

This module provides REST endpoints for workflow management and execution.
"""

from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status

from backend.api.models import (
    WorkflowExecuteRequest,
    WorkflowStatusResponse,
)
from backend.api.dependencies import get_current_user, require_permissions
from backend.workflows.state_machine import ProjectPhase
from backend.workflows.workflow_engine import WorkflowEngine
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/workflows", tags=["workflows"])

# In-memory workflow store
_workflows: dict[str, dict] = {}


async def _execute_workflow_real(workflow_id: str, project_id: str, phase: Optional[str]):
    """Execute workflow using the real LangGraph engine."""
    try:
        workflow = _workflows.get(workflow_id)
        if not workflow:
            return
        
        workflow["status"] = "running"
        workflow["started_at"] = datetime.now()
        workflow["logs"].append("Initializing LangGraph workflow engine...")
        
        # Initialize and run the real workflow engine
        engine = WorkflowEngine()
        
        # Create initial state
        from backend.workflows.state_machine import WorkflowState
        initial_state = WorkflowState(
            project_id=project_id,
            current_phase=ProjectPhase(phase) if phase else ProjectPhase.IDEA,
        )
        
        workflow["logs"].append(f"Starting workflow from phase: {initial_state.current_phase.value}")
        
        # Run the workflow (this will execute all phases via LangGraph)
        final_state = await engine.run(initial_state)
        
        # Update workflow with results
        workflow["current_phase"] = final_state.current_phase.value
        workflow["progress_percent"] = 100 if final_state.current_phase == ProjectPhase.COMPLETE else 75
        workflow["completed_at"] = datetime.now()
        
        if final_state.current_phase == ProjectPhase.FAILED:
            workflow["status"] = "failed"
            workflow["error_message"] = "Workflow execution failed"
            workflow["logs"].append("Workflow failed during execution")
        else:
            workflow["status"] = "completed"
            workflow["logs"].append("Workflow completed successfully via LangGraph engine")
            
        logger.info(
            "Real workflow execution completed",
            workflow_id=workflow_id,
            project_id=project_id,
            final_phase=final_state.current_phase.value,
        )
        
    except Exception as exc:
        logger.error(
            "Real workflow execution failed",
            workflow_id=workflow_id,
            project_id=project_id,
            error=str(exc),
        )
        workflow = _workflows.get(workflow_id)
        if workflow:
            workflow["status"] = "failed"
            workflow["error_message"] = str(exc)
            workflow["completed_at"] = datetime.now()
            workflow["logs"].append(f"Error: {str(exc)}")


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
) -> WorkflowStatusResponse:
    """
    Execute a workflow for a project.
    
    The workflow will run asynchronously. Use the returned workflow_id
    to check status via GET /workflows/{workflow_id}.
    """
    workflow_id = f"wf-{uuid4().hex[:12]}"
    
    workflow = {
        "workflow_id": workflow_id,
        "project_id": request.project_id,
        "status": "pending",
        "current_phase": request.phase or "requirements",
        "progress_percent": 0,
        "steps_completed": 0,
        "steps_total": 5,
        "started_at": None,
        "completed_at": None,
        "error_message": None,
        "logs": ["Workflow queued for execution"],
    }
    
    _workflows[workflow_id] = workflow
    
    # Start execution in background
    if request.async_execution:
        background_tasks.add_task(
            _execute_workflow_real,
            workflow_id,
            request.project_id,
            request.phase,
        )
    else:
        import asyncio
        asyncio.run(_execute_workflow_real(workflow_id, request.project_id, request.phase))
    
    logger.info(
        "Workflow execution started",
        workflow_id=workflow_id,
        project_id=request.project_id,
        phase=request.phase,
        user=user.user_id if user else "anonymous",
    )
    
    return WorkflowStatusResponse(**workflow)


@router.get(
    "/{workflow_id}",
    response_model=WorkflowStatusResponse,
    summary="Get workflow status",
)
async def get_workflow_status(
    workflow_id: str,
    user=Depends(get_current_user),
) -> WorkflowStatusResponse:
    """
    Get the current status of a workflow execution.
    """
    if workflow_id not in _workflows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    
    return WorkflowStatusResponse(**_workflows[workflow_id])


@router.get(
    "",
    response_model=List[WorkflowStatusResponse],
    summary="List workflows",
)
async def list_workflows(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    user=Depends(get_current_user),
) -> List[WorkflowStatusResponse]:
    """
    List workflow executions with optional filtering.
    """
    workflows = list(_workflows.values())
    
    if project_id:
        workflows = [w for w in workflows if w["project_id"] == project_id]
    
    if status:
        workflows = [w for w in workflows if w["status"] == status]
    
    # Sort by start time (newest first)
    workflows.sort(
        key=lambda w: w["started_at"] or datetime.min,
        reverse=True,
    )
    
    return [WorkflowStatusResponse(**w) for w in workflows]


@router.post(
    "/{workflow_id}/cancel",
    response_model=WorkflowStatusResponse,
    summary="Cancel workflow",
)
async def cancel_workflow(
    workflow_id: str,
    user=Depends(get_current_user),
) -> WorkflowStatusResponse:
    """
    Cancel a running workflow.
    """
    if workflow_id not in _workflows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    
    workflow = _workflows[workflow_id]
    
    if workflow["status"] not in ["pending", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel workflow with status {workflow['status']}",
        )
    
    workflow["status"] = "cancelled"
    workflow["completed_at"] = datetime.now()
    workflow["logs"].append("Workflow cancelled by user")
    
    logger.info(
        "Workflow cancelled",
        workflow_id=workflow_id,
        user=user.user_id if user else "anonymous",
    )
    
    return WorkflowStatusResponse(**workflow)


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
