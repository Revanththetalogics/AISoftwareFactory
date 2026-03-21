"""
Comprehensive tests for agents/model_router.py to achieve 100% coverage.

Covers:
- ModelProvider enum
- OllamaLLM class
- ModelRouter class
- get_model_router() singleton function
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import BaseModel

# Setup langchain mocks BEFORE importing model_router
mock_callback_manager = MagicMock()
mock_llm_base = MagicMock()

sys.modules['langchain.callbacks.manager'] = mock_callback_manager
sys.modules['langchain.llms.base'] = mock_llm_base

# Create mock LLM class that supports Pydantic-style initialization
class MockLLM(BaseModel):
    """Mock LLM base class that supports Pydantic Field initialization."""
    model_config = {'arbitrary_types_allowed': True, 'extra': 'allow'}

    # Define default field values as class attributes
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.7

mock_llm_base.LLM = MockLLM
mock_callback_manager.CallbackManagerForLLMRun = MagicMock()

from backend.agents.model_router import (  # noqa: E402
    ModelProvider,
    ModelRouter,
    OllamaLLM,
    get_model_router,
)


class TestModelProvider:
    """Tests for ModelProvider enum."""

    def test_ollama_value(self):
        """Test OLLAMA enum value."""
        assert ModelProvider.OLLAMA.value == "ollama"

    def test_openai_value(self):
        """Test OPENAI enum value."""
        assert ModelProvider.OPENAI.value == "openai"

    def test_anthropic_value(self):
        """Test ANTHROPIC enum value."""
        assert ModelProvider.ANTHROPIC.value == "anthropic"

    def test_enum_is_string(self):
        """Test enum inherits from str."""
        assert isinstance(ModelProvider.OLLAMA, str)


class TestOllamaLLM:
    """Tests for OllamaLLM class."""

    def test_init_defaults(self):
        """Test default initialization."""
        llm = OllamaLLM()

        # Access field values - they should be actual values, not FieldInfo
        assert str(llm.model) == "qwen2.5-coder"
        assert str(llm.base_url) == "http://localhost:11434"
        assert float(llm.temperature) == 0.7

    def test_init_custom_values(self):
        """Test initialization with custom values."""
        llm = OllamaLLM(
            model="deepseek-coder",
            base_url="http://custom:1234",
            temperature=0.5
        )

        # Access field values directly
        assert str(llm.model) == "deepseek-coder"
        assert str(llm.base_url) == "http://custom:1234"
        assert float(llm.temperature) == 0.5

    def test_llm_type_property(self):
        """Test _llm_type property."""
        llm = OllamaLLM()
        assert llm._llm_type == "ollama"

    def test_call_returns_stub_response(self):
        """Test _call returns stub response."""
        llm = OllamaLLM(model="test-model")
        prompt = "Test prompt"

        result = llm._call(prompt)

        assert "[Stub Response from test-model]" in result
        assert "11" in result  # Length of "Test prompt" is 11

    def test_call_with_stop_sequences(self):
        """Test _call with stop sequences."""
        llm = OllamaLLM()
        result = llm._call("prompt", stop=["STOP"])
        assert "[Stub Response" in result

    def test_call_with_run_manager(self):
        """Test _call with run_manager."""
        llm = OllamaLLM()
        mock_run_manager = Mock()
        result = llm._call("prompt", run_manager=mock_run_manager)
        assert "[Stub Response" in result

    def test_call_with_kwargs(self):
        """Test _call with additional kwargs."""
        llm = OllamaLLM()
        result = llm._call("prompt", custom_param="value")
        assert "[Stub Response" in result

    def test_identifying_params_property(self):
        """Test _identifying_params property."""
        llm = OllamaLLM(model="test-model", base_url="http://test:123", temperature=0.9)
        params = llm._identifying_params

        assert params["model"] == "test-model"
        assert params["base_url"] == "http://test:123"
        assert params["temperature"] == 0.9


class TestModelRouter:
    """Tests for ModelRouter class."""

    @patch('backend.agents.model_router.get_settings')
    def test_init(self, mock_get_settings):
        """Test initialization."""
        mock_settings = Mock()
        mock_get_settings.return_value = mock_settings

        router = ModelRouter()

        assert router.settings == mock_settings
        assert router._models == {}
        assert router._default_model == "qwen2.5-coder"

    @patch('backend.agents.model_router.get_settings')
    def test_get_llm_creates_ollama_llm(self, mock_get_settings):
        """Test get_llm creates OllamaLLM for Ollama provider."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        llm = router.get_llm(task_type="code", provider=ModelProvider.OLLAMA)

        assert isinstance(llm, OllamaLLM)
        assert llm.model == "qwen2.5-coder"

    @patch('backend.agents.model_router.get_settings')
    def test_get_llm_caches_model(self, mock_get_settings):
        """Test get_llm caches model instances."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        llm1 = router.get_llm(task_type="code")
        llm2 = router.get_llm(task_type="code")

        assert llm1 is llm2
        assert len(router._models) == 1

    @patch('backend.agents.model_router.get_settings')
    def test_get_llm_different_models(self, mock_get_settings):
        """Test get_llm creates different instances for different models."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        llm1 = router.get_llm(model_name="model1")
        llm2 = router.get_llm(model_name="model2")

        assert llm1 is not llm2
        assert len(router._models) == 2

    @patch('backend.agents.model_router.get_settings')
    def test_get_llm_unsupported_provider(self, mock_get_settings):
        """Test get_llm raises error for unsupported provider."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        with pytest.raises(ValueError, match="not yet implemented"):
            router.get_llm(provider=ModelProvider.OPENAI)

    @patch('backend.agents.model_router.get_settings')
    def test_get_llm_anthropic_provider(self, mock_get_settings):
        """Test get_llm raises error for Anthropic provider."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        with pytest.raises(ValueError, match="not yet implemented"):
            router.get_llm(provider=ModelProvider.ANTHROPIC)

    @patch('backend.agents.model_router.get_settings')
    def test_get_default_model_for_task_code(self, mock_get_settings):
        """Test default model for code task."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        model = router._get_default_model_for_task("code")
        assert model == "qwen2.5-coder"

    @patch('backend.agents.model_router.get_settings')
    def test_get_default_model_for_task_analysis(self, mock_get_settings):
        """Test default model for analysis task."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        model = router._get_default_model_for_task("analysis")
        assert model == "deepseek-coder"

    @patch('backend.agents.model_router.get_settings')
    def test_get_default_model_for_task_general(self, mock_get_settings):
        """Test default model for general task."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        model = router._get_default_model_for_task("general")
        assert model == "llama3.2"

    @patch('backend.agents.model_router.get_settings')
    def test_get_default_model_for_task_chat(self, mock_get_settings):
        """Test default model for chat task."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        model = router._get_default_model_for_task("chat")
        assert model == "qwen2.5"

    @patch('backend.agents.model_router.get_settings')
    def test_get_default_model_for_task_unknown(self, mock_get_settings):
        """Test default model for unknown task type."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        model = router._get_default_model_for_task("unknown")
        assert model == "qwen2.5-coder"  # Default model

    @patch('backend.agents.model_router.get_settings')
    def test_list_available_models(self, mock_get_settings):
        """Test list_available_models returns correct structure."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        models = router.list_available_models()

        assert "ollama" in models
        assert "openai" in models
        assert "anthropic" in models
        assert "qwen2.5-coder" in models["ollama"]
        assert "gpt-4" in models["openai"]
        assert "claude-3" in models["anthropic"]

    @patch('backend.agents.model_router.get_settings')
    def test_get_model_info_qwen(self, mock_get_settings):
        """Test get_model_info for qwen2.5-coder."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        info = router.get_model_info("qwen2.5-coder")

        assert info["provider"] == "ollama"
        assert info["description"] == "Code-focused model"
        assert info["context_length"] == 32768

    @patch('backend.agents.model_router.get_settings')
    def test_get_model_info_deepseek(self, mock_get_settings):
        """Test get_model_info for deepseek-coder."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        info = router.get_model_info("deepseek-coder")

        assert info["provider"] == "ollama"
        assert info["context_length"] == 16384

    @patch('backend.agents.model_router.get_settings')
    def test_get_model_info_llama(self, mock_get_settings):
        """Test get_model_info for llama3.2."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        info = router.get_model_info("llama3.2")

        assert info["context_length"] == 128000

    @patch('backend.agents.model_router.get_settings')
    def test_get_model_info_unknown(self, mock_get_settings):
        """Test get_model_info for unknown model."""
        mock_get_settings.return_value = Mock()
        router = ModelRouter()

        info = router.get_model_info("unknown-model")

        assert info == {"error": "Model not found"}


class TestGetModelRouter:
    """Tests for get_model_router singleton function."""

    def test_returns_model_router_instance(self):
        """Test get_model_router returns ModelRouter."""
        # Reset singleton for test isolation
        import backend.agents.model_router as module
        module._model_router = None

        with patch('backend.agents.model_router.get_settings') as mock_settings:
            mock_settings.return_value = Mock()
            router = get_model_router()
            assert isinstance(router, ModelRouter)

    def test_returns_same_instance(self):
        """Test get_model_router returns singleton."""
        import backend.agents.model_router as module
        module._model_router = None

        with patch('backend.agents.model_router.get_settings') as mock_settings:
            mock_settings.return_value = Mock()
            router1 = get_model_router()
            router2 = get_model_router()
            assert router1 is router2

    def test_creates_new_when_none(self):
        """Test get_model_router creates new when None."""
        import backend.agents.model_router as module
        module._model_router = None

        with patch('backend.agents.model_router.get_settings') as mock_settings:
            mock_settings.return_value = Mock()
            router = get_model_router()
            assert router is not None
            assert module._model_router is router
