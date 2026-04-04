"""
Base LLM provider interface for AI Software Factory.

This module defines the abstract base class for all LLM providers,
ensuring a consistent interface across different LLM implementations.
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM providers must implement this interface to ensure
    consistent behavior across different LLM implementations.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the LLM provider.

        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}

    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int | None = None, **kwargs) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text
        """
        pass  # pragma: no cover

    @abstractmethod
    async def generate_stream(
        self, prompt: str, temperature: float = 0.7, max_tokens: int | None = None, **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate text from a prompt with streaming.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated text
        """
        pass  # pragma: no cover

    @abstractmethod
    async def chat(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, **kwargs
    ) -> str:
        """
        Generate a chat response from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated response
        """
        pass  # pragma: no cover

    @abstractmethod
    async def chat_stream(
        self, messages: list[dict[str, str]], temperature: float = 0.7, max_tokens: int | None = None, **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate a chat response with streaming.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated response
        """
        pass  # pragma: no cover

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate embeddings for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        pass  # pragma: no cover

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy/available.

        Returns:
            True if healthy, False otherwise
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def name(self) -> str:
        """Get provider name."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        pass  # pragma: no cover

    @property
    @abstractmethod
    def supports_embeddings(self) -> bool:
        """Check if provider supports embeddings."""
        pass  # pragma: no cover
