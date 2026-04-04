"""
Agent Router for Workflow Engine.

This module provides task routing to appropriate agents or crews based on
task type, phase, and agent capabilities.
"""

from typing import Any

from backend.agents.agent_registry import get_agent_registry
from backend.agents.base_agent import BaseAgent
from backend.agents.base_agent import Task as AgentTask
from backend.agents.stubs import BackendEngineerAgent, CEOAgent, ProductManagerAgent
from backend.core.logging import get_logger
from backend.workflows.state_machine import ProjectPhase
from backend.workflows.task_manager import TaskManager, WorkflowTask

logger = get_logger(__name__)


class AgentRouter:
    """
    Router for assigning tasks to appropriate agents.

    This class is responsible for:
    - Selecting the best agent for a task
    - Routing tasks to individual agents or crews
    - Managing agent-task mappings
    - Handling agent availability

    Example:
        >>> router = AgentRouter()
        >>> agent = router.select_agent_for_task(task, phase=ProjectPhase.REQUIREMENTS)
        >>> result = await agent.execute_task(agent_task)
    """

    def __init__(self):
        """Initialize the agent router."""
        self._registry = get_agent_registry()
        self._task_manager = TaskManager()
        self._logger = get_logger(__name__)
        self._initialize_default_agents()

    def _initialize_default_agents(self) -> None:
        """Initialize default agents if not already registered."""
        # Check if agents already exist
        if self._registry.count() == 0:
            # Register default agents
            ceo = CEOAgent(name="CEO Agent")
            pm = ProductManagerAgent(name="Product Manager Agent")
            backend = BackendEngineerAgent(name="Backend Engineer Agent")

            self._registry.register(ceo)
            self._registry.register(pm)
            self._registry.register(backend)

            self._logger.info(
                "Default agents initialized",
                count=self._registry.count(),
            )

    def select_agent_for_task(
        self,
        task: WorkflowTask,
        phase: ProjectPhase | None = None,
    ) -> BaseAgent | None:
        """
        Select the best agent for a workflow task.

        Args:
            task: Workflow task
            phase: Current workflow phase

        Returns:
            Selected agent or None if no suitable agent found

        Example:
            >>> agent = router.select_agent_for_task(task, phase=ProjectPhase.REQUIREMENTS)
            >>> if agent:
            ...     result = await agent.execute_task(agent_task)
        """
        # Map task types to required capabilities
        capability_map = {
            "strategic_planning": ["strategic_planning"],
            "decision_making": ["decision_making"],
            "requirements": ["requirements_gathering"],
            "user_stories": ["user_story_creation"],
            "api_design": ["api_design"],
            "database_design": ["database_design"],
            "business_logic": ["business_logic"],
        }

        required_capabilities = capability_map.get(
            task.task_type,
            [task.task_type],
        )

        # Find agents with required capabilities
        candidates = []
        for capability in required_capabilities:
            agents = self._registry.get_by_capability(capability)
            candidates.extend(agents)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for agent in candidates:
            if agent.agent_id not in seen:
                seen.add(agent.agent_id)
                unique_candidates.append(agent)

        if not unique_candidates:
            self._logger.warning(
                "No agent found for task",
                task_type=task.task_type,
                required_capabilities=required_capabilities,
            )
            return None

        # Select first available agent (could be enhanced with load balancing)
        selected_agent = unique_candidates[0]

        self._logger.info(
            "Agent selected for task",
            task_id=task.task_id,
            task_type=task.task_type,
            agent_id=selected_agent.agent_id,
            agent_name=selected_agent.name,
        )

        return selected_agent

    def select_agents_for_phase(
        self,
        phase: ProjectPhase,
    ) -> list[BaseAgent]:
        """
        Select agents appropriate for a workflow phase.

        Args:
            phase: Workflow phase

        Returns:
            List of agents for the phase

        Example:
            >>> agents = router.select_agents_for_phase(ProjectPhase.REQUIREMENTS)
            >>> for agent in agents:
            ...     print(agent.name)
        """
        # Map phases to agent roles
        phase_role_map = {
            ProjectPhase.IDEA: ["CEO"],
            ProjectPhase.REQUIREMENTS: ["CEO", "Product Manager"],
            ProjectPhase.ARCHITECTURE: ["CEO", "Product Manager"],
            ProjectPhase.IMPLEMENTATION: ["Backend Engineer", "Product Manager"],
            ProjectPhase.TESTING: ["Backend Engineer"],
            ProjectPhase.DEPLOYMENT: ["Backend Engineer"],
        }

        roles = phase_role_map.get(phase, [])
        agents = []

        for role in roles:
            role_agents = self._registry.get_by_role(role)
            agents.extend(role_agents)

        # Remove duplicates
        seen = set()
        unique_agents = []
        for agent in agents:
            if agent.agent_id not in seen:
                seen.add(agent.agent_id)
                unique_agents.append(agent)

        return unique_agents

    async def route_and_execute(
        self,
        workflow_task: WorkflowTask,
    ) -> dict[str, Any]:
        """
        Route a task to an agent and execute it.

        Args:
            workflow_task: Workflow task to execute

        Returns:
            Execution result

        Example:
            >>> result = await router.route_and_execute(task)
            >>> print(result["status"])
        """
        # Select agent
        agent = self.select_agent_for_task(workflow_task)

        if not agent:
            return {
                "success": False,
                "error": "No suitable agent found",
            }

        # Convert workflow task to agent task
        agent_task = AgentTask(
            task_type=workflow_task.task_type,
            description=workflow_task.description,
            context=workflow_task.context,
            priority=workflow_task.priority.value,
        )

        try:
            # Execute task
            result = await agent.execute_task(agent_task)

            return {
                "success": result.status.value == "completed",
                "output": result.output,
                "error": result.error,
                "execution_time_ms": result.execution_time_ms,
                "agent_id": agent.agent_id,
            }

        except Exception as exc:
            self._logger.error(
                "Task execution failed",
                task_id=workflow_task.task_id,
                agent_id=agent.agent_id,
                error=str(exc),
            )

            return {
                "success": False,
                "error": str(exc),
            }

    def get_agent_workload(self, agent_id: str) -> int:
        """
        Get the number of tasks currently assigned to an agent.

        Args:
            agent_id: Agent ID

        Returns:
            Number of assigned tasks
        """
        return len(self._task_manager.get_assigned_tasks(agent_id=agent_id))

    def get_available_agents(self) -> list[BaseAgent]:
        """
        Get list of agents that have capacity to accept new tasks.

        Returns:
            List of agents whose current workload is below the capacity cap
        """
        max_tasks_per_agent = 5
        return [
            agent
            for agent in self._registry.list_all()
            if self.get_agent_workload(agent.agent_id) < max_tasks_per_agent
        ]
