"""
Agent Framework for AI Software Factory.

This module provides the agent framework including:
- BaseAgent: Abstract base class for all agents
- AgentRegistry: Registration and discovery of agents
- CrewAI roles and crew configurations
- Model routing for LLM integration
"""

from backend.agents.base_agent import BaseAgent, AgentIdentity, Task, TaskResult
from backend.agents.agent_registry import AgentRegistry, get_agent_registry

__all__ = [
    "BaseAgent",
    "AgentIdentity", 
    "Task",
    "TaskResult",
    "AgentRegistry",
    "get_agent_registry",
]
