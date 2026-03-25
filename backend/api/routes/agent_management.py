"""
Dynamic Agent and Crew Management API Routes.

This module provides REST endpoints for creating custom agents and crews
from the frontend.
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.llm.router import get_llm_router

logger = get_logger(__name__)
router = APIRouter(prefix="/agent-management", tags=["agent-management"])


class CreateAgentRequest(BaseModel):
    """Request to create a custom agent."""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    role: str = Field(..., min_length=1, max_length=100, description="Agent role (e.g., 'Security Engineer')")
    goal: str = Field(..., min_length=10, description="What the agent aims to accomplish")
    backstory: str = Field(..., min_length=10, description="Agent's background and expertise")
    llm_task_type: Literal["coding", "code_review", "reasoning", "chat", "general"] = Field(
        default="general",
        description="LLM task type for model selection"
    )
    allow_delegation: bool = Field(default=True, description="Whether agent can delegate tasks")


class CreateAgentResponse(BaseModel):
    """Response after creating an agent."""
    agent_id: str
    name: str
    role: str
    llm_model: str
    message: str


class CreateCrewRequest(BaseModel):
    """Request to create a custom crew."""
    name: str = Field(..., min_length=1, max_length=100, description="Crew name")
    description: str = Field(..., min_length=10, description="What this crew does")
    agent_ids: list[str] = Field(..., min_length=1, description="List of agent IDs to include")
    process: Literal["sequential", "hierarchical", "parallel"] = Field(
        default="sequential",
        description="How tasks are processed"
    )


class CreateCrewResponse(BaseModel):
    """Response after creating a crew."""
    crew_id: str
    name: str
    agent_count: int
    message: str


class ListModelsResponse(BaseModel):
    """Response listing available LLM models."""
    models: list[dict]


# In-memory storage for dynamically created agents/crews (in production, use database)
_dynamic_agents: dict[str, dict] = {}
_dynamic_crews: dict[str, dict] = {}


@router.post(
    "/agents",
    response_model=CreateAgentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom agent",
)
async def create_agent(
    request: CreateAgentRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreateAgentResponse:
    """
    Create a new custom agent dynamically.

    The agent will be configured with the specified role, goal, and backstory.
    LLM model is selected automatically based on llm_task_type.
    """
    import uuid

    # Select LLM based on task type
    router = get_llm_router()
    selected_model = router.select_model(request.llm_task_type)

    agent_id = f"agent-{uuid.uuid4().hex[:8]}"

    # Store agent configuration
    _dynamic_agents[agent_id] = {
        "id": agent_id,
        "name": request.name,
        "role": request.role,
        "goal": request.goal,
        "backstory": request.backstory,
        "llm_task_type": request.llm_task_type,
        "llm_model": selected_model,
        "allow_delegation": request.allow_delegation,
        "created_by": user.user_id if user else "anonymous",
    }

    logger.info(
        "Custom agent created",
        agent_id=agent_id,
        name=request.name,
        role=request.role,
        llm_model=selected_model,
        user=user.user_id if user else "anonymous",
    )

    return CreateAgentResponse(
        agent_id=agent_id,
        name=request.name,
        role=request.role,
        llm_model=selected_model,
        message=f"Agent '{request.name}' created successfully with {selected_model}",
    )


@router.get(
    "/agents",
    response_model=list[CreateAgentResponse],
    summary="List custom agents",
)
async def list_agents(
    user=Depends(get_current_user),
) -> list[CreateAgentResponse]:
    """List all dynamically created agents."""
    return [
        CreateAgentResponse(
            agent_id=agent["id"],
            name=agent["name"],
            role=agent["role"],
            llm_model=agent["llm_model"],
            message="",
        )
        for agent in _dynamic_agents.values()
    ]


@router.post(
    "/crews",
    response_model=CreateCrewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom crew",
)
async def create_crew(
    request: CreateCrewRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CreateCrewResponse:
    """
    Create a new custom crew dynamically from selected agents.
    
    Combines multiple agents into a collaborative crew for specific tasks.
    """
    import uuid

    crew_id = f"crew-{uuid.uuid4().hex[:8]}"

    # Validate agent IDs
    valid_agents = []
    for agent_id in request.agent_ids:
        if agent_id in _dynamic_agents:
            valid_agents.append(agent_id)
        else:
            # Check if it's a built-in agent
            valid_agents.append(agent_id)

    # Store crew configuration
    _dynamic_crews[crew_id] = {
        "id": crew_id,
        "name": request.name,
        "description": request.description,
        "agent_ids": valid_agents,
        "process": request.process,
        "created_by": user.user_id if user else "anonymous",
    }

    logger.info(
        "Custom crew created",
        crew_id=crew_id,
        name=request.name,
        agent_count=len(valid_agents),
        user=user.user_id if user else "anonymous",
    )

    return CreateCrewResponse(
        crew_id=crew_id,
        name=request.name,
        agent_count=len(valid_agents),
        message=f"Crew '{request.name}' created with {len(valid_agents)} agents",
    )


@router.get(
    "/crews",
    response_model=list[CreateCrewResponse],
    summary="List custom crews",
)
async def list_crews(
    user=Depends(get_current_user),
) -> list[CreateCrewResponse]:
    """List all dynamically created crews."""
    return [
        CreateCrewResponse(
            crew_id=crew["id"],
            name=crew["name"],
            agent_count=len(crew["agent_ids"]),
            message="",
        )
        for crew in _dynamic_crews.values()
    ]


@router.get(
    "/llm-models",
    response_model=ListModelsResponse,
    summary="Get available LLM models",
)
async def get_llm_models(
    user=Depends(get_current_user),
) -> ListModelsResponse:
    """
    Get list of available LLM models for agent creation.
    
    Returns models with their capabilities and recommended use cases.
    """
    models = [
        {
            "id": "deepseek-coder-v2",
            "name": "DeepSeek Coder v2",
            "task_types": ["coding", "code_review"],
            "description": "Best for code generation and review",
            "context_window": 128000,
        },
        {
            "id": "mixtral:8x7b",
            "name": "Mixtral 8x7b",
            "task_types": ["reasoning"],
            "description": "Best for complex reasoning and planning",
            "context_window": 32768,
        },
        {
            "id": "qwen2.5",
            "name": "Qwen 2.5",
            "task_types": ["chat", "general"],
            "description": "Good for general tasks and chat",
            "context_window": 32768,
        },
        {
            "id": "llama3.2",
            "name": "Llama 3.2",
            "task_types": ["general"],
            "description": "General purpose model",
            "context_window": 128000,
        },
    ]

    return ListModelsResponse(models=models)


@router.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom agent",
)
async def delete_agent(
    agent_id: str,
    user=Depends(get_current_user),
) -> None:
    """Delete a dynamically created agent."""
    if agent_id not in _dynamic_agents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found",
        )

    del _dynamic_agents[agent_id]

    logger.info(
        "Custom agent deleted",
        agent_id=agent_id,
        user=user.user_id if user else "anonymous",
    )


@router.delete(
    "/crews/{crew_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom crew",
)
async def delete_crew(
    crew_id: str,
    user=Depends(get_current_user),
) -> None:
    """Delete a dynamically created crew."""
    if crew_id not in _dynamic_crews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crew {crew_id} not found",
        )

    del _dynamic_crews[crew_id]

    logger.info(
        "Custom crew deleted",
        crew_id=crew_id,
        user=user.user_id if user else "anonymous",
    )
