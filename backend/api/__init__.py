"""
API Layer for AI Software Factory.

This module provides REST API endpoints and WebSocket support for the AI Software Factory.
"""

from fastapi import APIRouter

# Import individual modules directly to avoid circular imports
from backend.api import health
from backend.api.dependencies import get_current_user, require_permissions
from backend.api.models import (
    AgentResponse,
    DeploymentRequest,
    DeploymentResponse,
    ProjectCreate,
    ProjectResponse,
    WorkflowExecuteRequest,
    WorkflowStatusResponse,
)

# Import route modules directly
from backend.api.routes import (
    admin,
    agent_management,
    agents,
    analytics,
    # Phase 3 Enterprise Features
    architecture,
    auth,
    infrastructure,
    monitoring,
    scaling,
    codegen,
    collaboration,
    customization,
    db_performance,
    deployments,
    events,
    git,
    knowledge,
    plugins,
    projects,
    rate_limits,
    reports,
    resources,
    schema,
    simulations,
    testing,
    websocket,
    workflows,
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
api_router.include_router(testing.router)
api_router.include_router(events.router)
api_router.include_router(agent_management.router)
api_router.include_router(codegen.router)
api_router.include_router(knowledge.router)
api_router.include_router(simulations.router)
api_router.include_router(git.router)
api_router.include_router(resources.router)
api_router.include_router(scaling.router)
api_router.include_router(monitoring.router)
api_router.include_router(infrastructure.router)
api_router.include_router(db_performance.router)
api_router.include_router(rate_limits.router)
# Phase 3 Enterprise Feature Routes
api_router.include_router(architecture.router)
api_router.include_router(schema.router)
api_router.include_router(analytics.router)
api_router.include_router(collaboration.router)
api_router.include_router(plugins.router)
api_router.include_router(customization.router)
api_router.include_router(admin.router)
api_router.include_router(reports.router)
# WebSocket routes are mounted at app level, not in API router

__all__ = [
    "api_router",
    "projects",
    "workflows",
    "agents",
    "deployments",
    "websocket",
    "auth",
    "testing",
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
