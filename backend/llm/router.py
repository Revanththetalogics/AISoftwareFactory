"""
Model Router for AI Software Factory.

This module provides intelligent routing of LLM requests to appropriate
providers with fallback logic and model selection.
"""

from dataclasses import dataclass, field
from typing import Any

from backend.core.logging import get_logger
from backend.llm.providers.base import BaseLLMProvider, LLMRequest, LLMResponse

logger = get_logger(__name__)


@dataclass
class ModelConfig:
    """
    Configuration for a model.

    Attributes:
        name: Model name/identifier
        provider: Provider name
        priority: Priority for selection (higher = preferred)
        capabilities: List of supported capabilities
        context_window: Maximum context window size
        cost_per_1k_tokens: Cost per 1000 tokens (for cost tracking)
    """
    name: str
    provider: str
    priority: int = 1
    capabilities: list[str] = field(default_factory=list)
    context_window: int = 4096
    cost_per_1k_tokens: float = 0.0


class ModelRouter:
    """
    Router for LLM requests with provider selection and fallback logic.

    The Model Router manages multiple LLM providers and routes requests
to the best available provider based on model requirements, availability,
    and fallback chains.

    Attributes:
        providers: Dictionary of registered providers
        model_configs: Dictionary of model configurations
        default_model: Default model to use

    Example:
        >>> router = ModelRouter()
        >>> router.register_provider(OllamaProvider())
        >>> response = await router.generate(
        ...     LLMRequest(prompt="Hello!"),
        ...     model="llama2"
        ... )
    """

    def __init__(self, default_model: str = "llama3.2"):
        """
        Initialize the model router.

        Args:
            default_model: Default model to use
        """
        self.providers: dict[str, BaseLLMProvider] = {}
        self.model_configs: dict[str, ModelConfig] = {}
        self.default_model = default_model
        self._logger = get_logger(__name__)

        # Initialize with default model configs
        self._init_default_configs()

    def _init_default_configs(self) -> None:
        """Initialize default model configurations."""
        default_configs = [
            # Llama 3.2 - General purpose, fast, efficient
            ModelConfig(
                name="llama3.2",
                provider="ollama",
                priority=5,
                capabilities=["text_generation", "chat", "code_generation", "reasoning"],
                context_window=128000,
            ),
            # Llama 3.2 Vision - Multimodal capabilities
            ModelConfig(
                name="llama3.2-vision",
                provider="ollama",
                priority=4,
                capabilities=["text_generation", "chat", "vision", "reasoning"],
                context_window=128000,
            ),
            # DeepSeek Coder - Specialized for code generation
            ModelConfig(
                name="deepseek-coder",
                provider="ollama",
                priority=5,
                capabilities=["code_generation", "code_review", "text_generation", "reasoning"],
                context_window=16384,
            ),
            ModelConfig(
                name="deepseek-coder-v2",
                provider="ollama",
                priority=6,
                capabilities=["code_generation", "code_review", "text_generation", "reasoning"],
                context_window=128000,
            ),
            # Qwen - Strong multilingual and reasoning capabilities
            ModelConfig(
                name="qwen",
                provider="ollama",
                priority=4,
                capabilities=["chat", "text_generation", "reasoning", "code_generation"],
                context_window=8192,
            ),
            ModelConfig(
                name="qwen2.5",
                provider="ollama",
                priority=5,
                capabilities=["chat", "text_generation", "reasoning", "code_generation"],
                context_window=128000,
            ),
            ModelConfig(
                name="qwen2.5-coder",
                provider="ollama",
                priority=5,
                capabilities=["code_generation", "code_review", "text_generation", "reasoning"],
                context_window=128000,
            ),
            # Mixtral - MoE architecture for complex reasoning
            ModelConfig(
                name="mixtral",
                provider="ollama",
                priority=4,
                capabilities=["reasoning", "text_generation", "chat", "code_generation"],
                context_window=32768,
            ),
            ModelConfig(
                name="mixtral:8x7b",
                provider="ollama",
                priority=5,
                capabilities=["reasoning", "text_generation", "chat", "code_generation"],
                context_window=32768,
            ),
            # Llama 3.1 - Larger variant for complex tasks
            ModelConfig(
                name="llama3.1",
                provider="ollama",
                priority=4,
                capabilities=["text_generation", "chat", "code_generation", "reasoning"],
                context_window=128000,
            ),
            ModelConfig(
                name="llama3.1:70b",
                provider="ollama",
                priority=3,
                capabilities=["text_generation", "chat", "code_generation", "reasoning"],
                context_window=128000,
            ),
        ]

        for config in default_configs:
            self.model_configs[config.name] = config

    def register_provider(self, provider: BaseLLMProvider) -> None:
        """
        Register an LLM provider.

        Args:
            provider: Provider instance to register

        Example:
            >>> router = ModelRouter()
            >>> router.register_provider(OllamaProvider())
        """
        self.providers[provider.name] = provider
        self._logger.info("Provider registered", provider=provider.name)

    def get_provider(self, name: str) -> BaseLLMProvider | None:
        """
        Get a provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None
        """
        return self.providers.get(name)

    async def is_provider_available(self, name: str) -> bool:
        """
        Check if a provider is available.

        Args:
            name: Provider name

        Returns:
            True if provider is available
        """
        provider = self.providers.get(name)
        if not provider:
            return False
        return await provider.is_available()

    def get_available_providers(self) -> list[str]:
        """
        Get list of registered provider names.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())

    def select_model(self, task_type: str = "general") -> str:
        """
        Select the best model for a task type.

        Args:
            task_type: Type of task (general, coding, chat, reasoning)

        Returns:
            Selected model name

        Example:
            >>> model = router.select_model("coding")
            >>> print(model)  # "deepseek-coder"
        """
        # Map task types to preferred models
        task_model_map = {
            "coding": "deepseek-coder-v2",
            "code_generation": "deepseek-coder-v2",
            "code_review": "deepseek-coder-v2",
            "chat": "qwen2.5",
            "reasoning": "mixtral:8x7b",
            "general": "llama3.2",
        }

        preferred_model = task_model_map.get(task_type, self.default_model)

        # Check if model is available
        config = self.model_configs.get(preferred_model)
        if config:
            return preferred_model

        # Fallback to default
        return self.default_model

    async def generate(
        self,
        request: LLMRequest,
        model: str | None = None,
    ) -> LLMResponse:
        """
        Generate text using the appropriate provider.

        This method selects the best provider for the requested model
        and handles fallback to other providers if the primary fails.

        Args:
            request: LLM request
            model: Model to use (optional, defaults to request.model or default_model)

        Returns:
            LLM response

        Example:
            >>> request = LLMRequest(prompt="Hello!")
            >>> response = await router.generate(request, model="llama2")
            >>> print(response.text)
        """
        # Determine model to use
        target_model = model or request.model or self.default_model
        request.model = target_model

        self._logger.info(
            "Routing generation request",
            model=target_model,
            prompt_length=len(request.prompt),
        )

        # Get model config
        config = self.model_configs.get(target_model)

        if config:
            # Try primary provider
            primary_provider = self.providers.get(config.provider)
            if primary_provider:
                try:
                    if await primary_provider.is_available():
                        response = await primary_provider.generate(request)
                        if response.success:
                            self._logger.info(
                                "Generation successful",
                                provider=config.provider,
                                model=target_model,
                            )
                            return response
                        else:
                            self._logger.warning(
                                "Primary provider failed",
                                provider=config.provider,
                                error=response.error,
                            )
                except Exception as exc:
                    self._logger.error(
                        "Primary provider error",
                        provider=config.provider,
                        error=str(exc),
                    )

        # Try fallback providers
        return await self._try_fallbacks(request)

    async def _try_fallbacks(self, request: LLMRequest) -> LLMResponse:
        """
        Try fallback providers.

        Args:
            request: LLM request

        Returns:
            LLM response (may be error response)
        """
        self._logger.info("Trying fallback providers")

        # Sort providers by priority of their default models
        sorted_providers = sorted(
            self.providers.items(),
            key=lambda x: self.model_configs.get(
                x[1].default_model, ModelConfig(name="", provider="", priority=0)
            ).priority,
            reverse=True,
        )

        for provider_name, provider in sorted_providers:
            try:
                if await provider.is_available():
                    # Update request to use provider's default model
                    fallback_request = LLMRequest(
                        prompt=request.prompt,
                        model=provider.default_model,
                        max_tokens=request.max_tokens,
                        temperature=request.temperature,
                        top_p=request.top_p,
                        stop_sequences=request.stop_sequences,
                        context=request.context,
                    )

                    response = await provider.generate(fallback_request)
                    if response.success:
                        self._logger.info(
                            "Fallback successful",
                            provider=provider_name,
                            model=provider.default_model,
                        )
                        return response
                    else:
                        self._logger.warning(
                            "Fallback provider failed",
                            provider=provider_name,
                            error=response.error,
                        )
            except Exception as exc:
                self._logger.error(
                    "Fallback provider error",
                    provider=provider_name,
                    error=str(exc),
                )

        # All providers failed
        self._logger.error("All providers failed")
        return LLMResponse(
            text="",
            model="",
            error="All LLM providers are unavailable",
        )

    def get_model_info(self, model: str) -> ModelConfig | None:
        """
        Get information about a model.

        Args:
            model: Model name

        Returns:
            Model configuration or None
        """
        return self.model_configs.get(model)

    def list_models(self) -> list[str]:
        """
        List all configured models.

        Returns:
            List of model names
        """
        return list(self.model_configs.keys())

    async def health_check(self) -> dict[str, bool]:
        """
        Check health of all providers.

        Returns:
            Dictionary mapping provider names to availability
        """
        health = {}
        for name, provider in self.providers.items():
            try:
                health[name] = await provider.is_available()
            except Exception:
                health[name] = False
        return health

    def get_agent_llm(
        self,
        task_type: str = "general",
        model_name: str | None = None,
    ) -> Any:
        """
        Get a synchronous LLM wrapper suitable for use in agent/crew contexts.

        Selects the best model for the given task type and returns an AgentLLM
        that runs async generation in a background thread — no event-loop
        conflicts in synchronous CrewAI/agent code.

        Args:
            task_type: Task category — coding, reasoning, chat, general, etc.
            model_name: Override the model; uses task mapping if not provided.

        Returns:
            AgentLLM instance bound to the selected model.

        Example:
            >>> llm = router.get_agent_llm(task_type="coding")
            >>> response = llm("Write a FastAPI endpoint")
        """
        from backend.llm.agent_llm import AgentLLM  # local import to avoid circular
        resolved = model_name or self.select_model(task_type)
        return AgentLLM(model=resolved, router=self)


# ---------------------------------------------------------------------------
# Module-level singleton helpers
# ---------------------------------------------------------------------------

_router_instance: ModelRouter | None = None


def get_llm_router() -> ModelRouter:
    """
    Get the singleton ModelRouter, pre-wired with the Ollama provider.

    Returns:
        ModelRouter singleton with OllamaProvider registered.

    Example:
        >>> router = get_llm_router()
        >>> llm = router.get_agent_llm(task_type="coding")
    """
    global _router_instance
    if _router_instance is None:
        from backend.llm.factory import LLMFactory
        _router_instance = ModelRouter()
        provider = LLMFactory.create_llm()
        _router_instance.register_provider(provider)
        logger.info("LLM router singleton initialised with Ollama provider")
    return _router_instance
