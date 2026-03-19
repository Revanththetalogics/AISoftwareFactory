"""
API Routes for AI Software Factory.
"""

# Import individual route modules directly to avoid circular imports
from . import projects, workflows, agents, deployments, websocket, testing

__all__ = ["projects", "workflows", "agents", "deployments", "websocket", "testing"]
