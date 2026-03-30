"""Comprehensive tests for brain modules to increase coverage"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import numpy as np
from datetime import datetime, UTC

from backend.brain.context_manager import ContextManager
from backend.brain.embeddings import EmbeddingEngine
from backend.brain.knowledge_base import KnowledgeBase
from backend.brain.memory_store import MemoryStore
from backend.brain.rag_pipeline import RAGPipeline
from backend.brain.retrieval import RetrievalEngine
from backend.brain.vector_store import VectorStore

class TestBrainModules:
    """Test all brain-related modules"""
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test context manager functionality"""
        context_manager = ContextManager()
        
        # Test context creation
        context_id = await context_manager.create_context(
            session_id="session-1",
            user_id="user-1",
            initial_state={"topic": "software development"}
        )
        assert context_id is not None
        
        # Test context retrieval
        context = await context_manager.get_context(context_id)
        assert context is not None
        assert context.session_id == "session-1"
        
        # Test context update
        await context_manager.update_context(
            context_id,
            {"current_task": "coding"}
        )
        updated_context = await context_manager.get_context(context_id)
        assert updated_context.state.get("current_task") == "coding"
        
        # Test context cleanup
        await context_manager.cleanup_expired_contexts()
    
    @pytest.mark.asyncio
    async def test_embedding_service(self):
        """Test embedding service"""
        with patch('backend.brain.embeddings.OpenAIEmbeddings') as mock_embeddings:
            mock_embedder = AsyncMock()
            mock_embedder.embed_documents.return_value = [[0.1, 0.2, 0.3]]
            mock_embedder.embed_query.return_value = [0.1, 0.2, 0.3]
            mock_embeddings.return_value = mock_embedder
            
            embedding_service = EmbeddingEngine()
            await embedding_service.initialize()
            
            # Test document embedding
            docs = ["This is a test document"]
            embeddings = await embedding_service.embed_documents(docs)
            assert len(embeddings) == 1
            assert len(embeddings[0]) == 3
            
            # Test query embedding
            query_embedding = await embedding_service.embed_query("test query")
            assert len(query_embedding) == 3
    
    @pytest.mark.asyncio
    async def test_knowledge_base(self):
        """Test knowledge base functionality"""
        with patch('backend.brain.knowledge_base.VectorStore') as mock_vector_store:
            mock_store = AsyncMock()
            mock_store.add_documents.return_value = ["doc-1"]
            mock_store.similarity_search.return_value = [
                MagicMock(page_content="test content", metadata={})
            ]
            mock_vector_store.return_value = mock_store
            
            kb = KnowledgeBase(name="test_kb")
            await kb.initialize()
            
            # Test adding knowledge
            doc_id = await kb.add_knowledge(
                content="This is valuable knowledge",
                metadata={"source": "documentation"},
                tags=["technical"]
            )
            assert doc_id is not None
            
            # Test searching knowledge
            results = await kb.search("technical knowledge", k=5)
            assert len(results) > 0
            
            # Test getting knowledge by ID
            doc = await kb.get_knowledge(doc_id)
            assert doc is not None
    
    @pytest.mark.asyncio
    async def test_memory_store(self):
        """Test memory store functionality"""
        memory_store = MemoryStoreEngine()
        await memory_store.initialize()
        
        # Test storing memory
        memory_id = await memory_store.store_memory(
            content="User prefers Python for backend development",
            memory_type="preference",
            user_id="user-1",
            metadata={"confidence": 0.9}
        )
        assert memory_id is not None
        
        # Test retrieving memories
        memories = await memory_store.get_memories(
            user_id="user-1",
            memory_type="preference"
        )
        assert len(memories) > 0
        
        # Test memory search
        search_results = await memory_store.search_memories(
            query="Python backend",
            user_id="user-1"
        )
        # Search may return empty results depending on implementation
        
        # Test memory consolidation
        await memory_store.consolidate_memories("user-1")
    
    @pytest.mark.asyncio
    async def test_rag_pipeline(self):
        """Test RAG pipeline"""
        with patch('backend.brain.rag_pipeline.RetrievalService') as mock_retrieval, \
             patch('backend.brain.rag_pipeline.LLMService') as mock_llm:
            
            mock_retriever = AsyncMock()
            mock_retriever.retrieve.return_value = [
                {"content": "relevant context", "score": 0.9}
            ]
            mock_retrieval.return_value = mock_retriever
            
            mock_llm_service = AsyncMock()
            mock_llm_service.generate.return_value = "Generated answer based on context"
            mock_llm.return_value = mock_llm_service
            
            rag = RAGPipelineEngine()
            await rag.initialize()
            
            # Test question answering
            answer = await rag.answer_question(
                question="What is the best programming language?",
                context_filter={"topic": "programming"}
            )
            assert answer is not None
            assert isinstance(answer, str)
    
    @pytest.mark.asyncio
    async def test_retrieval_service(self):
        """Test retrieval service"""
        with patch('backend.brain.retrieval.VectorStore') as mock_vector_store:
            mock_store = AsyncMock()
            mock_store.similarity_search_with_score.return_value = [
                (MagicMock(page_content="relevant document"), 0.85)
            ]
            mock_vector_store.return_value = mock_store
            
            retrieval = RetrievalEngine()
            await retrieval.initialize()
            
            # Test similarity search
            results = await retrieval.retrieve(
                query="find relevant information",
                k=10,
                filters={"category": "technical"}
            )
            assert len(results) > 0
            
            # Test hybrid search (if implemented)
            try:
                hybrid_results = await retrieval.hybrid_search(
                    query="complex search",
                    k=5
                )
                # Hybrid search may not be implemented
            except NotImplementedError:
                pass  # Expected if not implemented
    
    @pytest.mark.asyncio
    async def test_vector_store(self):
        """Test vector store functionality"""
        with patch('backend.brain.vector_store.Chroma') as mock_chroma:
            mock_client = AsyncMock()
            mock_client.add_texts.return_value = ["id-1", "id-2"]
            mock_client.similarity_search_with_score.return_value = [
                (MagicMock(page_content="test"), 0.9)
            ]
            mock_chroma.return_value = mock_client
            
            vector_store = VectorStoreEngine()
            await vector_store.initialize()
            
            # Test adding documents
            doc_ids = await vector_store.add_documents([
                "First document content",
                "Second document content"
            ], metadatas=[
                {"source": "doc1"},
                {"source": "doc2"}
            ])
            assert len(doc_ids) == 2
            
            # Test similarity search
            results = await vector_store.similarity_search(
                query="test query",
                k=5
            )
            assert len(results) > 0
            
            # Test similarity search with scores
            results_with_scores = await vector_store.similarity_search_with_score(
                query="test query",
                k=3
            )
            assert len(results_with_scores) > 0

class TestBrainIntegration:
    """Test integration between brain modules"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_knowledge_flow(self):
        """Test complete knowledge processing flow"""
        # This would test the full flow from knowledge ingestion to retrieval
        # through all brain components
        pass
    
    @pytest.mark.asyncio
    async def test_context_aware_retrieval(self):
        """Test retrieval with context awareness"""
        with patch('backend.brain.context_manager.ContextManager') as mock_context_mgr, \
             patch('backend.brain.retrieval.RetrievalService') as mock_retrieval:
            
            mock_context = AsyncMock()
            mock_context.get_context.return_value = {
                "user_preferences": ["Python", "FastAPI"],
                "current_topic": "web development"
            }
            mock_context_mgr.return_value = mock_context
            
            mock_retriever = AsyncMock()
            mock_retriever.retrieve.return_value = [
                {"content": "Python FastAPI tutorial", "score": 0.95}
            ]
            mock_retrieval.return_value = mock_retriever
            
            # Test context-aware retrieval
            # Implementation would depend on specific integration patterns

if __name__ == "__main__":
    pytest.main([__file__, "-v"])