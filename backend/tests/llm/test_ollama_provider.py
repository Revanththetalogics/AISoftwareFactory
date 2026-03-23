"""
Tests for Ollama LLM Provider.

Tests for OllamaProvider class in backend/llm/ollama_provider.py.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.llm.ollama_provider import OllamaProvider
from backend.utils.resilience import CircuitBreakerOpenError


@pytest.fixture
def ollama_provider():
    """Create OllamaProvider instance for testing."""
    return OllamaProvider(config={"base_url": "http://localhost:11434", "model": "llama3.2"})


@pytest.fixture
def mock_settings():
    """Mock settings with LLM_TIMEOUT_SECONDS."""
    settings = MagicMock()
    settings.LLM_TIMEOUT_SECONDS = 30.0
    return settings


@pytest.fixture
def mock_metrics():
    """Mock metrics collector."""
    metrics = MagicMock()
    metrics.record_llm_call = MagicMock()
    metrics.record_circuit_breaker_success = MagicMock()
    metrics.record_circuit_breaker_state = MagicMock()
    metrics.record_circuit_breaker_rejection = MagicMock()
    metrics.record_circuit_breaker_failure = MagicMock()
    metrics.record_timeout = MagicMock()
    return metrics


class TestOllamaProviderInit:
    """Test OllamaProvider initialization."""

    def test_init_with_config(self):
        """Test initialization with configuration."""
        provider = OllamaProvider(config={
            "base_url": "http://custom:8080",
            "model": "custom-model"
        })

        assert provider.base_url == "http://custom:8080"
        assert provider.model == "custom-model"

    def test_init_default_values(self):
        """Test initialization with default values."""
        with patch.dict("os.environ", {}, clear=True):
            provider = OllamaProvider()

            assert provider.base_url == "http://localhost:11434"
            assert provider.model == "llama3.2"

    def test_init_from_env(self):
        """Test initialization from environment variables."""
        with patch("backend.llm.ollama_provider.get_settings") as mock_settings:
            mock_settings.return_value.OLLAMA_URL = "http://env-host:9999"
            mock_settings.return_value.OLLAMA_MODEL = "env-model"
            provider = OllamaProvider()

            assert provider.base_url == "http://env-host:9999"
            assert provider.model == "env-model"

    def test_init_config_overrides_env(self):
        """Test that config overrides environment variables."""
        with patch.dict("os.environ", {
            "OLLAMA_BASE_URL": "http://env-host:9999",
            "OLLAMA_MODEL": "env-model"
        }):
            provider = OllamaProvider(config={
                "base_url": "http://config-host:8888",
                "model": "config-model"
            })

            assert provider.base_url == "http://config-host:8888"
            assert provider.model == "config-model"


class TestOllamaProviderSession:
    """Test session management."""

    @pytest.mark.asyncio
    async def test_get_session_creates_new(self, ollama_provider):
        """Test _get_session creates a new session."""
        session = await ollama_provider._get_session()

        assert session is not None
        assert ollama_provider._session is session

        # Clean up
        await session.close()

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing(self, ollama_provider):
        """Test _get_session reuses existing session."""
        session1 = await ollama_provider._get_session()
        session2 = await ollama_provider._get_session()

        assert session1 is session2

        # Clean up
        await session1.close()


class TestOllamaProviderGenerate:
    """Test generate method."""

    @pytest.mark.asyncio
    async def test_generate_success(self, ollama_provider, mock_settings, mock_metrics):
        """Test successful text generation."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb, \
             patch.object(ollama_provider, "_get_session") as mock_get_session:

            # Mock circuit breaker to call function directly
            async def call_func(func):
                return await func()
            mock_cb.call = AsyncMock(side_effect=call_func)
            mock_cb.name = "llm_provider"
            mock_cb.get_state_value = MagicMock(return_value=0)

            # Mock the session and response
            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = AsyncMock(return_value={"response": "Generated text"})

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            result = await ollama_provider.generate("Test prompt")

            assert result == "Generated text"
            mock_metrics.record_llm_call.assert_called()
            mock_metrics.record_circuit_breaker_success.assert_called()

    @pytest.mark.asyncio
    async def test_generate_with_max_tokens(self, ollama_provider, mock_settings, mock_metrics):
        """Test generation with max_tokens parameter."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb, \
             patch.object(ollama_provider, "_get_session") as mock_get_session:

            async def call_func(func):
                return await func()
            mock_cb.call = AsyncMock(side_effect=call_func)
            mock_cb.name = "llm_provider"
            mock_cb.get_state_value = MagicMock(return_value=0)

            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = AsyncMock(return_value={"response": "Generated text"})

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            result = await ollama_provider.generate("Test prompt", max_tokens=100)

            assert result == "Generated text"

    @pytest.mark.asyncio
    async def test_generate_circuit_breaker_open(self, ollama_provider, mock_settings, mock_metrics):
        """Test generation when circuit breaker is open."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb:

            mock_cb.call = AsyncMock(side_effect=CircuitBreakerOpenError("Circuit is open"))
            mock_cb.name = "llm_provider"

            with pytest.raises(CircuitBreakerOpenError):
                await ollama_provider.generate("Test prompt")

            mock_metrics.record_circuit_breaker_rejection.assert_called()

    @pytest.mark.asyncio
    async def test_generate_timeout(self, ollama_provider, mock_settings, mock_metrics):
        """Test generation timeout."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb:

            mock_cb.call = AsyncMock(side_effect=TimeoutError("Timeout"))
            mock_cb.name = "llm_provider"

            with pytest.raises(TimeoutError):
                await ollama_provider.generate("Test prompt")

            mock_metrics.record_timeout.assert_called()

    @pytest.mark.asyncio
    async def test_generate_general_error(self, ollama_provider, mock_settings, mock_metrics):
        """Test generation with general error."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb:

            mock_cb.call = AsyncMock(side_effect=RuntimeError("Connection failed"))
            mock_cb.name = "llm_provider"

            with pytest.raises(RuntimeError):
                await ollama_provider.generate("Test prompt")

            mock_metrics.record_llm_call.assert_called()
            mock_metrics.record_circuit_breaker_failure.assert_called()


class TestOllamaProviderGenerateStream:
    """Test generate_stream method."""

    @pytest.mark.asyncio
    async def test_generate_stream_success(self, ollama_provider):
        """Test successful streaming generation."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            # Mock streaming response
            mock_lines = [
                b'{"response": "Hello"}',
                b'{"response": " world"}',
                b'{"done": true}'
            ]

            async def mock_iter():
                for line in mock_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = mock_iter()

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            chunks = []
            async for chunk in ollama_provider.generate_stream("Test prompt"):
                chunks.append(chunk)

            assert "Hello" in chunks
            assert " world" in chunks

    @pytest.mark.asyncio
    async def test_generate_stream_with_max_tokens(self, ollama_provider):
        """Test streaming with max_tokens."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_lines = [b'{"response": "Hello"}']

            async def mock_iter():
                for line in mock_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = mock_iter()

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            chunks = []
            async for chunk in ollama_provider.generate_stream("Test prompt", max_tokens=50):
                chunks.append(chunk)

            assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_generate_stream_json_decode_error(self, ollama_provider):
        """Test streaming handles JSON decode errors gracefully."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_lines = [
                b'invalid json',
                b'{"response": "Valid"}',
            ]

            async def mock_iter():
                for line in mock_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = mock_iter()

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            chunks = []
            async for chunk in ollama_provider.generate_stream("Test prompt"):
                chunks.append(chunk)

            assert "Valid" in chunks

    @pytest.mark.asyncio
    async def test_generate_stream_error(self, ollama_provider):
        """Test streaming error handling."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(side_effect=RuntimeError("Connection error"))
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            with pytest.raises(RuntimeError):
                async for _ in ollama_provider.generate_stream("Test prompt"):
                    pass


class TestOllamaProviderChat:
    """Test chat method."""

    @pytest.mark.asyncio
    async def test_chat_success(self, ollama_provider, mock_settings, mock_metrics):
        """Test successful chat completion."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb, \
             patch.object(ollama_provider, "_get_session") as mock_get_session:

            async def call_func(func):
                return await func()
            mock_cb.call = AsyncMock(side_effect=call_func)
            mock_cb.name = "llm_provider"

            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "message": {"content": "Chat response"}
            })

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            messages = [{"role": "user", "content": "Hello"}]
            result = await ollama_provider.chat(messages)

            assert result == "Chat response"
            mock_metrics.record_llm_call.assert_called()

    @pytest.mark.asyncio
    async def test_chat_with_max_tokens(self, ollama_provider, mock_settings, mock_metrics):
        """Test chat with max_tokens."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb, \
             patch.object(ollama_provider, "_get_session") as mock_get_session:

            async def call_func(func):
                return await func()
            mock_cb.call = AsyncMock(side_effect=call_func)
            mock_cb.name = "llm_provider"

            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "message": {"content": "Response"}
            })

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            messages = [{"role": "user", "content": "Hello"}]
            result = await ollama_provider.chat(messages, max_tokens=100)

            assert result == "Response"

    @pytest.mark.asyncio
    async def test_chat_circuit_breaker_open(self, ollama_provider, mock_settings, mock_metrics):
        """Test chat when circuit breaker is open."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb:

            mock_cb.call = AsyncMock(side_effect=CircuitBreakerOpenError("Circuit is open"))
            mock_cb.name = "llm_provider"

            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(CircuitBreakerOpenError):
                await ollama_provider.chat(messages)

            mock_metrics.record_circuit_breaker_rejection.assert_called()

    @pytest.mark.asyncio
    async def test_chat_timeout(self, ollama_provider, mock_settings, mock_metrics):
        """Test chat timeout."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb:

            mock_cb.call = AsyncMock(side_effect=TimeoutError("Timeout"))
            mock_cb.name = "llm_provider"

            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(TimeoutError):
                await ollama_provider.chat(messages)

            mock_metrics.record_timeout.assert_called()

    @pytest.mark.asyncio
    async def test_chat_general_error(self, ollama_provider, mock_settings, mock_metrics):
        """Test chat with general error."""
        with patch("backend.llm.ollama_provider.get_settings", return_value=mock_settings), \
             patch("backend.llm.ollama_provider.metrics", mock_metrics), \
             patch("backend.llm.ollama_provider.llm_circuit_breaker") as mock_cb:

            mock_cb.call = AsyncMock(side_effect=RuntimeError("Connection failed"))
            mock_cb.name = "llm_provider"

            messages = [{"role": "user", "content": "Hello"}]

            with pytest.raises(RuntimeError):
                await ollama_provider.chat(messages)

            mock_metrics.record_circuit_breaker_failure.assert_called()


class TestOllamaProviderChatStream:
    """Test chat_stream method."""

    @pytest.mark.asyncio
    async def test_chat_stream_success(self, ollama_provider):
        """Test successful chat streaming."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_lines = [
                b'{"message": {"content": "Hello"}}',
                b'{"message": {"content": " there"}}',
            ]

            async def mock_iter():
                for line in mock_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = mock_iter()

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            messages = [{"role": "user", "content": "Hi"}]
            chunks = []
            async for chunk in ollama_provider.chat_stream(messages):
                chunks.append(chunk)

            assert "Hello" in chunks
            assert " there" in chunks

    @pytest.mark.asyncio
    async def test_chat_stream_with_max_tokens(self, ollama_provider):
        """Test chat streaming with max_tokens."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_lines = [b'{"message": {"content": "Response"}}']

            async def mock_iter():
                for line in mock_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = mock_iter()

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            messages = [{"role": "user", "content": "Hi"}]
            chunks = []
            async for chunk in ollama_provider.chat_stream(messages, max_tokens=50):
                chunks.append(chunk)

            assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_chat_stream_json_decode_error(self, ollama_provider):
        """Test chat streaming handles JSON decode errors."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_lines = [
                b'not json',
                b'{"message": {"content": "Valid"}}',
            ]

            async def mock_iter():
                for line in mock_lines:
                    yield line

            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.content = mock_iter()

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            messages = [{"role": "user", "content": "Hi"}]
            chunks = []
            async for chunk in ollama_provider.chat_stream(messages):
                chunks.append(chunk)

            assert "Valid" in chunks

    @pytest.mark.asyncio
    async def test_chat_stream_error(self, ollama_provider):
        """Test chat streaming error handling."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(side_effect=RuntimeError("Connection error"))
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            messages = [{"role": "user", "content": "Hi"}]

            with pytest.raises(RuntimeError):
                async for _ in ollama_provider.chat_stream(messages):
                    pass


class TestOllamaProviderEmbed:
    """Test embed method."""

    @pytest.mark.asyncio
    async def test_embed_success(self, ollama_provider):
        """Test successful embedding generation."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = AsyncMock(return_value={
                "embedding": [0.1, 0.2, 0.3, 0.4]
            })

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            result = await ollama_provider.embed("Test text")

            assert result == [0.1, 0.2, 0.3, 0.4]

    @pytest.mark.asyncio
    async def test_embed_empty_embedding(self, ollama_provider):
        """Test embedding with empty result."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_response = AsyncMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json = AsyncMock(return_value={})

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            result = await ollama_provider.embed("Test text")

            assert result == []

    @pytest.mark.asyncio
    async def test_embed_error(self, ollama_provider):
        """Test embedding error handling."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(side_effect=RuntimeError("Connection error"))
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.post = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            with pytest.raises(RuntimeError):
                await ollama_provider.embed("Test text")


class TestOllamaProviderHealthCheck:
    """Test health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, ollama_provider):
        """Test successful health check."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status = 200

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.get = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            result = await ollama_provider.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, ollama_provider):
        """Test health check failure."""
        with patch.object(ollama_provider, "_get_session") as mock_get_session:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(side_effect=RuntimeError("Connection refused"))
            mock_context.__aexit__ = AsyncMock(return_value=None)

            mock_session = MagicMock()
            mock_session.get = MagicMock(return_value=mock_context)

            mock_get_session.return_value = mock_session

            result = await ollama_provider.health_check()

            assert result is False


class TestOllamaProviderProperties:
    """Test OllamaProvider properties."""

    def test_name_property(self, ollama_provider):
        """Test name property."""
        assert ollama_provider.name == "ollama:llama3.2"

    def test_supports_streaming_property(self, ollama_provider):
        """Test supports_streaming property."""
        assert ollama_provider.supports_streaming is True

    def test_supports_embeddings_property(self, ollama_provider):
        """Test supports_embeddings property."""
        assert ollama_provider.supports_embeddings is True
