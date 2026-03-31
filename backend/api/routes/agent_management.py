"""
Dynamic Agent and Crew Management API Routes.

This module provides REST endpoints for creating custom agents and crews
from the frontend. Data is persisted in the database so that it survives
server restarts.
"""

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import get_current_user
from backend.core.logging import get_logger
from backend.db.session import get_db
from backend.llm.router import get_llm_router
from backend.models.database import DBAgent, DBCustomCrew

logger = get_logger(__name__)
router = APIRouter(prefix="/agent-management", tags=["agent-management"])


# ── Pydantic models ────────────────────────────────────────────────────────────

class CreateAgentRequest(BaseModel):
    """Request to create a custom agent."""
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., min_length=1, max_length=100)
    goal: str = Field(..., min_length=10)
    backstory: str = Field(..., min_length=10)
    llm_task_type: Literal["coding", "code_review", "reasoning", "chat", "general"] = "general"
    allow_delegation: bool = True


class CreateAgentResponse(BaseModel):
    agent_id: str
    name: str
    role: str
    llm_model: str
    message: str


class CreateCrewRequest(BaseModel):
    """Request to create a custom crew."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    agent_ids: list[str] = Field(..., min_length=1)
    process: Literal["sequential", "hierarchical", "parallel"] = "sequential"


class CreateCrewResponse(BaseModel):
    crew_id: str
    name: str
    agent_count: int
    message: str


class ListModelsResponse(BaseModel):
    models: list[dict]


# ── Agents ─────────────────────────────────────────────────────────────────────

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
    """Create a new custom agent and persist it to the database."""
    llm_router = get_llm_router()
    selected_model = llm_router.select_model(request.llm_task_type)

    agent_id = f"agent-{uuid.uuid4().hex[:8]}"

    db_agent = DBAgent(
        id=agent_id,
        name=request.name,
        role=request.role,
        description=request.goal,
        capabilities=[request.role],
        status="idle",
        config={
            "goal": request.goal,
            "backstory": request.backstory,
            "llm_task_type": request.llm_task_type,
            "llm_model": selected_model,
            "allow_delegation": request.allow_delegation,
            "created_by": user.user_id if user else "anonymous",
            "is_custom": True,
        },
    )

    db.add(db_agent)
    await db.flush()

    logger.info("Custom agent created", agent_id=agent_id, name=request.name, role=request.role)

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
    db: AsyncSession = Depends(get_db),
) -> list[CreateAgentResponse]:
    """List all custom agents created by the current user."""
    result = await db.execute(
        select(DBAgent).where(
            DBAgent.config["is_custom"].as_boolean() == True  # noqa: E712
        )
    )
    agents = result.scalars().all()

    return [
        CreateAgentResponse(
            agent_id=a.id,
            name=a.name,
            role=a.role,
            llm_model=(a.config or {}).get("llm_model", "unknown"),
            message="",
        )
        for a in agents
    ]


@router.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom agent",
)
async def delete_agent(
    agent_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a custom agent from the database."""
    agent = await db.get(DBAgent, agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent {agent_id} not found")

    await db.delete(agent)
    logger.info("Custom agent deleted", agent_id=agent_id)


# ── Crews ──────────────────────────────────────────────────────────────────────

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
    """Create a new crew from selected agents and persist it to the database."""
    crew_id = f"crew-{uuid.uuid4().hex[:8]}"

    db_crew = DBCustomCrew(
        id=crew_id,
        name=request.name,
        description=request.description,
        agent_ids=request.agent_ids,
        process=request.process,
        created_by=user.user_id if user else None,
    )

    db.add(db_crew)
    await db.flush()

    logger.info("Custom crew created", crew_id=crew_id, name=request.name, agent_count=len(request.agent_ids))

    return CreateCrewResponse(
        crew_id=crew_id,
        name=request.name,
        agent_count=len(request.agent_ids),
        message=f"Crew '{request.name}' created with {len(request.agent_ids)} agents",
    )


@router.get(
    "/crews",
    response_model=list[CreateCrewResponse],
    summary="List custom crews",
)
async def list_crews(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CreateCrewResponse]:
    """List all custom crews."""
    result = await db.execute(select(DBCustomCrew))
    crews = result.scalars().all()

    return [
        CreateCrewResponse(
            crew_id=c.id,
            name=c.name,
            agent_count=len(c.agent_ids or []),
            message="",
        )
        for c in crews
    ]


@router.delete(
    "/crews/{crew_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom crew",
)
async def delete_crew(
    crew_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a custom crew from the database."""
    crew = await db.get(DBCustomCrew, crew_id)
    if not crew:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crew {crew_id} not found")

    await db.delete(crew)
    logger.info("Custom crew deleted", crew_id=crew_id)


# ── LLM Models ─────────────────────────────────────────────────────────────────

@router.get(
    "/llm-models",
    response_model=ListModelsResponse,
    summary="Get available LLM models",
)
async def get_llm_models(user=Depends(get_current_user)) -> ListModelsResponse:
    """Return the list of available LLM models for agent creation."""
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
