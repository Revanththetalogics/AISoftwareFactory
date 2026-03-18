"""
API Layer for AI Software Factory.

This module provides REST API endpoints and WebSocket support for the AI Software Factory.
"""

from fastapi import APIRouter

from backend.api.routes import projects, workflows, agents, deployments, websocket, auth
from backend.api import health
from backend.api.dependencies import get_current_user, require_permissions
from backend.api.models import (
    ProjectCreate,
    ProjectResponse,
    WorkflowExecuteRequest,
    WorkflowStatusResponse,
    AgentResponse,
    DeploymentRequest,
    DeploymentResponse,
)

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router)  # Authentication routes
api_router.include_router(projects.router)
api_router.include_router(workflows.router)
api_router.include_router(agents.router)
api_router.include_router(deployments.router)
# WebSocket routes are mounted at app level, not in API router

__all__ = [
    "api_router",
    "projects",
    "workflows",
    "agents",
    "deployments",
    "websocket",
    "auth",
    "get_current_user",
    "require_permissions",
    "ProjectCreate",
    "ProjectResponse",
    "WorkflowExecuteRequest",
    "WorkflowStatusResponse",
    "AgentResponse",
    "DeploymentRequest",
    "DeploymentResponse",
]
