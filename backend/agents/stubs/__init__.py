"""
Stub Agent Implementations for AI Software Factory.

This module provides concrete implementations of the BaseAgent class
for different roles in the software factory.
"""

from backend.agents.stubs.backend_engineer_agent import BackendEngineerAgent
from backend.agents.stubs.ceo_agent import CEOAgent
from backend.agents.stubs.product_manager_agent import ProductManagerAgent

__all__ = [
    "CEOAgent",
    "ProductManagerAgent",
    "BackendEngineerAgent",
]
