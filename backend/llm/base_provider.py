"""
Base LLM provider interface for AI Software Factory.

This module defines the abstract base class for all LLM providers,
ensuring a consistent interface across different LLM implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All LLM providers must implement this interface to ensure
    consistent behavior across different LLM implementations.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM provider.

        Args:
            config: Provider-specific configuration
        """
        self.config = config or {}

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
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
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
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
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
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
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
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
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the provider is healthy/available.

        Returns:
            True if healthy, False otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get provider name."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Check if provider supports streaming."""
        pass

    @property
    @abstractmethod
    def supports_embeddings(self) -> bool:
        """Check if provider supports embeddings."""
        pass
