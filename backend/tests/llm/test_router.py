"""
Tests for Model Router.
"""

import pytest

from backend.llm.providers.base import LLMRequest, LLMResponse
from backend.llm.providers.ollama import OllamaProvider
from backend.llm.router import ModelConfig, ModelRouter


class TestModelConfig:
    """Test cases for ModelConfig."""

    def test_config_creation(self):
        """Test creating model config."""
        config = ModelConfig(
            name="test-model",
            provider="test-provider",
            priority=5,
            capabilities=["chat", "code"],
        )

        assert config.name == "test-model"
        assert config.provider == "test-provider"
        assert config.priority == 5
        assert config.capabilities == ["chat", "code"]

    def test_config_defaults(self):
        """Test model config defaults."""
        config = ModelConfig(name="test", provider="ollama")

        assert config.priority == 1
        assert config.capabilities == []
        assert config.context_window == 4096
        assert config.cost_per_1k_tokens == 0.0


class TestModelRouter:
    """Test cases for ModelRouter."""

    def setup_method(self):
        """Create fresh router for each test."""
        self.router = ModelRouter()

    def test_router_initialization(self):
        """Test router initialization."""
        assert self.router.default_model == "llama3.2"
        assert len(self.router.model_configs) > 0

    def test_router_custom_default_model(self):
        """Test router with custom default model."""
        router = ModelRouter(default_model="custom-model")

        assert router.default_model == "custom-model"

    def test_register_provider(self):
        """Test registering a provider."""
        provider = OllamaProvider()

        self.router.register_provider(provider)

        assert "ollama" in self.router.providers

    def test_get_provider(self):
        """Test getting a provider."""
        provider = OllamaProvider()
        self.router.register_provider(provider)

        retrieved = self.router.get_provider("ollama")

        assert retrieved is provider

    def test_get_provider_not_found(self):
        """Test getting non-existent provider."""
        result = self.router.get_provider("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_is_provider_available_true(self):
        """Test is_provider_available when available."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider = MockProvider(name="mock", default_model="mock-model")
        provider._available = True
        self.router.register_provider(provider)

        result = await self.router.is_provider_available("mock")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_provider_available_not_registered(self):
        """Test is_provider_available for non-registered provider."""
        result = await self.router.is_provider_available("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_provider_available_unavailable(self):
        """Test is_provider_available when provider unavailable."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider = MockProvider(name="mock", default_model="mock-model")
        provider._available = False
        self.router.register_provider(provider)

        result = await self.router.is_provider_available("mock")

        assert result is False

    def test_select_model(self):
        """Test model selection by task type."""
        coding_model = self.router.select_model("coding")
        chat_model = self.router.select_model("chat")

        assert coding_model == "deepseek-coder-v2"
        assert chat_model == "qwen2.5"

    def test_select_model_default(self):
        """Test model selection fallback to default."""
        model = self.router.select_model("unknown_task")

        assert model == "llama3.2"  # default

    def test_select_model_code_generation(self):
        """Test model selection for code_generation task."""
        model = self.router.select_model("code_generation")

        assert model == "deepseek-coder-v2"

    def test_select_model_code_review(self):
        """Test model selection for code_review task."""
        model = self.router.select_model("code_review")

        assert model == "deepseek-coder-v2"

    def test_select_model_reasoning(self):
        """Test model selection for reasoning task."""
        model = self.router.select_model("reasoning")

        assert model == "mixtral:8x7b"

    def test_select_model_general(self):
        """Test model selection for general task."""
        model = self.router.select_model("general")

        assert model == "llama3.2"

    def test_select_model_unconfigured_fallback(self):
        """Test model selection falls back when model not in configs."""
        # Clear configs
        original_configs = self.router.model_configs.copy()
        self.router.model_configs.clear()

        model = self.router.select_model("coding")

        assert model == "llama3.2"  # Falls back to default

        # Restore
        self.router.model_configs = original_configs

    def test_get_model_info(self):
        """Test getting model information."""
        info = self.router.get_model_info("llama3.2")

        assert info is not None
        assert info.name == "llama3.2"
        assert info.provider == "ollama"

    def test_get_model_info_not_found(self):
        """Test getting info for non-existent model."""
        info = self.router.get_model_info("nonexistent")

        assert info is None

    def test_list_models(self):
        """Test listing models."""
        models = self.router.list_models()

        assert "llama3.2" in models
        assert "deepseek-coder-v2" in models
        assert "qwen2.5" in models

    def test_get_available_providers(self):
        """Test getting available providers."""
        provider = OllamaProvider()
        self.router.register_provider(provider)

        providers = self.router.get_available_providers()

        assert "ollama" in providers


class TestModelRouterGenerate:
    """Test cases for router generate method."""

    def setup_method(self):
        """Create fresh router for each test."""
        self.router = ModelRouter()

    @pytest.mark.asyncio
    async def test_generate_with_mock_provider(self):
        """Test generation with mock provider."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider = MockProvider(name="mock", default_model="mock-model")
        self.router.register_provider(provider)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request, model="mock-model")

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_uses_request_model(self):
        """Test generate uses model from request."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider = MockProvider(name="ollama", default_model="llama3.2")
        self.router.register_provider(provider)

        request = LLMRequest(prompt="Hello!", model="llama3.2")
        response = await self.router.generate(request)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_uses_default_model(self):
        """Test generate uses default model when none specified."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider = MockProvider(name="ollama", default_model="llama3.2")
        self.router.register_provider(provider)

        request = LLMRequest(prompt="Hello!")  # No model specified
        response = await self.router.generate(request)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_primary_provider_unavailable(self):
        """Test generate when primary provider is unavailable."""
        from backend.tests.llm.test_base_provider import MockProvider

        # Unavailable primary
        provider = MockProvider(name="ollama", default_model="llama3.2")
        provider._available = False
        self.router.register_provider(provider)

        # Available fallback
        fallback = MockProvider(name="fallback", default_model="fallback-model")
        fallback._available = True
        self.router.register_provider(fallback)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request, model="llama3.2")

        # Should fallback
        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_primary_provider_fails(self):
        """Test generate when primary provider returns error response."""
        from unittest.mock import AsyncMock

        from backend.tests.llm.test_base_provider import MockProvider

        # Primary that returns error
        provider = MockProvider(name="ollama", default_model="llama3.2")
        provider._available = True
        provider.generate = AsyncMock(return_value=LLMResponse(
            text="",
            model="llama3.2",
            error="Generation failed"
        ))
        self.router.register_provider(provider)

        # Working fallback
        fallback = MockProvider(name="fallback", default_model="fallback-model")
        fallback._available = True
        self.router.register_provider(fallback)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request, model="llama3.2")

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_primary_provider_exception(self):
        """Test generate when primary provider raises exception."""
        from unittest.mock import AsyncMock

        from backend.tests.llm.test_base_provider import MockProvider

        # Primary that raises exception
        provider = MockProvider(name="ollama", default_model="llama3.2")
        provider._available = True
        provider.is_available = AsyncMock(side_effect=RuntimeError("Connection error"))
        self.router.register_provider(provider)

        # Working fallback
        fallback = MockProvider(name="fallback", default_model="fallback-model")
        fallback._available = True
        self.router.register_provider(fallback)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request, model="llama3.2")

        assert response.success is True

    @pytest.mark.asyncio
    async def test_generate_no_config_for_model(self):
        """Test generate when model has no config."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider = MockProvider(name="mock", default_model="mock-model")
        self.router.register_provider(provider)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request, model="unknown-model")

        # Should try fallbacks
        assert response.success is True


class TestModelRouterFallbacks:
    """Test cases for router fallback logic."""

    def setup_method(self):
        """Create fresh router for each test."""
        self.router = ModelRouter()

    @pytest.mark.asyncio
    async def test_fallback_success(self):
        """Test fallback when primary provider fails."""
        from backend.tests.llm.test_base_provider import MockProvider

        # Create failing provider
        failing_provider = MockProvider(name="failing", default_model="failing-model")
        failing_provider._available = False

        # Create working fallback
        working_provider = MockProvider(name="working", default_model="working-model")

        self.router.register_provider(failing_provider)
        self.router.register_provider(working_provider)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request)

        # Should get response from working provider
        assert response.success is True

    @pytest.mark.asyncio
    async def test_fallback_provider_returns_error(self):
        """Test fallback when provider returns error response."""
        from unittest.mock import AsyncMock

        from backend.tests.llm.test_base_provider import MockProvider

        # First fallback returns error
        provider1 = MockProvider(name="provider1", default_model="model1")
        provider1._available = True
        provider1.generate = AsyncMock(return_value=LLMResponse(
            text="",
            model="model1",
            error="Provider failed"
        ))
        self.router.register_provider(provider1)

        # Second fallback works
        provider2 = MockProvider(name="provider2", default_model="model2")
        provider2._available = True
        self.router.register_provider(provider2)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_fallback_provider_exception(self):
        """Test fallback when provider raises exception."""
        from unittest.mock import AsyncMock

        from backend.tests.llm.test_base_provider import MockProvider

        # First fallback raises exception
        provider1 = MockProvider(name="provider1", default_model="model1")
        provider1._available = True
        provider1.generate = AsyncMock(side_effect=RuntimeError("Connection error"))
        self.router.register_provider(provider1)

        # Second fallback works
        provider2 = MockProvider(name="provider2", default_model="model2")
        provider2._available = True
        self.router.register_provider(provider2)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test when all providers fail."""
        from backend.tests.llm.test_base_provider import MockProvider

        # All unavailable
        provider1 = MockProvider(name="provider1", default_model="model1")
        provider1._available = False
        self.router.register_provider(provider1)

        provider2 = MockProvider(name="provider2", default_model="model2")
        provider2._available = False
        self.router.register_provider(provider2)

        request = LLMRequest(prompt="Hello!")
        response = await self.router.generate(request)

        assert response.success is False
        assert "unavailable" in response.error.lower()


class TestModelRouterHealthCheck:
    """Test cases for router health check."""

    def setup_method(self):
        """Create fresh router for each test."""
        self.router = ModelRouter()

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self):
        """Test health check with all healthy providers."""
        from backend.tests.llm.test_base_provider import MockProvider

        provider1 = MockProvider(name="provider1", default_model="model1")
        provider1._available = True
        provider2 = MockProvider(name="provider2", default_model="model2")
        provider2._available = True

        self.router.register_provider(provider1)
        self.router.register_provider(provider2)

        health = await self.router.health_check()

        assert health["provider1"] is True
        assert health["provider2"] is True

    @pytest.mark.asyncio
    async def test_health_check_some_unhealthy(self):
        """Test health check with some unhealthy providers."""
        from backend.tests.llm.test_base_provider import MockProvider

        healthy = MockProvider(name="healthy", default_model="model1")
        healthy._available = True
        unhealthy = MockProvider(name="unhealthy", default_model="model2")
        unhealthy._available = False

        self.router.register_provider(healthy)
        self.router.register_provider(unhealthy)

        health = await self.router.health_check()

        assert health["healthy"] is True
        assert health["unhealthy"] is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check when provider raises exception."""
        from unittest.mock import AsyncMock

        from backend.tests.llm.test_base_provider import MockProvider

        # Provider that raises exception
        provider = MockProvider(name="broken", default_model="model1")
        provider.is_available = AsyncMock(side_effect=RuntimeError("Connection error"))

        self.router.register_provider(provider)

        health = await self.router.health_check()

        assert health["broken"] is False

    @pytest.mark.asyncio
    async def test_health_check_no_providers(self):
        """Test health check with no providers."""
        health = await self.router.health_check()

        assert health == {}
