"""
Agent Framework for AI Software Factory.

This module provides the agent framework including:
- BaseAgent: Abstract base class for all agents
- AgentRegistry: Registration and discovery of agents
- CrewAI roles and crew configurations
- Model routing for LLM integration
"""

from backend.agents.agent_registry import AgentRegistry, get_agent_registry
from backend.agents.base_agent import AgentIdentity, BaseAgent, Task, TaskResult

__all__ = [
    "BaseAgent",
    "AgentIdentity",
    "Task",
    "TaskResult",
    "AgentRegistry",
    "get_agent_registry",
]
