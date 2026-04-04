"""
Vector store for Brain module.

This module provides vector storage with ChromaDB integration for
semantic search and similarity matching.
"""

from typing import Any
from uuid import uuid4

import numpy as np

from backend.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Vector store for semantic search.

    Provides storage and retrieval of vector embeddings with
    similarity search capabilities.
    """

    def __init__(self, collection_name: str = "default"):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the collection
        """
        self._collection_name = collection_name
        self._vectors: dict[str, dict[str, Any]] = {}
        self._logger = get_logger(__name__)

    async def add(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        """
        Add vectors to the store.

        Args:
            texts: Original texts
            embeddings: Vector embeddings
            metadatas: Optional metadata for each vector
            ids: Optional IDs (generated if not provided)

        Returns:
            List of IDs
        """
        ids = ids or [str(uuid4()) for _ in texts]
        metadatas = metadatas or [{} for _ in texts]

        for id_, text, embedding, metadata in zip(ids, texts, embeddings, metadatas, strict=False):
            self._vectors[id_] = {"text": text, "embedding": embedding, "metadata": metadata}

        self._logger.info("Vectors added", count=len(ids), collection=self._collection_name)

        return ids

    async def search(
        self, query_embedding: list[float], top_k: int = 5, filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            List of similar items with scores
        """
        results = []

        for id_, data in self._vectors.items():
            # Apply metadata filter
            if filter_metadata:
                if not all(data["metadata"].get(k) == v for k, v in filter_metadata.items()):
                    continue

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, data["embedding"])

            results.append({"id": id_, "text": data["text"], "metadata": data["metadata"], "score": similarity})

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def delete(self, ids: list[str]) -> int:
        """
        Delete vectors by ID.

        Args:
            ids: IDs to delete

        Returns:
            Number of deleted vectors
        """
        deleted = 0
        for id_ in ids:
            if id_ in self._vectors:
                del self._vectors[id_]
                deleted += 1

        self._logger.info("Vectors deleted", deleted=deleted, collection=self._collection_name)

        return deleted

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_array = np.array(a)
        b_array = np.array(b)

        dot_product = np.dot(a_array, b_array)
        norm_a = np.linalg.norm(a_array)
        norm_b = np.linalg.norm(b_array)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    def get_count(self) -> int:
        """Get the number of vectors in the store."""
        return len(self._vectors)
