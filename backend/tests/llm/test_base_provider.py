"""
Tests for Base LLM Provider.
"""

import pytest

from backend.llm.providers.base import (
    BaseLLMProvider,
    LLMRequest,
    LLMResponse,
    ModelCapability,
)


class MockProvider(BaseLLMProvider):
    """Mock provider for testing."""

    def __init__(self, name: str = "mock", default_model: str = "mock-model"):
        super().__init__(name=name, default_model=default_model)
        self._available = True

    async def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=f"Generated: {request.prompt[:20]}...",
            model=self.default_model,
            prompt_tokens=10,
            completion_tokens=5,
        )

    async def is_available(self) -> bool:
        return self._available

    def get_available_models(self):
        return [self.default_model]


class TestLLMRequest:
    """Test cases for LLMRequest."""

    def test_request_creation(self):
        """Test creating a request."""
        request = LLMRequest(
            prompt="Hello, world!",
            model="test-model",
            max_tokens=100,
            temperature=0.5,
        )

        assert request.prompt == "Hello, world!"
        assert request.model == "test-model"
        assert request.max_tokens == 100
        assert request.temperature == 0.5

    def test_request_defaults(self):
        """Test request default values."""
        request = LLMRequest(prompt="Test")

        assert request.max_tokens == 1024
        assert request.temperature == 0.7
        assert request.top_p == 0.9

    def test_request_to_dict(self):
        """Test converting request to dict."""
        request = LLMRequest(prompt="Test", model="model-1")

        result = request.to_dict()

        assert result["prompt"] == "Test"
        assert result["model"] == "model-1"


class TestLLMResponse:
    """Test cases for LLMResponse."""

    def test_response_creation(self):
        """Test creating a response."""
        response = LLMResponse(
            text="Generated text",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
        )

        assert response.text == "Generated text"
        assert response.model == "test-model"
        assert response.prompt_tokens == 10
        assert response.completion_tokens == 5
        assert response.total_tokens == 15

    def test_response_success(self):
        """Test response success property."""
        success_response = LLMResponse(text="OK", model="test")
        error_response = LLMResponse(text="", model="test", error="Failed")

        assert success_response.success is True
        assert error_response.success is False

    def test_response_to_dict(self):
        """Test converting response to dict."""
        response = LLMResponse(text="OK", model="test")

        result = response.to_dict()

        assert result["text"] == "OK"
        assert result["model"] == "test"
        assert result["success"] is True


class TestBaseLLMProvider:
    """Test cases for BaseLLMProvider."""

    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = MockProvider(name="test", default_model="model-x")

        assert provider.name == "test"
        assert provider.default_model == "model-x"

    @pytest.mark.asyncio
    async def test_provider_generate(self):
        """Test provider generate method."""
        provider = MockProvider()
        request = LLMRequest(prompt="Hello")

        response = await provider.generate(request)

        assert response.success is True
        assert "Generated:" in response.text

    @pytest.mark.asyncio
    async def test_provider_availability(self):
        """Test provider availability check."""
        provider = MockProvider()

        available = await provider.is_available()

        assert available is True

    def test_provider_capabilities(self):
        """Test provider capabilities."""
        provider = MockProvider()

        capabilities = provider.get_capabilities()

        assert ModelCapability.TEXT_GENERATION in capabilities
        assert ModelCapability.CHAT in capabilities

    def test_estimate_tokens(self):
        """Test token estimation."""
        provider = MockProvider()

        # Rough estimate: 1 token ≈ 4 characters
        tokens = provider.estimate_tokens("Hello world")  # 11 chars

        assert tokens == 2  # 11 // 4 = 2

    def test_create_error_response(self):
        """Test error response creation."""
        provider = MockProvider()

        response = provider._create_error_response("Test error")

        assert response.success is False
        assert response.error == "Test error"
