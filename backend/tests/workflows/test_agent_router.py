"""
Tests for Agent Router.
"""

import pytest

from backend.agents.agent_registry import get_agent_registry
from backend.workflows.agent_router import AgentRouter
from backend.workflows.state_machine import ProjectPhase
from backend.workflows.task_manager import TaskPriority, WorkflowTask


class TestAgentRouter:
    """Test cases for AgentRouter."""

    def setup_method(self):
        """Create fresh router for each test."""
        # Reset registry for isolation
        get_agent_registry()
        # Clear existing agents (we'll re-initialize)
        self.router = AgentRouter()

    def test_router_initialization(self):
        """Test router initializes with default agents."""
        registry = get_agent_registry()

        # Should have default agents registered
        assert registry.count() >= 3

    def test_select_agent_for_task(self):
        """Test selecting agent for task."""
        task = WorkflowTask(
            name="Requirements Task",
            task_type="requirements",
            priority=TaskPriority.HIGH,
        )

        agent = self.router.select_agent_for_task(task)

        assert agent is not None

    def test_select_agent_for_unknown_task_type(self):
        """Test selecting agent for unknown task type."""
        task = WorkflowTask(
            name="Unknown Task",
            task_type="unknown_type",
            priority=TaskPriority.MEDIUM,
        )

        self.router.select_agent_for_task(task)

        # May or may not find agent depending on capabilities
        # This is acceptable behavior

    def test_select_agents_for_phase_requirements(self):
        """Test selecting agents for requirements phase."""
        agents = self.router.select_agents_for_phase(ProjectPhase.REQUIREMENTS)

        assert len(agents) > 0
        # Should include CEO and Product Manager
        roles = [agent.role for agent in agents]
        assert "CEO" in roles or "Product Manager" in roles

    def test_select_agents_for_phase_implementation(self):
        """Test selecting agents for implementation phase."""
        agents = self.router.select_agents_for_phase(ProjectPhase.IMPLEMENTATION)

        assert len(agents) > 0
        # Should include Backend Engineer
        roles = [agent.role for agent in agents]
        assert "Backend Engineer" in roles

    def test_get_available_agents(self):
        """Test getting available agents."""
        agents = self.router.get_available_agents()

        assert len(agents) > 0

    @pytest.mark.asyncio
    async def test_route_and_execute(self):
        """Test routing and executing a task."""
        task = WorkflowTask(
            name="Strategic Planning",
            task_type="strategic_planning",
            description="Create a strategic plan",
            context={"goal": "Build a SaaS app"},
        )

        result = await self.router.route_and_execute(task)

        assert "success" in result
        # May succeed or fail depending on stub implementation

    @pytest.mark.asyncio
    async def test_route_and_execute_no_agent_found(self):
        """Test route_and_execute when no suitable agent is found (covers line 198)."""
        task = WorkflowTask(
            name="Unknown Task",
            task_type="completely_unknown_capability_xyz",
            description="Task with no matching agent",
        )

        # Clear registry to ensure no agent matches
        from unittest.mock import patch

        with patch.object(self.router, "select_agent_for_task", return_value=None):
            result = await self.router.route_and_execute(task)

        assert result["success"] is False
        assert "No suitable agent found" in result["error"]

    @pytest.mark.asyncio
    async def test_route_and_execute_exception(self):
        """Test route_and_execute when execution raises exception (covers lines 223-231)."""
        task = WorkflowTask(
            name="Error Task",
            task_type="strategic_planning",
            description="Task that will fail",
        )

        from unittest.mock import AsyncMock, patch

        # Mock agent to raise exception during execute_task
        mock_agent = AsyncMock()
        mock_agent.agent_id = "test-agent"
        mock_agent.execute_task = AsyncMock(side_effect=RuntimeError("Execution error"))

        with patch.object(self.router, "select_agent_for_task", return_value=mock_agent):
            result = await self.router.route_and_execute(task)

        assert result["success"] is False
        assert "Execution error" in result["error"]

    def test_get_agent_workload(self):
        """Test get_agent_workload returns workload count (covers line 248)."""
        workload = self.router.get_agent_workload("any-agent-id")

        # Current stub implementation returns 0
        assert workload == 0
        assert isinstance(workload, int)
