"""
API Routes for AI Software Factory.
"""

# Import individual route modules directly to avoid circular imports
from . import (
    agents,
    db_performance,
    deployments,
    events,
    git,
    infrastructure,
    knowledge,
    monitoring,
    projects,
    rate_limits,
    resources,
    scaling,
    simulations,
    testing,
    websocket,
    workflows,
)

__all__ = ["projects", "workflows", "agents", "deployments", "websocket", "testing", "events", "db_performance", "rate_limits", "knowledge", "simulations", "git", "resources", "scaling", "monitoring", "infrastructure"]
