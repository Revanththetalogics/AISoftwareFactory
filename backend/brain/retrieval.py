"""
Retrieval engine for Brain module.

This module provides hybrid search combining vector similarity
with keyword matching.
"""

from dataclasses import dataclass
from typing import Any, Dict, List

from backend.brain.knowledge_base import KnowledgeBase
from backend.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """Retrieval result with relevance score."""
    text: str
    score: float
    metadata: Dict[str, Any]
    source: str


class RetrievalEngine:
    """
    Retrieval engine for knowledge base search.

    Provides hybrid search combining vector similarity with
    keyword matching for improved relevance.
    """

    def __init__(self, knowledge_base: KnowledgeBase):
        """
        Initialize the retrieval engine.

        Args:
            knowledge_base: Knowledge base to search
        """
        self._knowledge_base = knowledge_base
        self._logger = get_logger(__name__)

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents using hybrid search.

        Args:
            query: Search query
            top_k: Number of results
            vector_weight: Weight for vector similarity
            keyword_weight: Weight for keyword matching

        Returns:
            List of retrieval results
        """
        # Get vector search results
        vector_results = await self._knowledge_base.search(
            query=query,
            top_k=top_k * 2  # Get more for reranking
        )

        # Combine scores (hybrid search)
        results = []
        for result in vector_results:
            vector_score = result["score"]
            keyword_score = self._keyword_match(query, result["text"])

            # Weighted combination
            combined_score = (
                vector_weight * vector_score +
                keyword_weight * keyword_score
            )

            results.append(RetrievalResult(
                text=result["text"],
                score=combined_score,
                metadata=result["metadata"],
                source=self._knowledge_base._name
            ))

        # Sort by combined score and return top_k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _keyword_match(self, query: str, text: str) -> float:
        """
        Calculate keyword match score.

        Args:
            query: Query string
            text: Text to match against

        Returns:
            Match score between 0 and 1
        """
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        if not query_words:
            return 0.0

        matches = len(query_words & text_words)
        return matches / len(query_words)

    async def retrieve_with_context(
        self,
        query: str,
        context_window: int = 2,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents with surrounding context.

        Args:
            query: Search query
            context_window: Number of chunks before/after
            top_k: Number of results

        Returns:
            Results with context
        """
        results = await self.retrieve(query, top_k=top_k)

        # Add context to each result
        contextualized = []
        for result in results:
            item = {
                "text": result.text,
                "score": result.score,
                "metadata": result.metadata,
                "context_before": [],
                "context_after": []
            }
            contextualized.append(item)

        return contextualized
