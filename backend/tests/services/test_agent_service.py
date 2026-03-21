"""
Comprehensive tests for agent service module.

Tests for AgentService covering all methods and edge cases.
"""

from datetime import datetime

import pytest
from backend.agents.base_agent import AgentStatus, BaseAgent
from backend.services.agent_service import AgentService


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(
        self,
        agent_id=None,
        name="Mock Agent",
        role="developer",
        capabilities=None,
        status=AgentStatus.IDLE,
        current_task=None,
        last_active=None
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities or ["code"]
        )
        self._status = status
        self._current_task = current_task
        self._last_active = last_active
        self._config = {}
        self._capabilities = capabilities or ["code"]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def current_task(self):
        return self._current_task

    @current_task.setter
    def current_task(self, value):
        self._current_task = value

    @property
    def last_active(self):
        return self._last_active

    @property
    def config(self):
        return self._config

    @property
    def capabilities(self):
        return self._capabilities

    async def execute_task(self, task):
        pass


class TestAgentService:
    """Comprehensive tests for AgentService."""

    def setup_method(self):
        """Setup test fixtures."""
        self.service = AgentService()
        # Mock the registry methods to match what AgentService expects
        self.mock_agents = []

        def mock_list_agents():
            return self.mock_agents

        def mock_get_agent(agent_id):
            for agent in self.mock_agents:
                if agent.agent_id == agent_id:
                    return agent
            return None

        # Patch the registry methods
        self.service._registry.list_agents = mock_list_agents
        self.service._registry.get_agent = mock_get_agent

    @pytest.mark.asyncio
    async def test_list_agents_empty(self):
        """Test listing agents when registry is empty."""
        self.mock_agents = []
        agents = await self.service.list_agents()
        assert agents == []

    @pytest.mark.asyncio
    async def test_list_agents_with_agents(self):
        """Test listing agents with registered agents."""
        self.mock_agents = [
            MockAgent(agent_id="agent-1", name="Agent 1", role="developer"),
            MockAgent(agent_id="agent-2", name="Agent 2", role="designer")
        ]

        agents = await self.service.list_agents()

        assert len(agents) == 2

    @pytest.mark.asyncio
    async def test_list_agents_filter_by_status(self):
        """Test listing agents filtered by status."""
        self.mock_agents = [
            MockAgent(agent_id="agent-1", status=AgentStatus.IDLE),
            MockAgent(agent_id="agent-2", status=AgentStatus.BUSY)
        ]

        agents = await self.service.list_agents(status="idle")

        assert len(agents) == 1
        assert agents[0]["status"] == "idle"

    @pytest.mark.asyncio
    async def test_list_agents_filter_by_role(self):
        """Test listing agents filtered by role."""
        self.mock_agents = [
            MockAgent(agent_id="agent-1", role="developer"),
            MockAgent(agent_id="agent-2", role="designer")
        ]

        agents = await self.service.list_agents(role="developer")

        assert len(agents) == 1
        assert agents[0]["role"] == "developer"

    @pytest.mark.asyncio
    async def test_list_agents_filter_by_both(self):
        """Test listing agents filtered by both status and role."""
        self.mock_agents = [
            MockAgent(agent_id="agent-1", role="developer", status=AgentStatus.IDLE),
            MockAgent(agent_id="agent-2", role="developer", status=AgentStatus.BUSY),
            MockAgent(agent_id="agent-3", role="designer", status=AgentStatus.IDLE)
        ]

        agents = await self.service.list_agents(status="idle", role="developer")

        assert len(agents) == 1
        assert agents[0]["status"] == "idle"
        assert agents[0]["role"] == "developer"

    @pytest.mark.asyncio
    async def test_list_agents_data_format(self):
        """Test that listed agents have correct data format."""
        self.mock_agents = [
            MockAgent(
                agent_id="agent-1",
                name="Test Agent",
                role="developer",
                capabilities=["code", "test"],
                status=AgentStatus.IDLE,
                current_task=None,
                last_active=datetime.utcnow()
            )
        ]

        agents = await self.service.list_agents()

        assert len(agents) == 1
        agent_data = agents[0]
        assert "agent_id" in agent_data
        assert "name" in agent_data
        assert "role" in agent_data
        assert "status" in agent_data
        assert "capabilities" in agent_data
        assert "current_task" in agent_data
        assert "last_active" in agent_data

    @pytest.mark.asyncio
    async def test_list_agents_last_active_none(self):
        """Test listing agents with None last_active."""
        self.mock_agents = [MockAgent(agent_id="agent-1", last_active=None)]

        agents = await self.service.list_agents()

        assert agents[0]["last_active"] is None

    @pytest.mark.asyncio
    async def test_get_agent_existing(self):
        """Test getting an existing agent."""
        agent = MockAgent(agent_id="agent-1", name="Test Agent")
        self.mock_agents = [agent]

        result = await self.service.get_agent("agent-1")

        assert result is not None
        assert result["agent_id"] == "agent-1"
        assert result["name"] == "Test Agent"

    @pytest.mark.asyncio
    async def test_get_agent_nonexistent(self):
        """Test getting a nonexistent agent."""
        self.mock_agents = []
        result = await self.service.get_agent("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_agent_data_format(self):
        """Test that get_agent returns correct data format."""
        agent = MockAgent(
            agent_id="agent-1",
            name="Test Agent",
            role="developer",
            capabilities=["code", "test"],
            status=AgentStatus.IDLE,
            current_task="task-123",
            last_active=datetime.utcnow()
        )
        agent._config = {"model": "gpt-4"}
        self.mock_agents = [agent]

        result = await self.service.get_agent("agent-1")

        assert result is not None
        assert "agent_id" in result
        assert "name" in result
        assert "role" in result
        assert "status" in result
        assert "capabilities" in result
        assert "current_task" in result
        assert "last_active" in result
        assert "config" in result

    @pytest.mark.asyncio
    async def test_assign_task_success(self):
        """Test assigning a task to an agent successfully."""
        agent = MockAgent(agent_id="agent-1", status=AgentStatus.IDLE)
        self.mock_agents = [agent]

        result = await self.service.assign_task(
            agent_id="agent-1",
            task_id="task-123",
            task_data={"description": "Test task"}
        )

        assert result is True
        assert agent.current_task == "task-123"
        assert agent.status == AgentStatus.BUSY

    @pytest.mark.asyncio
    async def test_assign_task_agent_not_found(self):
        """Test assigning task to nonexistent agent."""
        self.mock_agents = []
        result = await self.service.assign_task(
            agent_id="nonexistent-id",
            task_id="task-123",
            task_data={}
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_assign_task_agent_busy(self):
        """Test assigning task to busy agent."""
        agent = MockAgent(
            agent_id="agent-1",
            status=AgentStatus.BUSY,
            current_task="existing-task"
        )
        self.mock_agents = [agent]

        result = await self.service.assign_task(
            agent_id="agent-1",
            task_id="task-123",
            task_data={}
        )

        assert result is False
        # Task should not be changed
        assert agent.current_task == "existing-task"

    @pytest.mark.asyncio
    async def test_release_agent_success(self):
        """Test releasing an agent successfully."""
        agent = MockAgent(
            agent_id="agent-1",
            status=AgentStatus.BUSY,
            current_task="task-123"
        )
        self.mock_agents = [agent]

        result = await self.service.release_agent("agent-1")

        assert result is True
        assert agent.current_task is None
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_release_agent_not_found(self):
        """Test releasing a nonexistent agent."""
        self.mock_agents = []
        result = await self.service.release_agent("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_agent_activity(self):
        """Test getting agent activity."""
        activity = await self.service.get_agent_activity()

        assert isinstance(activity, list)
        # Returns mock data
        assert len(activity) == 1
        assert activity[0]["id"] == "act-001"
        assert activity[0]["agent_name"] == "CEO Agent"


class TestAgentServiceInit:
    """Tests for AgentService initialization."""

    def test_init_creates_registry(self):
        """Test that initialization creates agent registry."""
        service = AgentService()

        assert service._registry is not None
        assert service._logger is not None


class TestAgentStatusEnum:
    """Tests for AgentStatus enum used by service."""

    def test_idle_status(self):
        """Test IDLE status value."""
        assert AgentStatus.IDLE.value == "idle"

    def test_busy_status(self):
        """Test BUSY status value."""
        assert AgentStatus.BUSY.value == "busy"

    def test_offline_status(self):
        """Test OFFLINE status value."""
        assert AgentStatus.OFFLINE.value == "offline"

    def test_error_status(self):
        """Test ERROR status value."""
        assert AgentStatus.ERROR.value == "error"
