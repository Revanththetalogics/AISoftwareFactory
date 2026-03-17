"""
Tests for Model Router.
"""

import pytest

from backend.llm.router import ModelRouter, ModelConfig
from backend.llm.providers.base import LLMRequest, LLMResponse
from backend.llm.providers.ollama import OllamaProvider


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


class TestModelRouter:
    """Test cases for ModelRouter."""
    
    def setup_method(self):
        """Create fresh router for each test."""
        self.router = ModelRouter()
    
    def test_router_initialization(self):
        """Test router initialization."""
        assert self.router.default_model == "llama2"
        assert len(self.router.model_configs) > 0
    
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
    
    def test_select_model(self):
        """Test model selection by task type."""
        coding_model = self.router.select_model("coding")
        chat_model = self.router.select_model("chat")
        
        assert coding_model == "deepseek-coder"
        assert chat_model == "qwen"
    
    def test_select_model_default(self):
        """Test model selection fallback to default."""
        model = self.router.select_model("unknown_task")
        
        assert model == "llama2"  # default
    
    def test_get_model_info(self):
        """Test getting model information."""
        info = self.router.get_model_info("llama2")
        
        assert info is not None
        assert info.name == "llama2"
        assert info.provider == "ollama"
    
    def test_get_model_info_not_found(self):
        """Test getting info for non-existent model."""
        info = self.router.get_model_info("nonexistent")
        
        assert info is None
    
    def test_list_models(self):
        """Test listing models."""
        models = self.router.list_models()
        
        assert "llama2" in models
        assert "deepseek-coder" in models
        assert "qwen" in models
    
    def test_get_available_providers(self):
        """Test getting available providers."""
        provider = OllamaProvider()
        self.router.register_provider(provider)
        
        providers = self.router.get_available_providers()
        
        assert "ollama" in providers


class TestModelRouterFallbacks:
    """Test cases for router fallback logic."""
    
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
    async def test_generate_fallback(self):
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
    async def test_health_check(self):
        """Test health check."""
        from backend.tests.llm.test_base_provider import MockProvider
        
        provider = MockProvider()
        self.router.register_provider(provider)
        
        health = await self.router.health_check()
        
        assert "mock" in health
        assert health["mock"] is True
