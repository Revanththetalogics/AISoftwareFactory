"""
Base Agent class for AI Software Factory.

This module provides the abstract base class that all agents must inherit from,
defining the common interface and functionality for agent operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.logging import get_logger, get_correlation_id

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentIdentity:
    """
    Identity information for an agent.
    
    Attributes:
        agent_id: Unique identifier for the agent
        name: Human-readable name
        role: Agent role (e.g., "CEO", "Product Manager")
        capabilities: List of capabilities this agent has
        description: Detailed description of the agent
    """
    agent_id: str
    name: str
    role: str
    capabilities: List[str] = field(default_factory=list)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert identity to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "capabilities": self.capabilities,
            "description": self.description,
        }


@dataclass
class Task:
    """
    Task definition for agent execution.
    
    Attributes:
        task_id: Unique identifier for the task
        task_type: Type of task (e.g., "analyze", "design", "implement")
        description: Task description
        context: Additional context for the task
        priority: Task priority (1-5, where 5 is highest)
        deadline: Optional deadline for task completion
        parent_task_id: Optional parent task ID for subtasks
    """
    task_id: str = field(default_factory=lambda: str(uuid4()))
    task_type: str = ""
    description: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 3
    deadline: Optional[datetime] = None
    parent_task_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "context": self.context,
            "priority": self.priority,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "parent_task_id": self.parent_task_id,
        }


@dataclass
class TaskResult:
    """
    Result of task execution.
    
    Attributes:
        task_id: ID of the task that was executed
        status: Execution status
        output: Task output data
        error: Error message if task failed
        execution_time_ms: Execution time in milliseconds
        metadata: Additional metadata about the execution
    """
    task_id: str
    status: TaskStatus
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all AI Software Factory agents.
    
    This class defines the common interface and functionality that all agents
    must implement. Agents are responsible for executing tasks within their
    domain of expertise.
    
    Attributes:
        identity: Agent identity information
        
    Example:
        >>> class MyAgent(BaseAgent):
        ...     async def execute_task(self, task: Task) -> TaskResult:
        ...         # Implementation
        ...         pass
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        role: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        description: str = "",
    ):
        """
        Initialize the agent.
        
        Args:
            agent_id: Unique identifier (generated if not provided)
            name: Human-readable name
            role: Agent role
            capabilities: List of capabilities
            description: Detailed description
        """
        self._identity = AgentIdentity(
            agent_id=agent_id or str(uuid4()),
            name=name or self.__class__.__name__,
            role=role or "Generic Agent",
            capabilities=capabilities or [],
            description=description,
        )
        self._logger = get_logger(f"{__name__}.{self._identity.agent_id}")
        self._logger.info(
            "Agent initialized",
            agent_id=self._identity.agent_id,
            name=self._identity.name,
            role=self._identity.role,
        )
    
    @property
    def identity(self) -> AgentIdentity:
        """Get agent identity."""
        return self._identity
    
    @property
    def agent_id(self) -> str:
        """Get agent ID."""
        return self._identity.agent_id
    
    @property
    def name(self) -> str:
        """Get agent name."""
        return self._identity.name
    
    @property
    def role(self) -> str:
        """Get agent role."""
        return self._identity.role
    
    @abstractmethod
    async def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a task.
        
        This method must be implemented by all agent subclasses.
        It contains the core logic for executing tasks within the agent's domain.
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult: Result of task execution
            
        Example:
            >>> task = Task(task_type="analyze", description="Analyze requirements")
            >>> result = await agent.execute_task(task)
            >>> print(result.status)
            'completed'
        """
        pass
    
    async def query_memory(self, query: str) -> Dict[str, Any]:
        """
        Query the project brain/memory system.
        
        This is a stub method that will be fully implemented in Phase 5
        when the Project Brain is built.
        
        Args:
            query: Query string
            
        Returns:
            Dictionary containing query results
            
        TODO: Implement full integration with Project Brain (Phase 5)
        """
        self._logger.debug("Querying memory", query=query)
        # Stub implementation - returns empty results
        return {
            "query": query,
            "results": [],
            "total": 0,
        }
    
    def has_capability(self, capability: str) -> bool:
        """
        Check if agent has a specific capability.
        
        Args:
            capability: Capability to check
            
        Returns:
            True if agent has the capability
        """
        return capability in self._identity.capabilities
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to dictionary representation.
        
        Returns:
            Dictionary containing agent information
        """
        return {
            "identity": self._identity.to_dict(),
            "type": self.__class__.__name__,
        }
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<{self.__class__.__name__} {self._identity.name} ({self._identity.agent_id})>"
