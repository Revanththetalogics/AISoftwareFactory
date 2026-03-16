"""
Tests for BaseAgent class.
"""

import pytest

from backend.agents.base_agent import (
    AgentIdentity,
    BaseAgent,
    Task,
    TaskResult,
    TaskStatus,
)


class TestAgentIdentity:
    """Test cases for AgentIdentity."""
    
    def test_identity_creation(self):
        """Test creating an agent identity."""
        identity = AgentIdentity(
            agent_id="test-123",
            name="Test Agent",
            role="Tester",
            capabilities=["testing", "debugging"],
            description="A test agent",
        )
        
        assert identity.agent_id == "test-123"
        assert identity.name == "Test Agent"
        assert identity.role == "Tester"
        assert identity.capabilities == ["testing", "debugging"]
        assert identity.description == "A test agent"
    
    def test_identity_to_dict(self):
        """Test converting identity to dictionary."""
        identity = AgentIdentity(
            agent_id="test-123",
            name="Test Agent",
            role="Tester",
        )
        
        result = identity.to_dict()
        
        assert result["agent_id"] == "test-123"
        assert result["name"] == "Test Agent"
        assert result["role"] == "Tester"


class TestTask:
    """Test cases for Task."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            task_type="test",
            description="Test task",
            context={"key": "value"},
            priority=5,
        )
        
        assert task.task_type == "test"
        assert task.description == "Test task"
        assert task.context == {"key": "value"}
        assert task.priority == 5
        assert task.task_id is not None
    
    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(task_type="test", description="Test task")
        
        result = task.to_dict()
        
        assert result["task_type"] == "test"
        assert result["description"] == "Test task"


class TestTaskResult:
    """Test cases for TaskResult."""
    
    def test_result_creation(self):
        """Test creating a task result."""
        result = TaskResult(
            task_id="task-123",
            status=TaskStatus.COMPLETED,
            output={"result": "success"},
            execution_time_ms=100.0,
        )
        
        assert result.task_id == "task-123"
        assert result.status == TaskStatus.COMPLETED
        assert result.output == {"result": "success"}
        assert result.execution_time_ms == 100.0
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = TaskResult(
            task_id="task-123",
            status=TaskStatus.COMPLETED,
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["task_id"] == "task-123"
        assert result_dict["status"] == "completed"


class ConcreteTestAgent(BaseAgent):
    """Concrete implementation for testing."""
    
    async def execute_task(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output={"processed": task.description},
        )


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = ConcreteTestAgent(
            agent_id="agent-123",
            name="Test Agent",
            role="Tester",
            capabilities=["testing"],
        )
        
        assert agent.agent_id == "agent-123"
        assert agent.name == "Test Agent"
        assert agent.role == "Tester"
        assert agent.has_capability("testing")
    
    def test_agent_auto_id_generation(self):
        """Test that agent ID is auto-generated if not provided."""
        agent = ConcreteTestAgent()
        
        assert agent.agent_id is not None
        assert len(agent.agent_id) > 0
    
    def test_has_capability(self):
        """Test capability checking."""
        agent = ConcreteTestAgent(capabilities=["testing", "debugging"])
        
        assert agent.has_capability("testing") is True
        assert agent.has_capability("debugging") is True
        assert agent.has_capability("unknown") is False
    
    def test_to_dict(self):
        """Test converting agent to dictionary."""
        agent = ConcreteTestAgent(
            agent_id="agent-123",
            name="Test Agent",
            role="Tester",
        )
        
        result = agent.to_dict()
        
        assert result["identity"]["agent_id"] == "agent-123"
        assert result["identity"]["name"] == "Test Agent"
        assert result["type"] == "ConcreteTestAgent"
    
    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test task execution."""
        agent = ConcreteTestAgent()
        task = Task(task_type="test", description="Test task")
        
        result = await agent.execute_task(task)
        
        assert result.status == TaskStatus.COMPLETED
        assert result.output["processed"] == "Test task"
    
    @pytest.mark.asyncio
    async def test_query_memory_stub(self):
        """Test memory query stub."""
        agent = ConcreteTestAgent()
        
        result = await agent.query_memory("test query")
        
        assert result["query"] == "test query"
        assert result["results"] == []
        assert result["total"] == 0
