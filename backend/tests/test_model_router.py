"""
Tests for Model Router (agents).

Tests for ModelRouter and OllamaLLM in backend/agents/model_router.py.
"""

from unittest.mock import MagicMock

import pytest

# Check if langchain is available, skip tests if not
try:
    from langchain.llms.base import LLM
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create mocks for testing
    LLM = MagicMock

# Skip all tests in this module if langchain is not available
pytestmark = pytest.mark.skipif(
    not LANGCHAIN_AVAILABLE,
    reason="langchain not installed"
)

if LANGCHAIN_AVAILABLE:
    from backend.agents.model_router import (
        ModelProvider,
        ModelRouter,
        OllamaLLM,
        get_model_router,
    )
else:
    # Define dummy classes for type hints when langchain is not available
    ModelProvider = MagicMock
    ModelRouter = MagicMock
    OllamaLLM = MagicMock
    get_model_router = MagicMock


class TestModelProvider:
    """Test ModelProvider enum."""

    def test_ollama_value(self):
        """Test OLLAMA enum value."""
        assert ModelProvider.OLLAMA.value == "ollama"

    def test_openai_value(self):
        """Test OPENAI enum value."""
        assert ModelProvider.OPENAI.value == "openai"

    def test_anthropic_value(self):
        """Test ANTHROPIC enum value."""
        assert ModelProvider.ANTHROPIC.value == "anthropic"


class TestOllamaLLM:
    """Test OllamaLLM class."""

    def test_default_initialization(self):
        """Test default OllamaLLM initialization."""
        llm = OllamaLLM()

        # Access field values directly - now inherits from Pydantic BaseModel
        assert llm.model == "qwen2.5-coder"
        assert llm.base_url == "http://localhost:11434"
        assert llm.temperature == 0.7

        # Also test model_dump works now
        model_dict = llm.model_dump()
        assert model_dict["model"] == "qwen2.5-coder"

    def test_custom_initialization(self):
        """Test OllamaLLM with custom values."""
        llm = OllamaLLM(
            model="llama3.2",
            base_url="http://custom:8080",
            temperature=0.5
        )

        assert llm.model == "llama3.2"
        assert llm.base_url == "http://custom:8080"
        assert llm.temperature == 0.5

    def test_llm_type(self):
        """Test _llm_type property."""
        llm = OllamaLLM()

        assert llm._llm_type == "ollama"

    def test_call_returns_stub_response(self):
        """Test _call returns stub response."""
        llm = OllamaLLM(model="test-model")

        result = llm._call("Test prompt for model")

        assert "[Stub Response from test-model]" in result
        assert "21" in result  # Length of prompt

    def test_call_with_stop_and_run_manager(self):
        """Test _call with stop sequences and run manager."""
        llm = OllamaLLM()

        result = llm._call(
            "Short",
            stop=["stop1", "stop2"],
            run_manager=MagicMock()
        )

        assert "[Stub Response from" in result

    def test_identifying_params(self):
        """Test _identifying_params property."""
        llm = OllamaLLM(
            model="custom-model",
            base_url="http://custom:9999",
            temperature=0.3
        )

        params = llm._identifying_params

        assert params["model"] == "custom-model"
        assert params["base_url"] == "http://custom:9999"
        assert params["temperature"] == 0.3


class TestModelRouter:
    """Test ModelRouter class."""

    def setup_method(self):
        """Create fresh router for each test."""
        # Reset singleton
        import backend.agents.model_router as mr
        mr._model_router = None
        self.router = ModelRouter()

    def test_initialization(self):
        """Test ModelRouter initialization."""
        assert self.router._default_model == "qwen2.5-coder"
        assert isinstance(self.router._models, dict)
        assert len(self.router._models) == 0

    def test_get_llm_default(self):
        """Test get_llm with defaults."""
        llm = self.router.get_llm()

        assert isinstance(llm, OllamaLLM)

    def test_get_llm_code_task(self):
        """Test get_llm for code task."""
        llm = self.router.get_llm(task_type="code")

        assert isinstance(llm, OllamaLLM)
        assert llm.model == "qwen2.5-coder"

    def test_get_llm_analysis_task(self):
        """Test get_llm for analysis task."""
        llm = self.router.get_llm(task_type="analysis")

        assert isinstance(llm, OllamaLLM)
        assert llm.model == "deepseek-coder"

    def test_get_llm_general_task(self):
        """Test get_llm for general task."""
        llm = self.router.get_llm(task_type="general")

        assert isinstance(llm, OllamaLLM)
        assert llm.model == "llama3.2"

    def test_get_llm_chat_task(self):
        """Test get_llm for chat task."""
        llm = self.router.get_llm(task_type="chat")

        assert isinstance(llm, OllamaLLM)
        assert llm.model == "qwen2.5"

    def test_get_llm_custom_model(self):
        """Test get_llm with custom model name."""
        llm = self.router.get_llm(model_name="custom-model")

        assert isinstance(llm, OllamaLLM)
        assert llm.model == "custom-model"

    def test_get_llm_caches_instances(self):
        """Test that get_llm caches LLM instances."""
        llm1 = self.router.get_llm(task_type="code")
        llm2 = self.router.get_llm(task_type="code")

        assert llm1 is llm2

    def test_get_llm_different_models_not_shared(self):
        """Test different models get separate instances."""
        llm1 = self.router.get_llm(model_name="model-a")
        llm2 = self.router.get_llm(model_name="model-b")

        assert llm1 is not llm2
        assert llm1.model != llm2.model

    def test_get_llm_unsupported_provider(self):
        """Test get_llm with unsupported provider."""
        with pytest.raises(ValueError) as exc_info:
            self.router.get_llm(provider=ModelProvider.OPENAI)

        assert "not yet implemented" in str(exc_info.value)

    def test_get_llm_anthropic_provider_error(self):
        """Test get_llm with Anthropic provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            self.router.get_llm(provider=ModelProvider.ANTHROPIC)

        assert "not yet implemented" in str(exc_info.value)

    def test_get_default_model_for_task_code(self):
        """Test _get_default_model_for_task for code."""
        model = self.router._get_default_model_for_task("code")

        assert model == "qwen2.5-coder"

    def test_get_default_model_for_task_analysis(self):
        """Test _get_default_model_for_task for analysis."""
        model = self.router._get_default_model_for_task("analysis")

        assert model == "deepseek-coder"

    def test_get_default_model_for_task_general(self):
        """Test _get_default_model_for_task for general."""
        model = self.router._get_default_model_for_task("general")

        assert model == "llama3.2"

    def test_get_default_model_for_task_chat(self):
        """Test _get_default_model_for_task for chat."""
        model = self.router._get_default_model_for_task("chat")

        assert model == "qwen2.5"

    def test_get_default_model_for_task_unknown(self):
        """Test _get_default_model_for_task for unknown task type."""
        model = self.router._get_default_model_for_task("unknown")

        assert model == "qwen2.5-coder"  # Falls back to default

    def test_list_available_models(self):
        """Test list_available_models returns dict of models."""
        models = self.router.list_available_models()

        assert ModelProvider.OLLAMA.value in models
        assert ModelProvider.OPENAI.value in models
        assert ModelProvider.ANTHROPIC.value in models

        # Check Ollama models
        ollama_models = models[ModelProvider.OLLAMA.value]
        assert "qwen2.5-coder" in ollama_models
        assert "deepseek-coder" in ollama_models
        assert "llama3.2" in ollama_models
        assert "mixtral" in ollama_models

    def test_get_model_info_known(self):
        """Test get_model_info for known model."""
        info = self.router.get_model_info("qwen2.5-coder")

        assert info["provider"] == "ollama"
        assert info["description"] == "Code-focused model"
        assert info["context_length"] == 32768

    def test_get_model_info_deepseek(self):
        """Test get_model_info for deepseek-coder."""
        info = self.router.get_model_info("deepseek-coder")

        assert info["provider"] == "ollama"
        assert info["description"] == "DeepSeek Coder model"
        assert info["context_length"] == 16384

    def test_get_model_info_llama(self):
        """Test get_model_info for llama3.2."""
        info = self.router.get_model_info("llama3.2")

        assert info["provider"] == "ollama"
        assert info["description"] == "General purpose model"
        assert info["context_length"] == 128000

    def test_get_model_info_unknown(self):
        """Test get_model_info for unknown model."""
        info = self.router.get_model_info("unknown-model")

        assert info == {"error": "Model not found"}


class TestGetModelRouter:
    """Test get_model_router singleton function."""

    def setup_method(self):
        """Reset singleton before each test."""
        import backend.agents.model_router as mr
        mr._model_router = None

    def test_creates_singleton(self):
        """Test get_model_router creates singleton."""
        router1 = get_model_router()
        router2 = get_model_router()

        assert router1 is router2

    def test_returns_model_router_instance(self):
        """Test get_model_router returns ModelRouter instance."""
        router = get_model_router()

        assert isinstance(router, ModelRouter)

    def test_singleton_persists(self):
        """Test singleton persists across calls."""
        router1 = get_model_router()
        # Add a model to router1
        router1.get_llm(model_name="test-model")

        router2 = get_model_router()
        # Should have same cached models
        assert "ollama:test-model" in router2._models


class TestIntegration:
    """Integration tests for model router."""

    def setup_method(self):
        """Reset singleton before each test."""
        import backend.agents.model_router as mr
        mr._model_router = None

    def test_full_workflow(self):
        """Test complete workflow: get router, get LLM, call it."""
        router = get_model_router()
        llm = router.get_llm(task_type="code")

        # Call the LLM using _call method (stub)
        result = llm._call("Write a function to add two numbers")

        assert "[Stub Response from" in result
        assert "qwen2.5-coder" in result

    def test_multiple_task_types(self):
        """Test getting LLMs for multiple task types."""
        router = get_model_router()

        llms = {
            "code": router.get_llm(task_type="code"),
            "analysis": router.get_llm(task_type="analysis"),
            "general": router.get_llm(task_type="general"),
            "chat": router.get_llm(task_type="chat"),
        }

        # Verify each has correct model
        assert llms["code"].model == "qwen2.5-coder"
        assert llms["analysis"].model == "deepseek-coder"
        assert llms["general"].model == "llama3.2"
        assert llms["chat"].model == "qwen2.5"

        # All should be able to generate responses using _call
        for task, llm in llms.items():
            result = llm._call(f"Test prompt for {task}")
            assert "[Stub Response from" in result
