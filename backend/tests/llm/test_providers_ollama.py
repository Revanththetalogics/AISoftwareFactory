"""
Tests for Ollama Provider (providers module).

Tests for OllamaProvider class in backend/llm/providers/ollama.py.
"""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from backend.llm.providers.base import LLMRequest, ModelCapability
from backend.llm.providers.ollama import OllamaProvider


@pytest.fixture
def ollama_provider():
    """Create OllamaProvider instance for testing."""
    return OllamaProvider(
        base_url="http://localhost:11434",
        default_model="llama3.2",
        timeout=60.0
    )


@pytest.fixture
def mock_httpx_client():
    """Create mock httpx client."""
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


class TestOllamaProviderInit:
    """Test OllamaProvider initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        provider = OllamaProvider()

        assert provider.name == "ollama"
        assert provider.base_url == "http://localhost:11434"
        assert provider.default_model == "llama3.2"
        assert provider.timeout == 120.0

    def test_custom_initialization(self):
        """Test custom initialization."""
        provider = OllamaProvider(
            base_url="http://custom:8080/",  # Trailing slash
            default_model="custom-model",
            timeout=30.0
        )

        assert provider.base_url == "http://custom:8080"  # Slash stripped
        assert provider.default_model == "custom-model"
        assert provider.timeout == 30.0

    def test_recommended_models(self):
        """Test RECOMMENDED_MODELS constant."""
        assert OllamaProvider.RECOMMENDED_MODELS["general"] == "llama3.2"
        assert OllamaProvider.RECOMMENDED_MODELS["coding"] == "deepseek-coder-v2"
        assert OllamaProvider.RECOMMENDED_MODELS["chat"] == "qwen2.5"
        assert OllamaProvider.RECOMMENDED_MODELS["reasoning"] == "mixtral:8x7b"
        assert OllamaProvider.RECOMMENDED_MODELS["vision"] == "llama3.2-vision"


class TestOllamaProviderClient:
    """Test HTTP client management."""

    def test_get_client_creates_new(self, ollama_provider):
        """Test _get_client creates new client."""
        client = ollama_provider._get_client()

        assert isinstance(client, httpx.AsyncClient)
        assert ollama_provider._client is client

    def test_get_client_reuses_existing(self, ollama_provider, mock_httpx_client):
        """Test _get_client reuses existing client."""
        ollama_provider._client = mock_httpx_client

        client = ollama_provider._get_client()

        assert client is mock_httpx_client


class TestOllamaProviderIsAvailable:
    """Test is_available method."""

    @pytest.mark.asyncio
    async def test_is_available_success(self, ollama_provider, mock_httpx_client):
        """Test is_available returns True when Ollama is running."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2"},
                {"name": "qwen2.5"}
            ]
        }
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        result = await ollama_provider.is_available()

        assert result is True
        assert "llama3.2" in ollama_provider._available_models
        assert "qwen2.5" in ollama_provider._available_models

    @pytest.mark.asyncio
    async def test_is_available_failure(self, ollama_provider, mock_httpx_client):
        """Test is_available returns False on error."""
        mock_httpx_client.get = AsyncMock(side_effect=httpx.RequestError("Connection refused"))
        ollama_provider._client = mock_httpx_client

        result = await ollama_provider.is_available()

        assert result is False

    @pytest.mark.asyncio
    async def test_is_available_non_200(self, ollama_provider, mock_httpx_client):
        """Test is_available returns False on non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_httpx_client.get = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        result = await ollama_provider.is_available()

        assert result is False


class TestOllamaProviderGetAvailableModels:
    """Test get_available_models method."""

    def test_get_available_models_empty(self, ollama_provider):
        """Test get_available_models when empty."""
        result = ollama_provider.get_available_models()

        assert result == []

    def test_get_available_models_populated(self, ollama_provider):
        """Test get_available_models returns cached models."""
        ollama_provider._available_models = ["model1", "model2", "model3"]

        result = ollama_provider.get_available_models()

        assert result == ["model1", "model2", "model3"]

    def test_get_available_models_returns_copy(self, ollama_provider):
        """Test get_available_models returns a copy."""
        ollama_provider._available_models = ["model1"]

        result = ollama_provider.get_available_models()
        result.append("model2")

        # Original should be unchanged
        assert "model2" not in ollama_provider._available_models


class TestOllamaProviderGenerate:
    """Test generate method."""

    @pytest.mark.asyncio
    async def test_generate_success(self, ollama_provider, mock_httpx_client):
        """Test successful generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "Generated text",
            "prompt_eval_count": 10,
            "eval_count": 5,
            "done_reason": "stop",
            "total_duration": 1000,
            "load_duration": 500
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(prompt="Hello", model="llama3.2")
        response = await ollama_provider.generate(request)

        assert response.text == "Generated text"
        assert response.model == "llama3.2"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 5
        assert response.total_tokens == 15
        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_uses_default_model(self, ollama_provider, mock_httpx_client):
        """Test generate uses default model when none specified."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "OK"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(prompt="Hello")  # No model
        response = await ollama_provider.generate(request)

        assert response.model == "llama3.2"  # Default

    @pytest.mark.asyncio
    async def test_generate_with_stop_sequences(self, ollama_provider, mock_httpx_client):
        """Test generate with stop sequences."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "OK"}
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(
            prompt="Hello",
            stop_sequences=["STOP", "END"]
        )
        await ollama_provider.generate(request)

        # Verify stop sequences were included
        call_args = mock_httpx_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")
        assert payload["options"]["stop"] == ["STOP", "END"]

    @pytest.mark.asyncio
    async def test_generate_estimates_tokens(self, ollama_provider, mock_httpx_client):
        """Test generate estimates tokens when not provided."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "Short response",  # 14 chars
            "prompt_eval_count": 0,  # Not provided
            "eval_count": 0  # Not provided
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(prompt="Hello world test")  # 16 chars
        response = await ollama_provider.generate(request)

        # Should estimate tokens (chars // 4)
        assert response.prompt_tokens == 4  # 16 // 4
        assert response.completion_tokens == 3  # 14 // 4

    @pytest.mark.asyncio
    async def test_generate_http_error(self, ollama_provider, mock_httpx_client):
        """Test generate handles HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=mock_response
        )
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(prompt="Hello")
        response = await ollama_provider.generate(request)

        assert response.success is False
        assert "HTTP 500" in response.error

    @pytest.mark.asyncio
    async def test_generate_request_error(self, ollama_provider, mock_httpx_client):
        """Test generate handles request errors."""
        mock_httpx_client.post = AsyncMock(
            side_effect=httpx.RequestError("Connection refused")
        )
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(prompt="Hello")
        response = await ollama_provider.generate(request)

        assert response.success is False
        assert "Connection error" in response.error

    @pytest.mark.asyncio
    async def test_generate_general_error(self, ollama_provider, mock_httpx_client):
        """Test generate handles general errors."""
        mock_httpx_client.post = AsyncMock(
            side_effect=RuntimeError("Unexpected error")
        )
        ollama_provider._client = mock_httpx_client

        request = LLMRequest(prompt="Hello")
        response = await ollama_provider.generate(request)

        assert response.success is False
        assert "Unexpected error" in response.error


class TestOllamaProviderChat:
    """Test chat method."""

    @pytest.mark.asyncio
    async def test_chat_success(self, ollama_provider, mock_httpx_client):
        """Test successful chat completion."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Chat response"},
            "done": True
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        messages = [{"role": "user", "content": "Hello"}]
        response = await ollama_provider.chat(messages)

        assert response.text == "Chat response"
        assert response.success is True

    @pytest.mark.asyncio
    async def test_chat_with_model(self, ollama_provider, mock_httpx_client):
        """Test chat with specified model."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Response"},
            "done": True
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        messages = [{"role": "user", "content": "Hi"}]
        response = await ollama_provider.chat(messages, model="qwen2.5")

        assert response.model == "qwen2.5"

    @pytest.mark.asyncio
    async def test_chat_with_temperature(self, ollama_provider, mock_httpx_client):
        """Test chat with custom temperature."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Response"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        messages = [{"role": "user", "content": "Hi"}]
        await ollama_provider.chat(messages, temperature=0.5)

        call_args = mock_httpx_client.post.call_args
        payload = call_args.kwargs.get("json") or call_args[1].get("json")
        assert payload["options"]["temperature"] == 0.5

    @pytest.mark.asyncio
    async def test_chat_uses_default_model(self, ollama_provider, mock_httpx_client):
        """Test chat uses default model when none specified."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "message": {"content": "Response"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        messages = [{"role": "user", "content": "Hi"}]
        response = await ollama_provider.chat(messages)

        assert response.model == "llama3.2"

    @pytest.mark.asyncio
    async def test_chat_error(self, ollama_provider, mock_httpx_client):
        """Test chat error handling."""
        mock_httpx_client.post = AsyncMock(
            side_effect=RuntimeError("Connection error")
        )
        ollama_provider._client = mock_httpx_client

        messages = [{"role": "user", "content": "Hi"}]
        response = await ollama_provider.chat(messages)

        assert response.success is False
        assert "Connection error" in response.error


class TestOllamaProviderPullModel:
    """Test pull_model method."""

    @pytest.mark.asyncio
    async def test_pull_model_success(self, ollama_provider, mock_httpx_client):
        """Test successful model pull."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        result = await ollama_provider.pull_model("llama3.2")

        assert result is True

    @pytest.mark.asyncio
    async def test_pull_model_failure(self, ollama_provider, mock_httpx_client):
        """Test failed model pull."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_httpx_client.post = AsyncMock(return_value=mock_response)
        ollama_provider._client = mock_httpx_client

        result = await ollama_provider.pull_model("nonexistent-model")

        assert result is False

    @pytest.mark.asyncio
    async def test_pull_model_exception(self, ollama_provider, mock_httpx_client):
        """Test model pull with exception."""
        mock_httpx_client.post = AsyncMock(
            side_effect=RuntimeError("Connection error")
        )
        ollama_provider._client = mock_httpx_client

        result = await ollama_provider.pull_model("llama3.2")

        assert result is False


class TestOllamaProviderCapabilities:
    """Test get_capabilities method."""

    def test_get_capabilities(self, ollama_provider):
        """Test get_capabilities returns correct capabilities."""
        capabilities = ollama_provider.get_capabilities()

        assert ModelCapability.TEXT_GENERATION in capabilities
        assert ModelCapability.CHAT in capabilities
        assert ModelCapability.CODE_GENERATION in capabilities
        assert ModelCapability.CODE_REVIEW in capabilities


class TestOllamaProviderClose:
    """Test close method."""

    @pytest.mark.asyncio
    async def test_close(self, ollama_provider, mock_httpx_client):
        """Test close method."""
        ollama_provider._client = mock_httpx_client

        await ollama_provider.close()

        mock_httpx_client.aclose.assert_called_once()
        assert ollama_provider._client is None

    @pytest.mark.asyncio
    async def test_close_no_client(self, ollama_provider):
        """Test close with no client."""
        ollama_provider._client = None

        # Should not raise
        await ollama_provider.close()

        assert ollama_provider._client is None
