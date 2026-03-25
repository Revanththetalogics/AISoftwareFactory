"""
API Routes for AI Software Factory.
"""

# Import individual route modules directly to avoid circular imports
from . import agents, deployments, events, projects, testing, websocket, workflows

__all__ = ["projects", "workflows", "agents", "deployments", "websocket", "testing", "events"]
