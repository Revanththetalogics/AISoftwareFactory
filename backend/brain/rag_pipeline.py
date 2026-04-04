"""
RAG pipeline for Brain module.

This module provides the complete Retrieval-Augmented Generation pipeline
combining knowledge retrieval with LLM generation.
"""

from typing import Any

from backend.brain.context_manager import ContextManager
from backend.brain.knowledge_base import KnowledgeBase
from backend.brain.retrieval import RetrievalEngine
from backend.core.logging import get_logger
from backend.llm.factory import LLMFactory

logger = get_logger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.

    Combines knowledge retrieval with LLM generation for
    context-aware responses.
    """

    def __init__(
        self, knowledge_base: KnowledgeBase, context_manager: ContextManager | None = None, llm_provider: str = "ollama"
    ):
        """
        Initialize the RAG pipeline.

        Args:
            knowledge_base: Knowledge base for retrieval
            context_manager: Context manager for conversation history
            llm_provider: LLM provider to use
        """
        self._knowledge_base = knowledge_base
        self._retrieval = RetrievalEngine(knowledge_base)
        self._context = context_manager or ContextManager()
        self._llm = LLMFactory.create_llm(provider=llm_provider)
        self._logger = get_logger(__name__)

    async def query(
        self, query: str, conversation_id: str | None = None, top_k: int = 3, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """
        Execute a RAG query.

        Args:
            query: User query
            conversation_id: Optional conversation ID
            top_k: Number of documents to retrieve
            system_prompt: Optional system prompt

        Returns:
            Response with retrieved context
        """
        # Create conversation if needed
        if not conversation_id:
            conversation_id = self._context.create_conversation()

        # Add user message
        self._context.add_message(conversation_id, "user", query)

        # Retrieve relevant documents
        retrieved = await self._retrieval.retrieve(query, top_k=top_k)

        # Build context from retrieved documents
        context_text = "\n\n".join([f"[Document {i + 1}]: {r.text}" for i, r in enumerate(retrieved)])

        # Get conversation history
        history = self._context.get_context(conversation_id, max_messages=5)

        # Build prompt
        prompt = self._build_prompt(query=query, context=context_text, history=history, system_prompt=system_prompt)

        # Generate response
        try:
            response = await self._llm.generate(prompt)

            # Add assistant message
            self._context.add_message(conversation_id, "assistant", response)

            return {
                "response": response,
                "conversation_id": conversation_id,
                "retrieved_documents": [{"text": r.text, "score": r.score, "source": r.source} for r in retrieved],
                "success": True,
            }

        except Exception as e:
            self._logger.error("RAG query failed", error=str(e))
            return {"response": "", "conversation_id": conversation_id, "error": str(e), "success": False}

    def _build_prompt(
        self, query: str, context: str, history: list[dict[str, Any]], system_prompt: str | None = None
    ) -> str:
        """Build the RAG prompt."""
        parts = []

        # System prompt
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        else:
            parts.append(
                "System: You are a helpful assistant. Use the provided context "
                "to answer the user's question accurately."
            )

        # Context
        parts.append(f"\nContext:\n{context}")

        # History
        if history:
            parts.append("\nConversation History:")
            for msg in history:
                parts.append(f"{msg['role']}: {msg['content']}")

        # Query
        parts.append(f"\nUser: {query}")
        parts.append("\nAssistant:")

        return "\n".join(parts)

    def get_conversation_history(self, conversation_id: str) -> list[dict[str, Any]]:
        """Get conversation history."""
        return self._context.get_context(conversation_id)
