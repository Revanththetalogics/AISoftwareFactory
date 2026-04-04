"""
Tests for Brain components.
"""

from unittest.mock import AsyncMock, Mock

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

        ids = await store.add(texts=["test1", "test2"], embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        assert len(ids) == 2
        assert store.get_count() == 2

    @pytest.mark.asyncio
    async def test_search_vectors(self):
        """Test searching vectors."""
        store = VectorStore()

        await store.add(texts=["hello world", "goodbye world"], embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

        results = await store.search(query_embedding=[1.0, 0.0, 0.0], top_k=1)

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

        memory_id = store.store(agent_id="agent1", content="Important fact", memory_type="fact")

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


class TestVectorStoreAdditional:
    """Additional tests for VectorStore to achieve full coverage."""

    @pytest.mark.asyncio
    async def test_search_with_filter_no_match(self):
        """Test search with filter that doesn't match (lines 96-100)."""
        store = VectorStore()

        await store.add(texts=["hello world"], embeddings=[[1.0, 0.0, 0.0]], metadatas=[{"category": "greeting"}])

        results = await store.search(
            query_embedding=[1.0, 0.0, 0.0],
            top_k=5,
            filter_metadata={"category": "farewell"},  # Doesn't match
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_delete_vectors(self):
        """Test deleting vectors (lines 129-141)."""
        store = VectorStore()

        ids = await store.add(texts=["text1", "text2", "text3"], embeddings=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])

        assert store.get_count() == 3

        deleted = await store.delete([ids[0], ids[1]])

        assert deleted == 2
        assert store.get_count() == 1

    @pytest.mark.asyncio
    async def test_delete_nonexistent_vectors(self):
        """Test deleting nonexistent vectors."""
        store = VectorStore()

        deleted = await store.delete(["nonexistent-1", "nonexistent-2"])

        assert deleted == 0

    @pytest.mark.asyncio
    async def test_delete_partial_match(self):
        """Test deleting mix of existing and nonexistent vectors."""
        store = VectorStore()

        ids = await store.add(texts=["text1"], embeddings=[[0.1, 0.2]])

        deleted = await store.delete([ids[0], "nonexistent"])

        assert deleted == 1

    def test_cosine_similarity_zero_norm(self):
        """Test cosine similarity with zero norm vectors (line 157)."""
        store = VectorStore()

        # Zero vector should return 0.0
        result = store._cosine_similarity([0.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        assert result == 0.0

        result = store._cosine_similarity([1.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        assert result == 0.0


class TestRetrievalEngine:
    """Test cases for RetrievalEngine."""

    @pytest.fixture
    def mock_knowledge_base(self):
        """Create a mock knowledge base."""
        kb = Mock()
        kb._name = "test_kb"
        kb.search = AsyncMock(
            return_value=[
                {"text": "relevant document", "score": 0.9, "metadata": {"source": "test"}},
                {"text": "another document", "score": 0.7, "metadata": {"source": "test2"}},
            ]
        )
        return kb

    def test_init(self, mock_knowledge_base):
        """Test RetrievalEngine initialization (lines 41-42)."""
        from backend.brain.retrieval import RetrievalEngine

        engine = RetrievalEngine(knowledge_base=mock_knowledge_base)

        assert engine._knowledge_base == mock_knowledge_base

    @pytest.mark.asyncio
    async def test_retrieve(self, mock_knowledge_base):
        """Test retrieve method (lines 64-90)."""
        from backend.brain.retrieval import RetrievalEngine

        engine = RetrievalEngine(knowledge_base=mock_knowledge_base)

        results = await engine.retrieve(query="test query", top_k=2, vector_weight=0.7, keyword_weight=0.3)

        assert len(results) <= 2
        # Results should be sorted by combined score
        if len(results) > 1:
            assert results[0].score >= results[1].score

        # Check that knowledge base search was called
        mock_knowledge_base.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_with_keyword_match(self, mock_knowledge_base):
        """Test retrieve combines vector and keyword scores."""
        from backend.brain.retrieval import RetrievalEngine

        # Set up search results with text that matches keywords
        mock_knowledge_base.search = AsyncMock(
            return_value=[
                {"text": "test query document", "score": 0.5, "metadata": {}},
                {"text": "unrelated content", "score": 0.9, "metadata": {}},
            ]
        )

        engine = RetrievalEngine(knowledge_base=mock_knowledge_base)

        results = await engine.retrieve(query="test query", top_k=2, vector_weight=0.5, keyword_weight=0.5)

        # The document with keyword match should be boosted
        assert len(results) > 0

    def test_keyword_match(self, mock_knowledge_base):
        """Test _keyword_match method (lines 103-110)."""
        from backend.brain.retrieval import RetrievalEngine

        engine = RetrievalEngine(knowledge_base=mock_knowledge_base)

        # Full match
        score = engine._keyword_match("hello world", "hello world greeting")
        assert score == 1.0  # Both query words found

        # Partial match
        score = engine._keyword_match("hello world", "hello there")
        assert score == 0.5  # 1 out of 2 words found

        # No match
        score = engine._keyword_match("hello world", "goodbye everyone")
        assert score == 0.0

        # Empty query
        score = engine._keyword_match("", "some text")
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_retrieve_with_context(self, mock_knowledge_base):
        """Test retrieve_with_context method (lines 129-143)."""
        from backend.brain.retrieval import RetrievalEngine

        engine = RetrievalEngine(knowledge_base=mock_knowledge_base)

        results = await engine.retrieve_with_context(query="test query", context_window=2, top_k=2)

        assert len(results) <= 2
        for item in results:
            assert "text" in item
            assert "score" in item
            assert "metadata" in item
            assert "context_before" in item
            assert "context_after" in item
            assert isinstance(item["context_before"], list)
            assert isinstance(item["context_after"], list)
