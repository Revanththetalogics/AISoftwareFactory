"""
Base LLM Provider for AI Software Factory.

This module defines the abstract base class for all LLM providers
and common data structures for LLM requests and responses.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum


class ModelCapability(str, Enum):
    """Capabilities that models may have."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    REASONING = "reasoning"
    LONG_CONTEXT = "long_context"


@dataclass
class LLMRequest:
    """
    Request to an LLM provider.
    
    Attributes:
        prompt: The input prompt/text
        model: Specific model to use (optional)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 - 1.0)
        top_p: Nucleus sampling parameter
        stop_sequences: Sequences that stop generation
        context: Additional context for the request
    """
    prompt: str
    model: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    stop_sequences: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "prompt": self.prompt,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop_sequences": self.stop_sequences,
            "context": self.context,
        }


@dataclass
class LLMResponse:
    """
    Response from an LLM provider.
    
    Attributes:
        text: Generated text
        model: Model used for generation
        prompt_tokens: Number of tokens in prompt
        completion_tokens: Number of tokens generated
        total_tokens: Total tokens used
        finish_reason: Why generation stopped
        metadata: Additional response metadata
        timestamp: When response was received
        error: Error message if failed
    """
    text: str = ""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    
    def __post_init__(self):
        """Calculate total_tokens if not provided."""
        if self.total_tokens == 0 and (self.prompt_tokens > 0 or self.completion_tokens > 0):
            self.total_tokens = self.prompt_tokens + self.completion_tokens
    
    @property
    def success(self) -> bool:
        """Check if response was successful."""
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "success": self.success,
        }


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM providers (Ollama, OpenAI, etc.) must implement this interface
    to be compatible with the Model Router.
    
    Example:
        >>> class MyProvider(BaseLLMProvider):
        ...     async def generate(self, request: LLMRequest) -> LLMResponse:
        ...         # Implementation
        ...         pass
    """
    
    def __init__(self, name: str, default_model: str = ""):
        """
        Initialize the provider.
        
        Args:
            name: Provider name (e.g., "ollama", "openai")
            default_model: Default model to use
        """
        self.name = name
        self.default_model = default_model
        self._available = False
    
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text from the LLM.
        
        Args:
            request: LLM request with prompt and parameters
            
        Returns:
            LLM response with generated text and metadata
            
        Example:
            >>> request = LLMRequest(prompt="Hello, world!")
            >>> response = await provider.generate(request)
            >>> print(response.text)
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is available.
        
        Returns:
            True if the provider can serve requests
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model names/identifiers
        """
        pass
    
    def get_capabilities(self) -> List[ModelCapability]:
        """
        Get provider capabilities.
        
        Returns:
            List of supported capabilities
        """
        return [ModelCapability.TEXT_GENERATION, ModelCapability.CHAT]
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        This is a rough estimate (1 token ≈ 4 characters for English).
        Override for more accurate estimates.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
    
    def _create_error_response(self, error: str) -> LLMResponse:
        """Create an error response."""
        return LLMResponse(
            text="",
            model=self.default_model,
            error=error,
        )
