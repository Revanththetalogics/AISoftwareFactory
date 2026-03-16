"""
Model Router for AI Software Factory.

This module provides a unified interface for routing requests to different
LLM providers, with Ollama as the primary local inference engine.
"""

from enum import Enum
from typing import Any, Dict, Optional

from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field

from backend.core.config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class OllamaLLM(LLM):
    """
    LangChain-compatible LLM wrapper for Ollama.
    
    This is a stub implementation that will be fully integrated in Phase 3
    when the Ollama service is configured.
    
    TODO: Full Ollama integration in Phase 3
    """
    
    model: str = Field(default="qwen2.5-coder")
    base_url: str = Field(default="http://localhost:11434")
    temperature: float = Field(default=0.7)
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call the Ollama model.
        
        This is currently a stub that returns a placeholder response.
        Full implementation will connect to Ollama API in Phase 3.
        """
        logger.debug("OllamaLLM called", model=self.model, prompt_length=len(prompt))
        
        # Stub implementation - returns placeholder
        # TODO: Implement actual Ollama API call in Phase 3
        return f"[Stub Response from {self.model}]: Processing prompt of length {len(prompt)}"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "temperature": self.temperature,
        }


class ModelRouter:
    """
    Router for managing LLM model access.
    
    This class provides a unified interface for:
    - Selecting appropriate models for tasks
    - Managing model configurations
    - Fallback handling
    - Usage tracking
    
    Example:
        >>> router = ModelRouter()
        >>> llm = router.get_llm("code-generation")
        >>> response = llm("Generate a FastAPI endpoint")
    """
    
    def __init__(self):
        """Initialize the model router."""
        self.settings = get_settings()
        self._models: Dict[str, Any] = {}
        self._default_model = "qwen2.5-coder"
        
        logger.info("Model router initialized")
    
    def get_llm(
        self,
        task_type: str = "general",
        model_name: Optional[str] = None,
        provider: ModelProvider = ModelProvider.OLLAMA,
    ) -> LLM:
        """
        Get an LLM instance for a specific task.
        
        Args:
            task_type: Type of task (e.g., "code", "analysis", "general")
            model_name: Specific model name (uses default if not specified)
            provider: LLM provider to use
            
        Returns:
            LLM: Configured LangChain LLM instance
            
        Example:
            >>> router = ModelRouter()
            >>> llm = router.get_llm(task_type="code")
        """
        model_name = model_name or self._get_default_model_for_task(task_type)
        cache_key = f"{provider.value}:{model_name}"
        
        if cache_key not in self._models:
            if provider == ModelProvider.OLLAMA:
                self._models[cache_key] = OllamaLLM(model=model_name)
            else:
                raise ValueError(f"Provider {provider} not yet implemented")
        
        logger.debug(
            "LLM retrieved",
            task_type=task_type,
            model=model_name,
            provider=provider.value,
        )
        
        return self._models[cache_key]
    
    def _get_default_model_for_task(self, task_type: str) -> str:
        """
        Get the default model for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            str: Default model name
        """
        task_model_map = {
            "code": "qwen2.5-coder",
            "analysis": "deepseek-coder",
            "general": "llama3.2",
            "chat": "qwen2.5",
        }
        return task_model_map.get(task_type, self._default_model)
    
    def list_available_models(self) -> Dict[str, list]:
        """
        List available models by provider.
        
        Returns:
            Dictionary of providers and their available models
            
        Example:
            >>> router = ModelRouter()
            >>> models = router.list_available_models()
            >>> print(models["ollama"])
        """
        # Stub - will query Ollama API in Phase 3
        return {
            ModelProvider.OLLAMA.value: [
                "qwen2.5-coder",
                "deepseek-coder",
                "llama3.2",
                "mixtral",
            ],
            ModelProvider.OPENAI.value: ["gpt-4", "gpt-3.5-turbo"],  # Future
            ModelProvider.ANTHROPIC.value: ["claude-3"],  # Future
        }
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dictionary with model information
        """
        # Stub - will query Ollama API in Phase 3
        model_info = {
            "qwen2.5-coder": {
                "provider": "ollama",
                "description": "Code-focused model",
                "context_length": 32768,
            },
            "deepseek-coder": {
                "provider": "ollama",
                "description": "DeepSeek Coder model",
                "context_length": 16384,
            },
            "llama3.2": {
                "provider": "ollama",
                "description": "General purpose model",
                "context_length": 128000,
            },
        }
        return model_info.get(model_name, {"error": "Model not found"})


# Singleton instance
_model_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """
    Get the singleton model router instance.
    
    Returns:
        ModelRouter: Singleton instance
        
    Example:
        >>> router = get_model_router()
        >>> llm = router.get_llm()
    """
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
