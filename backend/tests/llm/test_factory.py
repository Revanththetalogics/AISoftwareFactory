"""
Tests for LLM Factory.

Tests for LLMFactory class in backend/llm/factory.py.
"""

from unittest.mock import patch

import pytest

from backend.llm.factory import LLMFactory


class TestLLMFactoryCreateLLM:
    """Test LLMFactory.create_llm method."""

    def test_create_ollama_provider(self):
        """Test creating Ollama provider."""
        provider = LLMFactory.create_llm("ollama")

        # Import after creation to verify type
        from backend.llm.ollama_provider import OllamaProvider

        assert isinstance(provider, OllamaProvider)

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        provider = LLMFactory.create_llm("openai")

        from backend.llm.openai_provider import OpenAIProvider

        assert isinstance(provider, OpenAIProvider)

    def test_create_default_provider(self):
        """Test creating provider with default (ollama)."""
        provider = LLMFactory.create_llm()

        from backend.llm.ollama_provider import OllamaProvider

        assert isinstance(provider, OllamaProvider)

    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.create_llm("anthropic")

        assert "Unsupported LLM provider" in str(exc_info.value)
        assert "anthropic" in str(exc_info.value)

    def test_create_invalid_provider(self):
        """Test creating invalid provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.create_llm("invalid_provider")

        assert "Unsupported LLM provider" in str(exc_info.value)

    def test_create_empty_provider(self):
        """Test creating empty provider name raises error."""
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.create_llm("")

        assert "Unsupported LLM provider" in str(exc_info.value)


class TestLLMFactoryGetDefaultProvider:
    """Test LLMFactory.get_default_provider method."""

    def test_default_from_env(self):
        """Test get_default_provider from environment."""
        with patch.dict("os.environ", {"LLM_PROVIDER": "openai"}):
            provider = LLMFactory.get_default_provider()

            assert provider == "openai"

    def test_default_without_env(self):
        """Test get_default_provider without environment variable."""
        with patch.dict("os.environ", {}, clear=True):
            provider = LLMFactory.get_default_provider()

            assert provider == "ollama"

    def test_default_custom_env_value(self):
        """Test get_default_provider with custom env value."""
        with patch.dict("os.environ", {"LLM_PROVIDER": "anthropic"}):
            provider = LLMFactory.get_default_provider()

            assert provider == "anthropic"


class TestLLMFactoryIntegration:
    """Integration tests for LLMFactory."""

    def test_create_and_use_ollama(self):
        """Test creating and using Ollama provider."""
        provider = LLMFactory.create_llm("ollama")

        assert provider.name == "ollama:llama3.2"
        assert provider.supports_streaming is True
        assert provider.supports_embeddings is True

    def test_create_and_use_openai(self):
        """Test creating and using OpenAI provider."""
        provider = LLMFactory.create_llm("openai")

        assert "openai:" in provider.name
        assert provider.supports_streaming is True
        assert provider.supports_embeddings is True

    def test_factory_is_stateless(self):
        """Test that factory is stateless (each call creates new instance)."""
        provider1 = LLMFactory.create_llm("ollama")
        provider2 = LLMFactory.create_llm("ollama")

        # Should be different instances
        assert provider1 is not provider2

    def test_create_with_default_provider(self):
        """Test creating with default provider from environment."""
        with patch.dict("os.environ", {"LLM_PROVIDER": "ollama"}):
            default_provider = LLMFactory.get_default_provider()
            provider = LLMFactory.create_llm(default_provider)

            from backend.llm.ollama_provider import OllamaProvider
            assert isinstance(provider, OllamaProvider)
