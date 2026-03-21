"""
Comprehensive tests for Brain components to achieve 100% coverage.

Covers:
- EmbeddingEngine (lines 36-39, 43-45, 57-60, 64-82, 86-105, 109-114)
- RAGPipeline (lines 41-45, 67-120, 135-159, 163)
- KnowledgeBase (lines 41-45, 68-111, 131-140, 152-164, 173-182, 186)
- MemoryStore (lines 110, 117, 120-121, 150, 174-184)
- ContextManager (lines 106, 139, 145, 167, 175, 190-194, 204-208)
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from backend.brain.context_manager import ContextManager, Conversation, Message
from backend.brain.memory_store import Memory, MemoryStore


class TestEmbeddingEngineFull:
    """Comprehensive tests for EmbeddingEngine."""

    def test_init_default_provider(self):
        """Test initialization with default provider."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine()
        assert engine._provider == "local"
        assert engine._model_name == "all-MiniLM-L6-v2"
        assert engine._model is None

    def test_init_openai_provider(self):
        """Test initialization with OpenAI provider."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="openai")
        assert engine._provider == "openai"
        assert engine._model_name == "text-embedding-3-small"

    def test_init_custom_model(self):
        """Test initialization with custom model name."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="local", model_name="custom-model")
        assert engine._model_name == "custom-model"

    def test_get_default_model_local(self):
        """Test getting default model for local provider."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="local")
        # Force call _get_default_model by not passing model_name
        assert engine._model_name == "all-MiniLM-L6-v2"

    def test_get_default_model_openai(self):
        """Test getting default model for OpenAI provider."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="openai")
        assert engine._model_name == "text-embedding-3-small"

    @pytest.mark.asyncio
    async def test_embed_routes_to_openai(self):
        """Test embed routes to OpenAI for openai provider."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="openai")

        with patch.object(engine, '_embed_openai', new_callable=AsyncMock) as mock:
            mock.return_value = [[0.1, 0.2, 0.3]]
            await engine.embed(["test"])
            mock.assert_called_once_with(["test"])

    @pytest.mark.asyncio
    async def test_embed_routes_to_local(self):
        """Test embed routes to local for local provider."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="local")

        with patch.object(engine, '_embed_local', new_callable=AsyncMock) as mock:
            mock.return_value = [[0.1, 0.2, 0.3]]
            await engine.embed(["test"])
            mock.assert_called_once_with(["test"])

    @pytest.mark.asyncio
    async def test_embed_local_success(self):
        """Test local embedding generation."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="local")

        # Mock the import inside the method
        import sys

        import numpy as np

        mock_model = Mock()
        mock_model.encode = Mock(return_value=np.array([[0.1, 0.2], [0.3, 0.4]]))

        mock_st_module = Mock()
        mock_st_module.SentenceTransformer = Mock(return_value=mock_model)

        with patch.dict(sys.modules, {'sentence_transformers': mock_st_module}):
            result = await engine._embed_local(["text1", "text2"])

            assert len(result) == 2
            assert result[0] == [0.1, 0.2]

    @pytest.mark.asyncio
    async def test_embed_local_import_error(self):
        """Test local embedding handles import error."""
        import sys

        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="local")

        # Simulate ImportError by removing the module
        with patch.dict(sys.modules, {'sentence_transformers': None}):
            with pytest.raises(ImportError):
                await engine._embed_local(["text"])

    @pytest.mark.asyncio
    async def test_embed_local_model_caching(self):
        """Test that local model is cached after first load."""
        import sys

        import numpy as np

        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="local")

        mock_model = Mock()
        mock_model.encode = Mock(return_value=np.array([[0.1, 0.2]]))

        mock_st_class = Mock(return_value=mock_model)
        mock_st_module = Mock()
        mock_st_module.SentenceTransformer = mock_st_class

        with patch.dict(sys.modules, {'sentence_transformers': mock_st_module}):
            await engine._embed_local(["text1"])
            await engine._embed_local(["text2"])

            # SentenceTransformer should only be called once
            assert mock_st_class.call_count == 1

    @pytest.mark.asyncio
    async def test_embed_openai_success(self):
        """Test OpenAI embedding generation."""
        import sys

        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="openai")

        mock_client = AsyncMock()
        mock_response = Mock()
        mock_item = Mock()
        mock_item.embedding = [0.1, 0.2, 0.3]
        mock_response.data = [mock_item]
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        mock_openai_module = Mock()
        mock_openai_module.AsyncOpenAI = Mock(return_value=mock_client)

        with patch.dict(sys.modules, {'openai': mock_openai_module}):
            result = await engine._embed_openai(["test text"])

            assert result == [[0.1, 0.2, 0.3]]

    @pytest.mark.asyncio
    async def test_embed_openai_import_error(self):
        """Test OpenAI embedding handles import error."""
        import sys

        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(provider="openai")

        with patch.dict(sys.modules, {'openai': None}):
            with pytest.raises(ImportError):
                await engine._embed_openai(["text"])

    def test_get_dimension_minilm(self):
        """Test getting dimension for MiniLM model."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2")
        assert engine.get_dimension() == 384

    def test_get_dimension_openai_small(self):
        """Test getting dimension for OpenAI small model."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(
            provider="openai",
            model_name="text-embedding-3-small"
        )
        assert engine.get_dimension() == 1536

    def test_get_dimension_openai_large(self):
        """Test getting dimension for OpenAI large model."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(
            provider="openai",
            model_name="text-embedding-3-large"
        )
        assert engine.get_dimension() == 3072

    def test_get_dimension_unknown_model(self):
        """Test getting dimension for unknown model defaults to 384."""
        from backend.brain.embeddings import EmbeddingEngine

        engine = EmbeddingEngine(model_name="unknown-model")
        assert engine.get_dimension() == 384


class TestRAGPipelineFull:
    """Comprehensive tests for RAGPipeline."""

    @pytest.fixture
    def mock_knowledge_base(self):
        """Create a mock knowledge base."""
        kb = Mock()
        kb._name = "test_kb"
        return kb

    @pytest.fixture
    def mock_context_manager(self):
        """Create a mock context manager."""
        return Mock()

    def test_init_with_defaults(self, mock_knowledge_base):
        """Test initialization with defaults."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine'):
            with patch('backend.brain.rag_pipeline.ContextManager'):
                with patch('backend.brain.rag_pipeline.LLMFactory'):
                    from backend.brain.rag_pipeline import RAGPipeline

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)
                    assert pipeline._knowledge_base == mock_knowledge_base

    def test_init_with_custom_context_manager(self, mock_knowledge_base, mock_context_manager):
        """Test initialization with custom context manager."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine'):
            with patch('backend.brain.rag_pipeline.LLMFactory'):
                from backend.brain.rag_pipeline import RAGPipeline

                pipeline = RAGPipeline(
                    knowledge_base=mock_knowledge_base,
                    context_manager=mock_context_manager
                )
                assert pipeline._context == mock_context_manager

    @pytest.mark.asyncio
    async def test_query_success(self, mock_knowledge_base):
        """Test successful RAG query."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine') as mock_re:
            with patch('backend.brain.rag_pipeline.ContextManager') as mock_cm:
                with patch('backend.brain.rag_pipeline.LLMFactory') as mock_llm:
                    from backend.brain.rag_pipeline import RAGPipeline
                    from backend.brain.retrieval import RetrievalResult

                    # Setup mocks
                    mock_retrieval = Mock()
                    mock_result = RetrievalResult(
                        text="relevant text",
                        score=0.9,
                        metadata={"key": "value"},
                        source="test"
                    )
                    mock_retrieval.retrieve = AsyncMock(return_value=[mock_result])
                    mock_re.return_value = mock_retrieval

                    mock_context = Mock()
                    mock_context.create_conversation = Mock(return_value="conv-123")
                    mock_context.add_message = Mock(return_value=True)
                    mock_context.get_context = Mock(return_value=[])
                    mock_cm.return_value = mock_context

                    mock_llm_instance = Mock()
                    mock_llm_instance.generate = AsyncMock(return_value="Generated response")
                    mock_llm.create_llm.return_value = mock_llm_instance

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    result = await pipeline.query("What is this?")

                    assert result["success"] is True
                    assert result["response"] == "Generated response"
                    assert result["conversation_id"] == "conv-123"
                    assert len(result["retrieved_documents"]) == 1

    @pytest.mark.asyncio
    async def test_query_with_existing_conversation(self, mock_knowledge_base):
        """Test query with existing conversation ID."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine') as mock_re:
            with patch('backend.brain.rag_pipeline.ContextManager') as mock_cm:
                with patch('backend.brain.rag_pipeline.LLMFactory') as mock_llm:
                    from backend.brain.rag_pipeline import RAGPipeline

                    mock_retrieval = Mock()
                    mock_retrieval.retrieve = AsyncMock(return_value=[])
                    mock_re.return_value = mock_retrieval

                    mock_context = Mock()
                    mock_context.add_message = Mock(return_value=True)
                    mock_context.get_context = Mock(return_value=[])
                    mock_cm.return_value = mock_context

                    mock_llm_instance = Mock()
                    mock_llm_instance.generate = AsyncMock(return_value="Response")
                    mock_llm.create_llm.return_value = mock_llm_instance

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    result = await pipeline.query(
                        "Question?",
                        conversation_id="existing-conv-456"
                    )

                    assert result["conversation_id"] == "existing-conv-456"
                    mock_context.create_conversation.assert_not_called()

    @pytest.mark.asyncio
    async def test_query_with_system_prompt(self, mock_knowledge_base):
        """Test query with custom system prompt."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine') as mock_re:
            with patch('backend.brain.rag_pipeline.ContextManager') as mock_cm:
                with patch('backend.brain.rag_pipeline.LLMFactory') as mock_llm:
                    from backend.brain.rag_pipeline import RAGPipeline

                    mock_retrieval = Mock()
                    mock_retrieval.retrieve = AsyncMock(return_value=[])
                    mock_re.return_value = mock_retrieval

                    mock_context = Mock()
                    mock_context.create_conversation = Mock(return_value="conv")
                    mock_context.add_message = Mock(return_value=True)
                    mock_context.get_context = Mock(return_value=[])
                    mock_cm.return_value = mock_context

                    mock_llm_instance = Mock()
                    mock_llm_instance.generate = AsyncMock(return_value="Response")
                    mock_llm.create_llm.return_value = mock_llm_instance

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    await pipeline.query(
                        "Question?",
                        system_prompt="You are a helpful AI."
                    )

                    # Verify the prompt was built with custom system prompt
                    call_args = mock_llm_instance.generate.call_args[0][0]
                    assert "You are a helpful AI" in call_args

    @pytest.mark.asyncio
    async def test_query_llm_failure(self, mock_knowledge_base):
        """Test query handles LLM failure."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine') as mock_re:
            with patch('backend.brain.rag_pipeline.ContextManager') as mock_cm:
                with patch('backend.brain.rag_pipeline.LLMFactory') as mock_llm:
                    from backend.brain.rag_pipeline import RAGPipeline

                    mock_retrieval = Mock()
                    mock_retrieval.retrieve = AsyncMock(return_value=[])
                    mock_re.return_value = mock_retrieval

                    mock_context = Mock()
                    mock_context.create_conversation = Mock(return_value="conv")
                    mock_context.add_message = Mock(return_value=True)
                    mock_context.get_context = Mock(return_value=[])
                    mock_cm.return_value = mock_context

                    mock_llm_instance = Mock()
                    mock_llm_instance.generate = AsyncMock(
                        side_effect=Exception("LLM error")
                    )
                    mock_llm.create_llm.return_value = mock_llm_instance

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    result = await pipeline.query("Question?")

                    assert result["success"] is False
                    assert "LLM error" in result["error"]

    def test_build_prompt_with_history(self, mock_knowledge_base):
        """Test building prompt with conversation history."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine'):
            with patch('backend.brain.rag_pipeline.ContextManager'):
                with patch('backend.brain.rag_pipeline.LLMFactory'):
                    from backend.brain.rag_pipeline import RAGPipeline

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    history = [
                        {"role": "user", "content": "Hi"},
                        {"role": "assistant", "content": "Hello!"}
                    ]

                    prompt = pipeline._build_prompt(
                        query="How are you?",
                        context="Context text",
                        history=history
                    )

                    assert "Conversation History:" in prompt
                    assert "user: Hi" in prompt
                    assert "assistant: Hello!" in prompt

    def test_build_prompt_without_history(self, mock_knowledge_base):
        """Test building prompt without history."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine'):
            with patch('backend.brain.rag_pipeline.ContextManager'):
                with patch('backend.brain.rag_pipeline.LLMFactory'):
                    from backend.brain.rag_pipeline import RAGPipeline

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    prompt = pipeline._build_prompt(
                        query="Question?",
                        context="Context",
                        history=[]
                    )

                    assert "Conversation History:" not in prompt

    def test_get_conversation_history(self, mock_knowledge_base):
        """Test getting conversation history."""
        with patch('backend.brain.rag_pipeline.RetrievalEngine'):
            with patch('backend.brain.rag_pipeline.ContextManager') as mock_cm:
                with patch('backend.brain.rag_pipeline.LLMFactory'):
                    from backend.brain.rag_pipeline import RAGPipeline

                    mock_context = Mock()
                    mock_context.get_context = Mock(return_value=[
                        {"role": "user", "content": "test"}
                    ])
                    mock_cm.return_value = mock_context

                    pipeline = RAGPipeline(knowledge_base=mock_knowledge_base)

                    history = pipeline.get_conversation_history("conv-123")

                    assert len(history) == 1


class TestKnowledgeBaseFull:
    """Comprehensive tests for KnowledgeBase."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        store = Mock()
        store.add = AsyncMock(return_value=["chunk-1", "chunk-2"])
        store.search = AsyncMock(return_value=[
            {"id": "1", "text": "result", "metadata": {}, "score": 0.9}
        ])
        store.delete = AsyncMock(return_value=2)
        store.get_count = Mock(return_value=10)
        return store

    @pytest.fixture
    def mock_embedding_engine(self):
        """Create mock embedding engine."""
        engine = Mock()
        engine.embed = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        return engine

    def test_init_with_defaults(self):
        """Test initialization with defaults."""
        from backend.brain.knowledge_base import KnowledgeBase

        with patch('backend.brain.knowledge_base.VectorStore'):
            with patch('backend.brain.knowledge_base.EmbeddingEngine'):
                kb = KnowledgeBase(name="test_kb")
                assert kb._name == "test_kb"

    def test_init_with_custom_stores(self, mock_vector_store, mock_embedding_engine):
        """Test initialization with custom stores."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )
        assert kb._vector_store == mock_vector_store
        assert kb._embedding_engine == mock_embedding_engine

    @pytest.mark.asyncio
    async def test_add_document(self, mock_vector_store, mock_embedding_engine):
        """Test adding a document."""
        from backend.brain.knowledge_base import KnowledgeBase

        mock_embedding_engine.embed = AsyncMock(
            return_value=[[0.1, 0.2], [0.3, 0.4]]
        )
        mock_vector_store.add = AsyncMock(return_value=["c1", "c2"])

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        doc_id = await kb.add_document(
            content="This is test content that is long enough to chunk",
            metadata={"source": "test"}
        )

        assert doc_id is not None
        assert doc_id in kb._documents
        assert kb._documents[doc_id]["metadata"]["source"] == "test"

    @pytest.mark.asyncio
    async def test_add_document_with_custom_id(self, mock_vector_store, mock_embedding_engine):
        """Test adding document with custom ID."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        doc_id = await kb.add_document(
            content="Content",
            doc_id="custom-doc-id"
        )

        assert doc_id == "custom-doc-id"

    @pytest.mark.asyncio
    async def test_add_document_custom_chunk_params(
        self, mock_vector_store, mock_embedding_engine
    ):
        """Test adding document with custom chunk parameters."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        doc_id = await kb.add_document(
            content="A" * 1000,
            chunk_size=100,
            chunk_overlap=10
        )

        assert doc_id is not None

    @pytest.mark.asyncio
    async def test_search(self, mock_vector_store, mock_embedding_engine):
        """Test searching the knowledge base."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        results = await kb.search("query text", top_k=5)

        assert len(results) == 1
        mock_embedding_engine.embed.assert_called_once()
        mock_vector_store.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_filter(self, mock_vector_store, mock_embedding_engine):
        """Test searching with metadata filter."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        await kb.search(
            "query",
            filter_metadata={"category": "test"}
        )

        call_args = mock_vector_store.search.call_args
        assert call_args.kwargs["filter_metadata"] == {"category": "test"}

    @pytest.mark.asyncio
    async def test_delete_document_existing(self, mock_vector_store, mock_embedding_engine):
        """Test deleting existing document."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        # Add a document first
        doc_id = await kb.add_document(content="Test content")

        result = await kb.delete_document(doc_id)

        assert result is True
        assert doc_id not in kb._documents

    @pytest.mark.asyncio
    async def test_delete_document_nonexistent(self, mock_vector_store, mock_embedding_engine):
        """Test deleting nonexistent document."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        result = await kb.delete_document("nonexistent")

        assert result is False

    def test_chunk_text(self, mock_vector_store, mock_embedding_engine):
        """Test text chunking."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        text = "A" * 100
        chunks = kb._chunk_text(text, chunk_size=30, chunk_overlap=10)

        assert len(chunks) > 1
        assert all(len(chunk) <= 30 for chunk in chunks)

    def test_chunk_text_small_text(self, mock_vector_store, mock_embedding_engine):
        """Test chunking text smaller than chunk size."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        chunks = kb._chunk_text("Small text", chunk_size=100, chunk_overlap=10)

        assert len(chunks) == 1

    def test_get_stats(self, mock_vector_store, mock_embedding_engine):
        """Test getting knowledge base stats."""
        from backend.brain.knowledge_base import KnowledgeBase

        kb = KnowledgeBase(
            name="test_kb",
            vector_store=mock_vector_store,
            embedding_engine=mock_embedding_engine
        )

        stats = kb.get_stats()

        assert stats["name"] == "test_kb"
        assert stats["document_count"] == 0
        assert stats["vector_count"] == 10


class TestMemoryStoreFull:
    """Comprehensive tests for MemoryStore."""

    def test_init(self):
        """Test initialization."""
        store = MemoryStore()
        assert store._memories == {}
        assert store._agent_memories == {}

    def test_store_first_memory(self):
        """Test storing first memory for an agent."""
        store = MemoryStore()

        memory_id = store.store(
            agent_id="agent-1",
            content="Important fact",
            memory_type="fact",
            importance=0.8
        )

        assert memory_id is not None
        assert memory_id in store._memories
        assert "agent-1" in store._agent_memories
        assert memory_id in store._agent_memories["agent-1"]

    def test_store_multiple_memories(self):
        """Test storing multiple memories for same agent."""
        store = MemoryStore()

        store.store(agent_id="agent-1", content="Fact 1")
        store.store(agent_id="agent-1", content="Fact 2")

        assert len(store._agent_memories["agent-1"]) == 2

    def test_retrieve_no_agent(self):
        """Test retrieving from nonexistent agent returns empty."""
        store = MemoryStore()

        memories = store.retrieve(agent_id="nonexistent")

        assert memories == []

    def test_retrieve_with_type_filter(self):
        """Test retrieving with memory type filter."""
        store = MemoryStore()

        store.store(agent_id="agent-1", content="Fact", memory_type="fact")
        store.store(agent_id="agent-1", content="Experience", memory_type="experience")

        memories = store.retrieve(agent_id="agent-1", memory_type="fact")

        assert len(memories) == 1
        assert memories[0].memory_type == "fact"

    def test_retrieve_with_query_filter(self):
        """Test retrieving with content query filter."""
        store = MemoryStore()

        store.store(agent_id="agent-1", content="Python is great")
        store.store(agent_id="agent-1", content="Java is good")

        memories = store.retrieve(agent_id="agent-1", query="python")

        assert len(memories) == 1
        assert "Python" in memories[0].content

    def test_retrieve_sorted_by_importance(self):
        """Test memories are sorted by importance."""
        store = MemoryStore()

        store.store(agent_id="agent-1", content="Low", importance=0.1)
        store.store(agent_id="agent-1", content="High", importance=0.9)

        memories = store.retrieve(agent_id="agent-1")

        assert memories[0].content == "High"

    def test_retrieve_updates_access_stats(self):
        """Test retrieving updates access statistics."""
        store = MemoryStore()

        store.store(agent_id="agent-1", content="Test")

        memories = store.retrieve(agent_id="agent-1")

        assert memories[0].access_count == 1
        assert memories[0].last_accessed is not None

    def test_retrieve_with_limit(self):
        """Test retrieving with limit."""
        store = MemoryStore()

        for i in range(5):
            store.store(agent_id="agent-1", content=f"Memory {i}")

        memories = store.retrieve(agent_id="agent-1", limit=2)

        assert len(memories) == 2

    def test_forget_existing(self):
        """Test forgetting existing memory."""
        store = MemoryStore()

        memory_id = store.store(agent_id="agent-1", content="To forget")

        result = store.forget(memory_id)

        assert result is True
        assert memory_id not in store._memories
        assert memory_id not in store._agent_memories["agent-1"]

    def test_forget_nonexistent(self):
        """Test forgetting nonexistent memory."""
        store = MemoryStore()

        result = store.forget("nonexistent")

        assert result is False

    def test_get_agent_memory_stats_no_agent(self):
        """Test getting stats for nonexistent agent."""
        store = MemoryStore()

        stats = store.get_agent_memory_stats("nonexistent")

        assert stats["total"] == 0
        assert stats["by_type"] == {}

    def test_get_agent_memory_stats_with_memories(self):
        """Test getting stats with memories."""
        store = MemoryStore()

        store.store(agent_id="agent-1", content="Fact 1", memory_type="fact")
        store.store(agent_id="agent-1", content="Fact 2", memory_type="fact")
        store.store(agent_id="agent-1", content="Exp 1", memory_type="experience")

        stats = store.get_agent_memory_stats("agent-1")

        assert stats["total"] == 3
        assert stats["by_type"]["fact"] == 2
        assert stats["by_type"]["experience"] == 1


class TestContextManagerFull:
    """Comprehensive tests for ContextManager."""

    def test_init(self):
        """Test initialization."""
        manager = ContextManager()
        assert manager._max_tokens == 4000
        assert manager._conversations == {}

    def test_init_custom_max_tokens(self):
        """Test initialization with custom max tokens."""
        manager = ContextManager(max_tokens=8000)
        assert manager._max_tokens == 8000

    def test_create_conversation_auto_id(self):
        """Test creating conversation with auto-generated ID."""
        manager = ContextManager()

        conv_id = manager.create_conversation()

        assert conv_id is not None
        assert conv_id in manager._conversations

    def test_create_conversation_custom_id(self):
        """Test creating conversation with custom ID."""
        manager = ContextManager()

        conv_id = manager.create_conversation(
            conversation_id="custom-id",
            metadata={"key": "value"}
        )

        assert conv_id == "custom-id"
        assert manager._conversations[conv_id].metadata == {"key": "value"}

    def test_add_message_success(self):
        """Test adding message to existing conversation."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        result = manager.add_message(conv_id, "user", "Hello")

        assert result is True
        assert len(manager._conversations[conv_id].messages) == 1

    def test_add_message_nonexistent_conversation(self):
        """Test adding message to nonexistent conversation returns False."""
        manager = ContextManager()

        result = manager.add_message("nonexistent", "user", "Hello")

        assert result is False

    def test_add_message_with_metadata(self):
        """Test adding message with metadata."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        manager.add_message(
            conv_id, "user", "Hello",
            metadata={"timestamp": "2024-01-01"}
        )

        msg = manager._conversations[conv_id].messages[0]
        assert msg.metadata == {"timestamp": "2024-01-01"}

    def test_get_context_nonexistent(self):
        """Test getting context for nonexistent conversation."""
        manager = ContextManager()

        context = manager.get_context("nonexistent")

        assert context == []

    def test_get_context_with_max_messages(self):
        """Test getting context with message limit."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        for i in range(5):
            manager.add_message(conv_id, "user", f"Message {i}")

        context = manager.get_context(conv_id, max_messages=2)

        assert len(context) == 2
        # Should be last 2 messages
        assert "Message 3" in context[0]["content"]
        assert "Message 4" in context[1]["content"]

    def test_get_conversation_summary_nonexistent(self):
        """Test getting summary for nonexistent conversation."""
        manager = ContextManager()

        summary = manager.get_conversation_summary("nonexistent")

        assert summary is None

    def test_get_conversation_summary_empty(self):
        """Test getting summary for empty conversation."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        summary = manager.get_conversation_summary(conv_id)

        assert summary == "Empty conversation"

    def test_get_conversation_summary_with_messages(self):
        """Test getting summary with user messages."""
        manager = ContextManager()
        conv_id = manager.create_conversation()
        manager.add_message(conv_id, "user", "How do I implement authentication?")

        summary = manager.get_conversation_summary(conv_id)

        assert "authentication" in summary
        assert "(1 messages)" in summary

    def test_delete_conversation_existing(self):
        """Test deleting existing conversation."""
        manager = ContextManager()
        conv_id = manager.create_conversation()

        result = manager.delete_conversation(conv_id)

        assert result is True
        assert conv_id not in manager._conversations

    def test_delete_conversation_nonexistent(self):
        """Test deleting nonexistent conversation."""
        manager = ContextManager()

        result = manager.delete_conversation("nonexistent")

        assert result is False

    def test_manage_context_window_no_trimming(self):
        """Test context management when under limit."""
        manager = ContextManager(max_tokens=1000)
        conv_id = manager.create_conversation()

        manager.add_message(conv_id, "user", "Short message")

        # Should not trim
        assert len(manager._conversations[conv_id].messages) == 1

    def test_manage_context_window_trims_when_over_limit(self):
        """Test context management trims when over limit."""
        manager = ContextManager(max_tokens=10)  # Very small limit
        conv_id = manager.create_conversation()

        # Add many long messages
        for _i in range(10):
            manager.add_message(conv_id, "user", "A" * 100)

        # Should have trimmed some messages but kept at least 2
        assert len(manager._conversations[conv_id].messages) >= 2

    def test_manage_context_window_keeps_minimum_messages(self):
        """Test context management keeps at least 2 messages."""
        manager = ContextManager(max_tokens=1)  # Tiny limit
        conv_id = manager.create_conversation()

        manager.add_message(conv_id, "user", "First long message " * 50)
        manager.add_message(conv_id, "assistant", "Second long message " * 50)
        manager.add_message(conv_id, "user", "Third long message " * 50)

        # Should keep at least 2 messages
        assert len(manager._conversations[conv_id].messages) >= 2


class TestMemoryDataclass:
    """Tests for Memory dataclass."""

    def test_memory_creation(self):
        """Test memory creation with defaults."""
        memory = Memory(
            memory_id="m-123",
            agent_id="a-456",
            content="Test content",
            memory_type="fact"
        )
        assert memory.importance == 1.0
        assert memory.access_count == 0
        assert memory.last_accessed is None


class TestMessageDataclass:
    """Tests for Message dataclass."""

    def test_message_creation(self):
        """Test message creation with defaults."""
        msg = Message(role="user", content="Hello")
        assert msg.metadata == {}
        assert isinstance(msg.timestamp, datetime)


class TestConversationDataclass:
    """Tests for Conversation dataclass."""

    def test_conversation_creation(self):
        """Test conversation creation with defaults."""
        conv = Conversation(conversation_id="c-123")
        assert conv.messages == []
        assert conv.metadata == {}
        assert isinstance(conv.created_at, datetime)
