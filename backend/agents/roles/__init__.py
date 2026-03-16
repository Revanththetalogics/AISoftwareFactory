"""
CrewAI Role Definitions for AI Software Factory.

This module defines the roles used by CrewAI for agent collaboration.
Each role defines the agent's goal, backstory, and responsibilities.
"""

from backend.agents.roles.ceo_role import get_ceo_role
from backend.agents.roles.product_manager_role import get_product_manager_role
from backend.agents.roles.backend_engineer_role import get_backend_engineer_role
from backend.agents.roles.frontend_engineer_role import get_frontend_engineer_role
from backend.agents.roles.architect_role import get_architect_role
from backend.agents.roles.devops_engineer_role import get_devops_engineer_role

__all__ = [
    "get_ceo_role",
    "get_product_manager_role",
    "get_backend_engineer_role",
    "get_frontend_engineer_role",
    "get_architect_role",
    "get_devops_engineer_role",
]
