"""
Agent Management API Routes.

This module provides REST endpoints for agent management and task assignment.
Uses DatabaseAgentService for database-backed agent persistence.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_agent_service, get_current_user
from backend.api.models import AgentResponse, AgentTaskRequest, TaskAssignmentResponse
from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.services.database_services import DatabaseAgentService

logger = get_logger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


def _db_agent_to_response(agent) -> AgentResponse:
    """Convert a DBAgent to AgentResponse."""
    return AgentResponse(
        agent_id=agent.id,
        name=agent.name,
        role=agent.role,
        capabilities=agent.capabilities or [],
        status=agent.status,
        current_task=agent.current_task_id,
        last_active=agent.last_active,
        metadata=agent.config or {},
    )


@router.get(
    "",
    response_model=list[AgentResponse],
    summary="List all agents",
)
async def list_agents(
    role: str = None,
    agent_status: str = None,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    agent_service: DatabaseAgentService = Depends(get_agent_service),
) -> list[AgentResponse]:
    """
    List all registered agents and their status.
    """
    agents = await agent_service.list_agents(role=role, status=agent_status, db=db)

    logger.info(
        "Agents listed",
        count=len(agents),
        user=user.user_id if user else "anonymous",
    )

    return [_db_agent_to_response(agent) for agent in agents]


@router.get(
    "/{agent_id}",
    response_model=AgentResponse,
    summary="Get agent details",
)
async def get_agent(
    agent_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    agent_service: DatabaseAgentService = Depends(get_agent_service),
) -> AgentResponse:
    """
    Get detailed information about a specific agent.
    """
    agent = await agent_service.get_agent(agent_id, db=db)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    return _db_agent_to_response(agent)


@router.post(
    "",
    response_model=AgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new agent",
)
async def register_agent(
    name: str,
    role: str,
    capabilities: list[str] = None,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    agent_service: DatabaseAgentService = Depends(get_agent_service),
) -> AgentResponse:
    """
    Register a new agent in the system.
    """
    agent = await agent_service.register_agent(name=name, role=role, capabilities=capabilities or [], db=db)

    logger.info(
        "Agent registered",
        agent_id=agent.id,
        name=name,
        role=role,
        user=user.user_id if user else "anonymous",
    )

    return _db_agent_to_response(agent)


@router.post(
    "/{agent_id}/tasks",
    response_model=TaskAssignmentResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Assign task to agent",
)
async def assign_task(
    agent_id: str,
    request: AgentTaskRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    agent_service: DatabaseAgentService = Depends(get_agent_service),
) -> TaskAssignmentResponse:
    """
    Assign a task to a specific agent.

    The agent will process the task asynchronously.
    """
    agent = await agent_service.get_agent(agent_id, db=db)

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    # Check if agent is busy
    if agent.status == "busy":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent {agent_id} is currently busy",
        )

    task_id = f"task-{uuid4().hex[:12]}"

    # TODO: Update agent status to busy and assign task
    # This would require adding an update method to DatabaseAgentService

    logger.info(
        "Task assigned to agent",
        task_id=task_id,
        agent_id=agent_id,
        task_type=request.task_type,
        user=user.user_id if user else "anonymous",
    )

    return TaskAssignmentResponse(
        task_id=task_id,
        agent_id=agent_id,
        status="accepted",
        message=f"Task {request.task_type} assigned to agent {agent_id}",
    )


@router.get(
    "/roles/available",
    response_model=list[str],
    summary="Get available agent roles",
)
async def get_available_roles(
    user=Depends(get_current_user),
) -> list[str]:
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
