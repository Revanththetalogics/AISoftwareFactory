"""
Agent service for AI Software Factory.

This module provides business logic for agent management operations.
"""

from typing import Any, Dict, List, Optional

from backend.agents.agent_registry import AgentRegistry
from backend.agents.base_agent import AgentStatus
from backend.core.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    """
    Service for managing agents.

    This service handles agent lifecycle, status monitoring, and task assignment.
    """

    def __init__(self):
        """Initialize the agent service."""
        self._registry = AgentRegistry()
        self._logger = get_logger(__name__)

    async def list_agents(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all registered agents.

        Args:
            status: Filter by status
            role: Filter by role

        Returns:
            List of agent data
        """
        agents = self._registry.list_agents()

        # Convert to dict representation
        agent_list = []
        for agent in agents:
            agent_data = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,
                "status": agent.status.value,
                "capabilities": agent.capabilities,
                "current_task": agent.current_task,
                "last_active": agent.last_active.isoformat() if agent.last_active else None
            }

            # Apply filters
            if status and agent_data["status"] != status:
                continue
            if role and agent_data["role"] != role:
                continue

            agent_list.append(agent_data)

        return agent_list

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent data or None if not found
        """
        agent = self._registry.get_agent(agent_id)
        if not agent:
            return None

        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "role": agent.role,
            "status": agent.status.value,
            "capabilities": agent.capabilities,
            "current_task": agent.current_task,
            "last_active": agent.last_active.isoformat() if agent.last_active else None,
            "config": agent.config
        }

    async def assign_task(
        self,
        agent_id: str,
        task_id: str,
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Assign a task to an agent.

        Args:
            agent_id: Agent ID
            task_id: Task ID
            task_data: Task data

        Returns:
            True if assigned, False if agent not found or busy
        """
        agent = self._registry.get_agent(agent_id)
        if not agent:
            return False

        if agent.status == AgentStatus.BUSY:
            self._logger.warning(
                "Agent is busy",
                agent_id=agent_id,
                current_task=agent.current_task
            )
            return False

        agent.current_task = task_id
        agent.status = AgentStatus.BUSY

        self._logger.info(
            "Task assigned to agent",
            agent_id=agent_id,
            task_id=task_id
        )
        return True

    async def release_agent(self, agent_id: str) -> bool:
        """
        Release an agent from its current task.

        Args:
            agent_id: Agent ID

        Returns:
            True if released, False if not found
        """
        agent = self._registry.get_agent(agent_id)
        if not agent:
            return False

        agent.current_task = None
        agent.status = AgentStatus.IDLE

        self._logger.info("Agent released", agent_id=agent_id)
        return True

    async def get_agent_activity(self) -> List[Dict[str, Any]]:
        """
        Get recent agent activity.

        Returns:
            List of activity records
        """
        # This would typically query a database
        # For now, return mock data
        return [
            {
                "id": "act-001",
                "agent_name": "CEO Agent",
                "agent_role": "ceo",
                "action": "project_initiated",
                "target": "Project Alpha",
                "timestamp": "2026-03-17T10:00:00Z",
                "status": "completed"
            }
        ]
