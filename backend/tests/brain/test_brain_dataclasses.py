"""
Dataclass and helper tests to increase coverage.
"""

import pytest


class TestBrainRetrievalResult:
    """Tests for RetrievalResult dataclass."""

    def test_retrieval_result_creation(self):
        """Test creating RetrievalResult instance."""
        from backend.brain.retrieval import RetrievalResult

        result = RetrievalResult(text="test text", score=0.95, metadata={"source": "test"})

        assert result.text == "test text"
        assert result.score == 0.95
        assert result.metadata == {"source": "test"}

    def test_retrieval_result_default_metadata(self):
        """Test RetrievalResult with default metadata."""
        from backend.brain.retrieval import RetrievalResult

        result = RetrievalResult(text="test", score=0.9)

        assert result.metadata == {}


class TestBrainMemoryDataclass:
    """Tests for Memory dataclass."""

    def test_memory_creation(self):
        """Test creating Memory instance."""
        from backend.brain.memory_store import Memory

        memory = Memory(
            memory_id="mem_123", agent_id="agent_001", content="Test memory", memory_type="fact", importance=0.8
        )

        assert memory.memory_id == "mem_123"
        assert memory.agent_id == "agent_001"
        assert memory.content == "Test memory"
        assert memory.memory_type == "fact"
        assert memory.importance == 0.8

    def test_memory_default_importance(self):
        """Test Memory with default importance."""
        from backend.brain.memory_store import Memory

        memory = Memory(memory_id="mem_456", agent_id="agent_002", content="Another memory", memory_type="preference")

        assert memory.importance == 1.0


class TestBrainConversationDataclass:
    """Tests for Conversation dataclass."""

    def test_conversation_creation(self):
        """Test creating Conversation instance."""
        from backend.brain.context_manager import Conversation

        conv = Conversation(conversation_id="conv_123")

        assert conv.conversation_id == "conv_123"
        assert conv.messages == []
        assert conv.metadata == {}

    def test_conversation_with_metadata(self):
        """Test Conversation with custom metadata."""
        from backend.brain.context_manager import Conversation

        conv = Conversation(conversation_id="conv_456", metadata={"user_id": "user_123"})

        assert conv.metadata == {"user_id": "user_123"}


class TestBrainMessageDataclass:
    """Tests for Message dataclass."""

    def test_message_creation(self):
        """Test creating Message instance."""
        from backend.brain.context_manager import Message

        msg = Message(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_message_with_metadata(self):
        """Test Message with custom metadata."""
        from backend.brain.context_manager import Message

        msg = Message(role="assistant", content="Hi there!", metadata={"timestamp_extra": "extra_info"})

        assert msg.metadata == {"timestamp_extra": "extra_info"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
