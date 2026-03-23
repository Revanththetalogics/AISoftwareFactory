"""
AgentLLM — synchronous LLM wrapper for agent/crew contexts.

Provides a thin synchronous interface over the async ModelRouter so that
CrewAI agents and other synchronous agent code can call the enterprise
LLM router without managing event loops.
"""

import asyncio
import concurrent.futures
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class AgentLLM:
    """
    Synchronous LLM wrapper that delegates to the async ModelRouter.

    Designed for use in CrewAI agents and other synchronous contexts.
    Runs async generation in a dedicated thread to avoid event-loop conflicts.

    Attributes:
        model: The Ollama model name this instance is bound to.

    Example:
        >>> from backend.llm.router import get_llm_router
        >>> llm = get_llm_router().get_agent_llm(task_type="coding")
        >>> response = llm("Write a FastAPI endpoint")
    """

    def __init__(self, model: str, router: Any) -> None:
        """
        Initialise the AgentLLM.

        Args:
            model: Ollama model name (e.g. "deepseek-coder-v2").
            router: ModelRouter instance to delegate to.
        """
        self.model = model
        self._router = router

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def __call__(self, prompt: str, **kwargs: Any) -> str:
        """Convenience shortcut — allows llm("prompt") syntax."""
        return self.generate(prompt, **kwargs)

    def generate(self, prompt: str, temperature: float = 0.7, **kwargs: Any) -> str:
        """
        Generate a response from the model synchronously.

        Submits the async router.generate() call to a background thread so
        that synchronous callers (CrewAI, agent task handlers) are not
        blocked by event-loop management.

        Args:
            prompt: Input text / instruction for the model.
            temperature: Sampling temperature (0.0 – 1.0).

        Returns:
            Generated text string, or an error string on failure.
        """
        from backend.llm.providers.base import LLMRequest

        request = LLMRequest(
            prompt=prompt,
            model=self.model,
            temperature=temperature,
        )
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, self._router.generate(request))
                response = future.result()
        except Exception as exc:
            logger.error("AgentLLM.generate failed", model=self.model, error=str(exc))
            return f"[Error from {self.model}]: {exc}"

        if response.success:
            return response.text
        return f"[Error from {self.model}]: {response.error}"

    # ------------------------------------------------------------------
    # Metadata helpers (used by CrewAI / LangChain interop)
    # ------------------------------------------------------------------

    @property
    def _llm_type(self) -> str:
        return "ollama"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"model": self.model}
