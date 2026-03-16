"""
LLM Integration Layer for AI Software Factory.

This module provides the LLM provider abstraction, model routing,
and prompt management for the AI Software Factory.
"""

from backend.llm.providers.base import BaseLLMProvider, LLMResponse, LLMRequest
from backend.llm.providers.ollama import OllamaProvider
from backend.llm.router import ModelRouter
from backend.llm.prompt_manager import PromptManager

__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "LLMRequest",
    "OllamaProvider",
    "ModelRouter",
    "PromptManager",
]
