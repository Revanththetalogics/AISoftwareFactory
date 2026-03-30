"""
Comprehensive tests for Brain modules to increase coverage.
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from backend.brain.context_manager import ContextManager, Conversation, Message
from backend.brain.embeddings import EmbeddingEngine
from backend.brain.knowledge_base import KnowledgeBase
from backend.brain.memory_store import MemoryStore
from backend.brain.retrieval import RetrievalEngine, RetrievalResult


class TestMessageDataclass:
    """Tests for Message dataclass."""

    def test_create_message_basic(self):
        """Test creating a basic message."""
        msg = Message(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.metadata == {}
        assert isinstance(msg.timestamp, datetime)

    def test_create_message_with_metadata(self):
        """Test creating a message with metadata."""
        msg = Message(
            role="assistant",
            content="Hi there!",
            metadata={"source": "gpt-4", "tokens": 10}
        )

        assert msg.role == "assistant"
        assert msg.content == "Hi there!"
        assert len(msg.metadata) == 2
        assert msg.metadata["source"] == "gpt-4"

    def test_message_timestamp_default(self):
        """Test message timestamp is set automatically."""
        before = datetime.utcnow()
        msg = Message(role="system", content="System message")
        after = datetime.utcnow()

        assert before <= msg.timestamp <= after


class TestConversationDataclass:
    """Tests for Conversation dataclass."""

    def test_create_conversation_basic(self):
        """Test creating a basic conversation."""
        conv = Conversation(conversation_id="conv_001")

        assert conv.conversation_id == "conv_001"
        assert conv.messages == []
        assert conv.metadata == {}
        assert isinstance(conv.created_at, datetime)

    def test_create_conversation_with_messages(self):
        """Test creating a conversation with initial messages."""
        msg = Message(role="user", content="Test")
        conv = Conversation(
            conversation_id="conv_002",
            messages=[msg],
            metadata={"topic": "testing"}
        )

        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Test"
        assert conv.metadata["topic"] == "testing"


class TestContextManager:
    """Comprehensive tests for ContextManager."""

    @pytest.fixture
    def context_manager(self):
        """Create ContextManager instance."""
        return ContextManager(max_tokens=1000)

    def test_init(self, context_manager):
        """Test ContextManager initialization."""
        assert context_manager._max_tokens == 1000
        assert isinstance(context_manager._conversations, dict)
        assert len(context_manager._conversations) == 0

    def test_create_conversation_auto_id(self, context_manager):
        """Test creating conversation with auto-generated ID."""
        conv_id = context_manager.create_conversation()

        assert conv_id is not None
        assert len(conv_id) > 0
        assert conv_id in context_manager._conversations

    def test_create_conversation_custom_id(self, context_manager):
        """Test creating conversation with custom ID."""
        conv_id = context_manager.create_conversation(
            conversation_id="my_conv_123",
            metadata={"user": "test_user"}
        )

        assert conv_id == "my_conv_123"
        assert conv_id in context_manager._conversations
        assert context_manager._conversations[conv_id].metadata["user"] == "test_user"

    def test_add_message_success(self, context_manager):
        """Test adding message to conversation."""
        conv_id = context_manager.create_conversation()

        result = context_manager.add_message(
            conversation_id=conv_id,
            role="user",
            content="Hello, AI!",
            metadata={"sentiment": "positive"}
        )

        assert result is True
        assert len(context_manager._conversations[conv_id].messages) == 1
        assert context_manager._conversations[conv_id].messages[0].role == "user"
        assert context_manager._conversations[conv_id].messages[0].content == "Hello, AI!"

    def test_add_message_nonexistent_conversation(self, context_manager):
        """Test adding message to non-existent conversation."""
        result = context_manager.add_message(
            conversation_id="nonexistent",
            role="user",
            content="Test"
        )

        assert result is False

    def test_get_context_empty_conversation(self, context_manager):
        """Test getting context from empty conversation."""
        conv_id = context_manager.create_conversation()

        context = context_manager.get_context(conv_id)

        assert context == []

    def test_get_context_with_messages(self, context_manager):
        """Test getting context with messages."""
        conv_id = context_manager.create_conversation()
        context_manager.add_message(conv_id, "user", "Message 1")
        context_manager.add_message(conv_id, "assistant", "Response 1")

        context = context_manager.get_context(conv_id)

        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "Message 1"
        assert context[1]["role"] == "assistant"
        assert "timestamp" in context[1]

    def test_get_context_max_messages(self, context_manager):
        """Test getting context with max_messages limit."""
        conv_id = context_manager.create_conversation()

        for i in range(5):
            context_manager.add_message(conv_id, "user", f"Message {i}")

        context = context_manager.get_context(conv_id, max_messages=2)

        assert len(context) == 2
        assert context[0]["content"] == "Message 3"
        assert context[1]["content"] == "Message 4"

    def test_get_context_nonexistent_conversation(self, context_manager):
        """Test getting context from non-existent conversation."""
        context = context_manager.get_context("nonexistent")
        assert context == []

    def test_get_conversation_summary(self, context_manager):
        """Test getting conversation summary."""
        conv_id = context_manager.create_conversation()
        context_manager.add_message(conv_id, "user", "This is a test message about testing")
        context_manager.add_message(conv_id, "assistant", "Sure, I can help with that")

        summary = context_manager.get_conversation_summary(conv_id)

        assert summary is not None
        assert "Conversation about:" in summary
        assert "This is a test message" in summary
        assert "(2 messages)" in summary

    def test_get_conversation_summary_empty(self, context_manager):
        """Test getting summary of empty conversation."""
        conv_id = context_manager.create_conversation()

        summary = context_manager.get_conversation_summary(conv_id)

        assert summary == "Empty conversation"

    def test_get_conversation_summary_no_user_messages(self, context_manager):
        """Test getting summary with only assistant messages."""
        conv_id = context_manager.create_conversation()
        context_manager.add_message(conv_id, "assistant", "Hello")

        summary = context_manager.get_conversation_summary(conv_id)

        assert summary == "Empty conversation"

    def test_delete_conversation_success(self, context_manager):
        """Test deleting existing conversation."""
        conv_id = context_manager.create_conversation()

        result = context_manager.delete_conversation(conv_id)

        assert result is True
        assert conv_id not in context_manager._conversations

    def test_delete_conversation_not_found(self, context_manager):
        """Test deleting non-existent conversation."""
        result = context_manager.delete_conversation("nonexistent")
        assert result is False

    def test_context_window_management(self, context_manager):
        """Test automatic context window management."""
        # Create manager with small token limit
        small_manager = ContextManager(max_tokens=50)
        conv_id = small_manager.create_conversation()

        # Add multiple long messages
        for i in range(10):
            small_manager.add_message(conv_id, "user", f"This is a very long message number {i} with lots of text")

        # Should have removed old messages
        assert len(small_manager._conversations[conv_id].messages) < 10

    def test_multiple_conversations_isolated(self, context_manager):
        """Test that multiple conversations are isolated."""
        conv1 = context_manager.create_conversation()
        conv2 = context_manager.create_conversation()

        context_manager.add_message(conv1, "user", "Message for conv1")
        context_manager.add_message(conv2, "user", "Message for conv2")

        ctx1 = context_manager.get_context(conv1)
        ctx2 = context_manager.get_context(conv2)

        assert len(ctx1) == 1
        assert len(ctx2) == 1
        assert ctx1[0]["content"] == "Message for conv1"
        assert ctx2[0]["content"] == "Message for conv2"


class TestEmbeddingEngine:
    """Tests for EmbeddingEngine."""

    @pytest.fixture
    def embedding_engine(self):
        """Create EmbeddingEngine instance."""
        return EmbeddingEngine()

    def test_init(self, embedding_engine):
        """Test EmbeddingEngine initialization."""
        assert embedding_engine._model_name == "all-MiniLM-L6-v2"
        assert embedding_engine._model is None

    def test_compute_embedding_success(self, embedding_engine):
        """Test computing embeddings successfully."""
        # Mock the model
        mock_model = MagicMock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        embedding_engine._model = mock_model

        import asyncio
        result = asyncio.run(embedding_engine.embed(["Test text"]))

        assert len(result) == 1
        assert len(result[0]) == 5
        mock_model.encode.assert_called_once_with(["Test text"], convert_to_numpy=True)

    def test_get_dimension(self, embedding_engine):
        """Test getting embedding dimension."""
        dim = embedding_engine.get_dimension()
        assert dim == 384


class TestKnowledgeBase:
    """Tests for KnowledgeBase."""

    @pytest.fixture
    def knowledge_base(self):
        """Create KnowledgeBase instance."""
        return KnowledgeBase(name="test_kb")

    def test_init(self, knowledge_base):
        """Test KnowledgeBase initialization."""
        assert knowledge_base._name == "test_kb"
        assert len(knowledge_base._documents) == 0

    @pytest.mark.asyncio
    async def test_add_document_success(self, knowledge_base):
        """Test adding document successfully."""
        doc_id = await knowledge_base.add_document(
            content="Test content",
            metadata={"source": "test"},
            doc_id="doc1"
        )

        assert doc_id == "doc1"
        assert len(knowledge_base._documents) == 1
        assert "doc1" in knowledge_base._documents

    @pytest.mark.asyncio
    async def test_add_document_without_id(self, knowledge_base):
        """Test adding document without ID generates one."""
        doc_id = await knowledge_base.add_document(content="Test content")

        assert doc_id is not None
        assert len(doc_id) > 0
        assert len(knowledge_base._documents) == 1

    @pytest.mark.asyncio
    async def test_remove_document_success(self, knowledge_base):
        """Test removing document successfully."""
        await knowledge_base.add_document(content="Test", doc_id="doc_to_remove")

        result = await knowledge_base.remove_document("doc_to_remove")

        assert result is True
        assert len(knowledge_base._documents) == 0

    @pytest.mark.asyncio
    async def test_remove_document_not_found(self, knowledge_base):
        """Test removing non-existent document."""
        result = await knowledge_base.remove_document("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_document_success(self, knowledge_base):
        """Test getting document successfully."""
        await knowledge_base.add_document(content="Get me", doc_id="doc_get")

        result = await knowledge_base.get_document("doc_get")

        assert result is not None
        assert result["id"] == "doc_get"

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, knowledge_base):
        """Test getting non-existent document."""
        result = await knowledge_base.get_document("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_search_documents(self, knowledge_base):
        """Test searching documents."""
        await knowledge_base.add_document(content="Python programming", doc_id="py")
        await knowledge_base.add_document(content="Java development", doc_id="java")

        results = await knowledge_base.search("Python", top_k=1)

        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_get_statistics(self, knowledge_base):
        """Test getting knowledge base statistics."""
        await knowledge_base.add_document(content="Doc 1", doc_id="d1")
        await knowledge_base.add_document(content="Doc 2", doc_id="d2")

        stats = await knowledge_base.get_statistics()

        assert isinstance(stats, dict)
        assert stats["document_count"] == 2


class TestMemoryStore:
    """Tests for MemoryStore."""

    @pytest.fixture
    def memory_store(self):
        """Create MemoryStore instance."""
        return MemoryStore()

    def test_init(self, memory_store):
        """Test MemoryStore initialization."""
        assert len(memory_store._memories) == 0
        assert len(memory_store._agent_memories) == 0

    def test_store_memory_success(self, memory_store):
        """Test storing memory successfully."""
        memory_id = memory_store.store(
            agent_id="agent_001",
            content="Paris is capital of France",
            memory_type="fact",
            importance=0.9
        )

        assert memory_id is not None
        assert len(memory_store._memories) == 1
        assert memory_id in memory_store._memories
        assert memory_store._memories[memory_id].content == "Paris is capital of France"

    def test_recall_memory_success(self, memory_store):
        """Test recalling memory successfully."""
        memory_store.store(
            agent_id="agent_002",
            content="Water boils at 100C",
            memory_type="fact"
        )

        # Use retrieve method instead of recall
        results = memory_store.retrieve(agent_id="agent_002")

        assert len(results) > 0
        assert any(m.content == "Water boils at 100C" for m in results)

    def test_recall_memory_not_found(self, memory_store):
        """Test recalling non-existent memory."""
        results = memory_store.retrieve(agent_id="nonexistent")
        assert results == []

    def test_forget_memory_success(self, memory_store):
        """Test forgetting memory successfully."""
        memory_id = memory_store.store(
            agent_id="agent_003",
            content="Forget me",
            memory_type="fact"
        )

        result = memory_store.forget(memory_id)

        assert result is True
        assert memory_id not in memory_store._memories

    def test_clear_all_memories(self, memory_store):
        """Test clearing all memories."""
        memory_store.store(agent_id="agent_004", content="Mem1")
        memory_store.store(agent_id="agent_004", content="Mem2")

        # Delete memories one by one (no clear_all method)
        memory_ids = list(memory_store._memories.keys())
        for mid in memory_ids:
            memory_store.forget(mid)

        assert len(memory_store._memories) == 0

    def test_get_agent_memories(self, memory_store):
        """Test getting memories by agent."""
        memory_store.store(agent_id="agent_005", content="Fact1", memory_type="fact")
        memory_store.store(agent_id="agent_005", content="Pref1", memory_type="preference")

        # Get all memories for agent
        memories = memory_store.retrieve(agent_id="agent_005")

        assert len(memories) == 2

        # Filter by type
        facts = memory_store.retrieve(agent_id="agent_005", memory_type="fact")
        assert len(facts) == 1
        assert facts[0].memory_type == "fact"


class TestRetrievalEngine:
    """Tests for RetrievalEngine."""

    @pytest.fixture
    def retrieval_engine(self):
        """Create RetrievalEngine instance with mock knowledge base."""
        # Create a minimal mock KB
        class MockKB:
            _name = "mock_kb"
            async def search(self, query, top_k):
                return [
                    {"text": f"Result about {query}", "score": 0.9, "metadata": {}},
                    {"text": "Another result", "score": 0.7, "metadata": {}}
                ]

        mock_kb = MockKB()
        return RetrievalEngine(knowledge_base=mock_kb)

    @pytest.mark.asyncio
    async def test_retrieve_success(self, retrieval_engine):
        """Test retrieving documents successfully."""
        results = await retrieval_engine.retrieve(query="test query", top_k=3)

        assert len(results) > 0
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert all(hasattr(r, 'text') for r in results)
        assert all(hasattr(r, 'score') for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_with_context(self, retrieval_engine):
        """Test retrieving documents with context."""
        results = await retrieval_engine.retrieve_with_context(
            query="test",
            context_window=2,
            top_k=2
        )

        assert len(results) > 0
        assert "text" in results[0]
        assert "score" in results[0]
        assert "context_before" in results[0]
        assert "context_after" in results[0]

    @pytest.mark.asyncio
    async def test_retrieve_respects_top_k(self, retrieval_engine):
        """Test that retrieve respects top_k parameter."""
        results = await retrieval_engine.retrieve(query="test", top_k=1)

        assert len(results) <= 1

    @pytest.mark.asyncio
    async def test_keyword_match_internal(self, retrieval_engine):
        """Test internal keyword matching (via retrieve)."""
        # The keyword matching is tested indirectly through retrieve
        results = await retrieval_engine.retrieve(query="python programming")

        # Should have combined scores
        assert len(results) > 0
        assert all(0 <= r.score <= 1 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
