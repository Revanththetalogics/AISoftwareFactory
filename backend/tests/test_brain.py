"""
Tests for Brain components.
"""

import pytest

from backend.brain.context_manager import ContextManager
from backend.brain.memory_store import MemoryStore
from backend.brain.vector_store import VectorStore


class TestVectorStore:
    """Tests for VectorStore."""

    @pytest.mark.asyncio
    async def test_add_vectors(self):
        """Test adding vectors."""
        store = VectorStore()

        ids = await store.add(
            texts=["test1", "test2"],
            embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        )

        assert len(ids) == 2
        assert store.get_count() == 2

    @pytest.mark.asyncio
    async def test_search_vectors(self):
        """Test searching vectors."""
        store = VectorStore()

        await store.add(
            texts=["hello world", "goodbye world"],
            embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        )

        results = await store.search(
            query_embedding=[1.0, 0.0, 0.0],
            top_k=1
        )

        assert len(results) == 1
        assert results[0]["text"] == "hello world"


class TestContextManager:
    """Tests for ContextManager."""

    def test_create_conversation(self):
        """Test creating a conversation."""
        manager = ContextManager()

        conv_id = manager.create_conversation()

        assert conv_id is not None

    def test_add_message(self):
        """Test adding a message."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        result = manager.add_message(conv_id, "user", "Hello")

        assert result is True

        context = manager.get_context(conv_id)
        assert len(context) == 1
        assert context[0]["role"] == "user"

    def test_get_conversation_summary(self):
        """Test getting conversation summary."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        manager.add_message(conv_id, "user", "This is a test message")

        summary = manager.get_conversation_summary(conv_id)

        assert summary is not None
        assert "test message" in summary


class TestMemoryStore:
    """Tests for MemoryStore."""

    def test_store_memory(self):
        """Test storing a memory."""
        store = MemoryStore()

        memory_id = store.store(
            agent_id="agent1",
            content="Important fact",
            memory_type="fact"
        )

        assert memory_id is not None

    def test_retrieve_memories(self):
        """Test retrieving memories."""
        store = MemoryStore()

        store.store(agent_id="agent1", content="Fact 1", memory_type="fact")
        store.store(agent_id="agent1", content="Fact 2", memory_type="fact")

        memories = store.retrieve(agent_id="agent1")

        assert len(memories) == 2

    def test_forget_memory(self):
        """Test forgetting a memory."""
        store = MemoryStore()

        memory_id = store.store(agent_id="agent1", content="To be forgotten")

        result = store.forget(memory_id)

        assert result is True

        memories = store.retrieve(agent_id="agent1")
        assert len(memories) == 0
