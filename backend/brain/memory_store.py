"""
Memory store for Brain module.

This module provides agent memory persistence for maintaining state
across sessions and interactions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Memory:
    """A memory item."""
    memory_id: str
    agent_id: str
    content: str
    memory_type: str  # fact, experience, preference
    importance: float = 1.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class MemoryStore:
    """
    Memory store for agent memory persistence.
    
    Provides storage and retrieval of agent memories with
    importance weighting and decay.
    """
    
    def __init__(self):
        """Initialize the memory store."""
        self._memories: Dict[str, Memory] = {}
        self._agent_memories: Dict[str, List[str]] = {}  # agent_id -> memory_ids
        self._logger = get_logger(__name__)
    
    def store(
        self,
        agent_id: str,
        content: str,
        memory_type: str = "fact",
        importance: float = 1.0
    ) -> str:
        """
        Store a memory.
        
        Args:
            agent_id: Agent ID
            content: Memory content
            memory_type: Type of memory
            importance: Importance score (0-1)
            
        Returns:
            Memory ID
        """
        memory_id = str(uuid4())
        
        memory = Memory(
            memory_id=memory_id,
            agent_id=agent_id,
            content=content,
            memory_type=memory_type,
            importance=importance
        )
        
        self._memories[memory_id] = memory
        
        # Index by agent
        if agent_id not in self._agent_memories:
            self._agent_memories[agent_id] = []
        self._agent_memories[agent_id].append(memory_id)
        
        self._logger.info(
            "Memory stored",
            memory_id=memory_id,
            agent_id=agent_id,
            type=memory_type
        )
        
        return memory_id
    
    def retrieve(
        self,
        agent_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Memory]:
        """
        Retrieve memories for an agent.
        
        Args:
            agent_id: Agent ID
            query: Optional content filter
            memory_type: Optional type filter
            limit: Maximum memories to return
            
        Returns:
            List of memories
        """
        if agent_id not in self._agent_memories:
            return []
        
        memory_ids = self._agent_memories[agent_id]
        memories = [self._memories[mid] for mid in memory_ids]
        
        # Apply filters
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        if query:
            query_lower = query.lower()
            memories = [
                m for m in memories 
                if query_lower in m.content.lower()
            ]
        
        # Sort by importance and recency
        memories.sort(
            key=lambda m: (m.importance, m.created_at),
            reverse=True
        )
        
        # Update access stats
        for memory in memories[:limit]:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()
        
        return memories[:limit]
    
    def forget(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            True if deleted, False if not found
        """
        if memory_id not in self._memories:
            return False
        
        memory = self._memories[memory_id]
        
        # Remove from agent index
        if memory.agent_id in self._agent_memories:
            self._agent_memories[memory.agent_id].remove(memory_id)
        
        # Remove memory
        del self._memories[memory_id]
        
        self._logger.info("Memory forgotten", memory_id=memory_id)
        return True
    
    def get_agent_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Memory statistics
        """
        if agent_id not in self._agent_memories:
            return {"total": 0, "by_type": {}}
        
        memory_ids = self._agent_memories[agent_id]
        memories = [self._memories[mid] for mid in memory_ids]
        
        by_type = {}
        for memory in memories:
            by_type[memory.memory_type] = by_type.get(memory.memory_type, 0) + 1
        
        return {
            "total": len(memories),
            "by_type": by_type
        }
