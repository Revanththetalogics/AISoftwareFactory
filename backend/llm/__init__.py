"""
LLM Integration Layer for AI Software Factory.

This module provides the LLM provider abstraction, model routing,
and prompt management for the AI Software Factory.
"""

from backend.llm.agent_llm import AgentLLM
from backend.llm.prompt_manager import PromptManager
from backend.llm.providers.base import BaseLLMProvider, LLMRequest, LLMResponse
from backend.llm.providers.ollama import OllamaProvider
from backend.llm.router import ModelRouter, get_llm_router

__all__ = [
    "AgentLLM",
    "BaseLLMProvider",
    "LLMResponse",
    "LLMRequest",
    "OllamaProvider",
    "ModelRouter",
    "get_llm_router",
    "PromptManager",
]
