"""
Agent Management API Routes.

This module provides REST endpoints for agent management and task assignment.
"""

from typing import List
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends, status

from backend.api.models import AgentResponse, AgentTaskRequest
from backend.api.dependencies import get_current_user, require_permissions
from backend.agents.agent_registry import get_agent_registry
from backend.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


@router.get(
    "",
    response_model=List[AgentResponse],
    summary="List all agents",
)
async def list_agents(
    user=Depends(get_current_user),
) -> List[AgentResponse]:
    """
    List all registered agents and their status.
    """
    registry = get_agent_registry()
    
    agents = []
    for agent_id in registry.list_agents():
        # Stub: Create agent response from registry
        agent_data = {
            "agent_id": agent_id,
            "name": f"Agent {agent_id[:8]}",
            "role": "unknown",
            "capabilities": [],
            "status": "idle",
            "current_task": None,
            "last_active": None,
            "metadata": {},
        }
        agents.append(AgentResponse(**agent_data))
    
    logger.info(
        "Agents listed",
        count=len(agents),
        user=user.user_id if user else "anonymous",
    )
    
    return agents


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get agent details",
)
async def get_agent(
    agent_id: str,
    user=Depends(get_current_user),
) -> AgentResponse:
    """
    Get detailed information about a specific agent.
    """
    registry = get_agent_registry()
    
    if not registry.get_agent(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    
    # Stub: Return agent data
    agent_data = {
        "agent_id": agent_id,
        "name": f"Agent {agent_id[:8]}",
        "role": "software_engineer",
        "capabilities": ["code_generation", "code_review"],
        "status": "idle",
        "current_task": None,
        "last_active": datetime.now(),
        "metadata": {},
    }
    
    return AgentResponse(**agent_data)


@router.post(
    "/{agent_id}/tasks",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Assign task to agent",
)
async def assign_task(
    agent_id: str,
    request: AgentTaskRequest,
    user=Depends(get_current_user),
) -> dict:
    """
    Assign a task to a specific agent.
    
    The agent will process the task asynchronously.
    """
    registry = get_agent_registry()
    
    if not registry.get_agent(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )
    
    task_id = f"task-{uuid4().hex[:12]}"
    
    logger.info(
        "Task assigned to agent",
        task_id=task_id,
        agent_id=agent_id,
        task_type=request.task_type,
        user=user.user_id if user else "anonymous",
    )
    
    return {
        "task_id": task_id,
        "agent_id": agent_id,
        "status": "accepted",
        "message": f"Task {request.task_type} assigned to agent {agent_id}",
    }


@router.get(
    "/roles/available",
    response_model=List[str],
    summary="Get available agent roles",
)
async def get_available_roles(
    user=Depends(get_current_user),
) -> List[str]:
    """
    Get list of available agent roles.
    """
    return [
        "ceo",
        "product_manager",
        "architect",
        "backend_engineer",
        "frontend_engineer",
        "devops_engineer",
    ]
