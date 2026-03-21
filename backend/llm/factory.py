"""
LLM Factory for creating LLM provider instances.
"""

import os

from backend.core.logging import get_logger
from backend.llm.base_provider import BaseLLMProvider

logger = get_logger(__name__)


class LLMFactory:
    """
    Factory for creating LLM provider instances.

    Provides a unified interface for instantiating different LLM providers
    based on configuration.
    """

    @staticmethod
    def create_llm(provider: str = "ollama") -> BaseLLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider: Provider name (ollama, openai, anthropic)

        Returns:
            LLM provider instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider == "ollama":
            from backend.llm.ollama_provider import OllamaProvider
            return OllamaProvider()
        elif provider == "openai":
            from backend.llm.openai_provider import OpenAIProvider
            return OpenAIProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def get_default_provider() -> str:
        """Get the default LLM provider from environment."""
        return os.getenv("LLM_PROVIDER", "ollama")
