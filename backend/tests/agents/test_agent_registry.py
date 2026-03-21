"""
Tests for AgentRegistry.
"""

import pytest

from backend.agents.agent_registry import AgentRegistry, get_agent_registry, reset_agent_registry
from backend.agents.base_agent import BaseAgent, Task, TaskResult, TaskStatus


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    async def execute_task(self, task: Task) -> TaskResult:
        return TaskResult(task_id=task.task_id, status=TaskStatus.COMPLETED)


class TestAgentRegistry:
    """Test cases for AgentRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        reset_agent_registry()

    def test_singleton(self):
        """Test that registry is a singleton."""
        registry1 = AgentRegistry()
        registry2 = AgentRegistry()

        assert registry1 is registry2

    def test_register_agent(self):
        """Test registering an agent."""
        registry = AgentRegistry()
        agent = MockAgent(agent_id="agent-1", name="Agent 1", role="Tester")

        registry.register(agent)

        assert registry.count() == 1
        assert registry.get_by_id("agent-1") is agent

    def test_register_duplicate_raises_error(self):
        """Test that registering duplicate agent raises error."""
        registry = AgentRegistry()
        agent = MockAgent(agent_id="agent-1", name="Agent 1", role="Tester")

        registry.register(agent)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(agent)

    def test_unregister_agent(self):
        """Test unregistering an agent."""
        registry = AgentRegistry()
        agent = MockAgent(agent_id="agent-1", name="Agent 1", role="Tester")

        registry.register(agent)
        unregistered = registry.unregister("agent-1")

        assert unregistered is agent
        assert registry.count() == 0
        assert registry.get_by_id("agent-1") is None

    def test_unregister_nonexistent(self):
        """Test unregistering non-existent agent."""
        registry = AgentRegistry()

        result = registry.unregister("nonexistent")

        assert result is None

    def test_get_by_role(self):
        """Test getting agents by role."""
        registry = AgentRegistry()
        agent1 = MockAgent(agent_id="agent-1", name="Agent 1", role="Tester")
        agent2 = MockAgent(agent_id="agent-2", name="Agent 2", role="Tester")
        agent3 = MockAgent(agent_id="agent-3", name="Agent 3", role="Developer")

        registry.register(agent1)
        registry.register(agent2)
        registry.register(agent3)

        testers = registry.get_by_role("Tester")

        assert len(testers) == 2
        assert agent1 in testers
        assert agent2 in testers

    def test_get_by_capability(self):
        """Test getting agents by capability."""
        registry = AgentRegistry()
        agent1 = MockAgent(agent_id="agent-1", capabilities=["testing", "debugging"])
        agent2 = MockAgent(agent_id="agent-2", capabilities=["testing"])
        agent3 = MockAgent(agent_id="agent-3", capabilities=["coding"])

        registry.register(agent1)
        registry.register(agent2)
        registry.register(agent3)

        testers = registry.get_by_capability("testing")

        assert len(testers) == 2
        assert agent1 in testers
        assert agent2 in testers

    def test_list_all(self):
        """Test listing all agents."""
        registry = AgentRegistry()
        agent1 = MockAgent(agent_id="agent-1")
        agent2 = MockAgent(agent_id="agent-2")

        registry.register(agent1)
        registry.register(agent2)

        all_agents = registry.list_all()

        assert len(all_agents) == 2
        assert agent1 in all_agents
        assert agent2 in all_agents

    def test_list_roles(self):
        """Test listing all roles."""
        registry = AgentRegistry()
        agent1 = MockAgent(agent_id="agent-1", role="Tester")
        agent2 = MockAgent(agent_id="agent-2", role="Developer")

        registry.register(agent1)
        registry.register(agent2)

        roles = registry.list_roles()

        assert "Tester" in roles
        assert "Developer" in roles

    def test_to_dict(self):
        """Test converting registry to dictionary."""
        registry = AgentRegistry()
        agent = MockAgent(agent_id="agent-1", name="Test Agent", role="Tester")

        registry.register(agent)
        result = registry.to_dict()

        assert result["total_agents"] == 1
        assert "Tester" in result["roles"]
        assert len(result["agents"]) == 1


class TestGetAgentRegistry:
    """Test cases for get_agent_registry function."""

    def test_get_agent_registry_returns_singleton(self):
        """Test that get_agent_registry returns singleton."""
        registry1 = get_agent_registry()
        registry2 = get_agent_registry()

        assert registry1 is registry2
