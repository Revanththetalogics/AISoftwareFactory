"""
Agent Registry for AI Software Factory.

This module provides a registry for managing and discovering agents in the system.
It supports registration, unregistration, and lookup of agents by ID or role.
"""

from functools import lru_cache
from typing import Any, Optional

from backend.agents.base_agent import BaseAgent
from backend.core.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """
    Registry for managing agents in the AI Software Factory.

    This class provides a centralized registry for agent discovery and management.
    It supports:
    - Registering and unregistering agents
    - Looking up agents by ID or role
    - Listing all registered agents
    - Getting agents by capability

    The registry is implemented as a singleton to ensure consistent agent
    management across the application.

    Example:
        >>> registry = AgentRegistry()
        >>> registry.register(agent)
        >>> found_agent = registry.get_by_id(agent.agent_id)
    """

    _instance: Optional["AgentRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "AgentRegistry":
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the registry."""
        if not self._initialized:
            self._agents: dict[str, BaseAgent] = {}
            self._agents_by_role: dict[str, list[str]] = {}
            self._logger = get_logger(__name__)
            self._initialized = True
            self._logger.info("Agent registry initialized")

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent in the registry.

        Args:
            agent: Agent instance to register

        Raises:
            ValueError: If agent with same ID already registered

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register(my_agent)
        """
        agent_id = agent.agent_id

        if agent_id in self._agents:
            raise ValueError(f"Agent with ID '{agent_id}' is already registered")

        self._agents[agent_id] = agent

        # Index by role
        role = agent.role
        if role not in self._agents_by_role:
            self._agents_by_role[role] = []
        self._agents_by_role[role].append(agent_id)

        self._logger.info(
            "Agent registered",
            agent_id=agent_id,
            name=agent.name,
            role=role,
        )

    def unregister(self, agent_id: str) -> BaseAgent | None:
        """
        Unregister an agent from the registry.

        Args:
            agent_id: ID of agent to unregister

        Returns:
            The unregistered agent, or None if not found

        Example:
            >>> agent = registry.unregister("agent-123")
            >>> if agent:
            ...     print(f"Unregistered {agent.name}")
        """
        agent = self._agents.pop(agent_id, None)

        if agent:
            # Remove from role index
            role = agent.role
            if role in self._agents_by_role:
                self._agents_by_role[role].remove(agent_id)
                if not self._agents_by_role[role]:
                    del self._agents_by_role[role]

            self._logger.info("Agent unregistered", agent_id=agent_id, name=agent.name)

        return agent

    def get_by_id(self, agent_id: str) -> BaseAgent | None:
        """
        Get agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent instance, or None if not found

        Example:
            >>> agent = registry.get_by_id("agent-123")
            >>> if agent:
            ...     print(agent.name)
        """
        return self._agents.get(agent_id)

    def get_by_role(self, role: str) -> list[BaseAgent]:
        """
        Get all agents with a specific role.

        Args:
            role: Role to search for

        Returns:
            List of agents with the specified role

        Example:
            >>> agents = registry.get_by_role("CEO")
            >>> for agent in agents:
            ...     print(agent.name)
        """
        agent_ids = self._agents_by_role.get(role, [])
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def get_by_capability(self, capability: str) -> list[BaseAgent]:
        """
        Get all agents with a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of agents with the specified capability

        Example:
            >>> agents = registry.get_by_capability("architecture")
            >>> for agent in agents:
            ...     print(agent.name)
        """
        return [
            agent for agent in self._agents.values()
            if agent.has_capability(capability)
        ]

    def list_all(self) -> list[BaseAgent]:
        """
        List all registered agents.

        Returns:
            List of all registered agents

        Example:
            >>> agents = registry.list_all()
            >>> print(f"Total agents: {len(agents)}")
        """
        return list(self._agents.values())

    def list_roles(self) -> list[str]:
        """
        List all registered roles.

        Returns:
            List of unique roles

        Example:
            >>> roles = registry.list_roles()
            >>> print(f"Available roles: {roles}")
        """
        return list(self._agents_by_role.keys())

    def count(self) -> int:
        """
        Get total number of registered agents.

        Returns:
            Number of agents
        """
        return len(self._agents)

    def clear(self) -> None:
        """
        Clear all registered agents.

        WARNING: This is primarily for testing. Use with caution in production.
        """
        self._agents.clear()
        self._agents_by_role.clear()
        self._logger.warning("Agent registry cleared")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert registry state to dictionary.

        Returns:
            Dictionary containing registry information
        """
        return {
            "total_agents": self.count(),
            "roles": self.list_roles(),
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "role": agent.role,
                    "capabilities": agent.identity.capabilities,
                }
                for agent in self.list_all()
            ],
        }


@lru_cache
def get_agent_registry() -> AgentRegistry:
    """
    Get the singleton agent registry instance.

    Returns:
        AgentRegistry: Singleton registry instance

    Example:
        >>> registry = get_agent_registry()
        >>> registry.register(agent)
    """
    return AgentRegistry()


def reset_agent_registry() -> AgentRegistry:
    """
    Reset and return a fresh registry instance.

    This is primarily for testing purposes.

    Returns:
        AgentRegistry: Fresh registry instance
    """
    registry = AgentRegistry()
    registry.clear()
    AgentRegistry._instance = None
    return get_agent_registry()
