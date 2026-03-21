"""
Knowledge base for Brain module.

This module provides document ingestion and management for the
knowledge system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.brain.embeddings import EmbeddingEngine
from backend.brain.vector_store import VectorStore
from backend.core.logging import get_logger

logger = get_logger(__name__)


class KnowledgeBase:
    """
    Knowledge base for document storage and retrieval.

    Provides document ingestion, chunking, and management
    with vector search capabilities.
    """

    def __init__(
        self,
        name: str,
        vector_store: Optional[VectorStore] = None,
        embedding_engine: Optional[EmbeddingEngine] = None
    ):
        """
        Initialize the knowledge base.

        Args:
            name: Knowledge base name
            vector_store: Vector store instance
            embedding_engine: Embedding engine instance
        """
        self._name = name
        self._vector_store = vector_store or VectorStore(name)
        self._embedding_engine = embedding_engine or EmbeddingEngine()
        self._documents: Dict[str, Dict[str, Any]] = {}
        self._logger = get_logger(__name__)

    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> str:
        """
        Add a document to the knowledge base.

        Args:
            content: Document content
            metadata: Document metadata
            doc_id: Document ID (generated if not provided)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks

        Returns:
            Document ID
        """
        doc_id = doc_id or str(uuid4())
        metadata = metadata or {}

        # Chunk the document
        chunks = self._chunk_text(content, chunk_size, chunk_overlap)

        # Generate embeddings
        embeddings = await self._embedding_engine.embed(chunks)

        # Prepare metadata for each chunk
        chunk_metadatas = [
            {
                **metadata,
                "doc_id": doc_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            for i in range(len(chunks))
        ]

        # Add to vector store
        chunk_ids = await self._vector_store.add(
            texts=chunks,
            embeddings=embeddings,
            metadatas=chunk_metadatas
        )

        # Store document metadata
        self._documents[doc_id] = {
            "id": doc_id,
            "metadata": metadata,
            "chunk_ids": chunk_ids,
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow().isoformat()
        }

        self._logger.info(
            "Document added to knowledge base",
            doc_id=doc_id,
            chunks=len(chunks),
            kb_name=self._name
        )

        return doc_id

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            top_k: Number of results
            filter_metadata: Metadata filter

        Returns:
            Search results
        """
        # Generate query embedding
        query_embedding = (await self._embedding_engine.embed([query]))[0]

        # Search vector store
        results = await self._vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )

        return results

    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the knowledge base.

        Args:
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        if doc_id not in self._documents:
            return False

        doc = self._documents[doc_id]

        # Delete chunks from vector store
        await self._vector_store.delete(doc["chunk_ids"])

        # Remove document metadata
        del self._documents[doc_id]

        self._logger.info("Document deleted", doc_id=doc_id)
        return True

    def _chunk_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap

        return chunks

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "name": self._name,
            "document_count": len(self._documents),
            "vector_count": self._vector_store.get_count()
        }
