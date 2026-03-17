"""
Ollama Provider for AI Software Factory.

This module implements the Ollama LLM provider for local model inference.
"""

import json
from typing import Any, Dict, List, Optional

import httpx

from backend.llm.providers.base import (
    BaseLLMProvider,
    LLMRequest,
    LLMResponse,
    ModelCapability,
)
from backend.core.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama LLM provider for local model inference.
    
    This provider connects to a local Ollama instance for running
    open-source models like Llama, Qwen, DeepSeek Coder, etc.
    
    Attributes:
        base_url: Ollama API base URL
        default_model: Default model to use
        timeout: Request timeout in seconds
        
    Example:
        >>> provider = OllamaProvider(base_url="http://localhost:11434")
        >>> request = LLMRequest(prompt="Hello, world!", model="llama2")
        >>> response = await provider.generate(request)
    """
    
    # Recommended models for different tasks
    RECOMMENDED_MODELS = {
        "general": "llama3.2",
        "coding": "deepseek-coder-v2",
        "chat": "qwen2.5",
        "reasoning": "mixtral:8x7b",
        "vision": "llama3.2-vision",
    }
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3.2",
        timeout: float = 120.0,
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Ollama API base URL
            default_model: Default model to use
            timeout: Request timeout in seconds
        """
        super().__init__(name="ollama", default_model=default_model)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._available_models: List[str] = []
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def is_available(self) -> bool:
        """
        Check if Ollama is available.
        
        Returns:
            True if Ollama is running and accessible
        """
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/api/tags")
            available = response.status_code == 200
            
            if available:
                # Cache available models
                data = response.json()
                self._available_models = [
                    model["name"] for model in data.get("models", [])
                ]
                logger.info(
                    "Ollama is available",
                    models_count=len(self._available_models),
                )
            
            return available
            
        except Exception as exc:
            logger.warning("Ollama is not available", error=str(exc))
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available models.
        
        Returns:
            List of model names available in Ollama
        """
        return self._available_models.copy()
    
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text using Ollama.
        
        Args:
            request: LLM request with prompt and parameters
            
        Returns:
            LLM response with generated text
            
        Example:
            >>> request = LLMRequest(
            ...     prompt="Write a Python function to add two numbers",
            ...     model="deepseek-coder",
            ...     max_tokens=512,
            ... )
            >>> response = await provider.generate(request)
            >>> print(response.text)
        """
        model = request.model or self.default_model
        
        logger.info(
            "Generating with Ollama",
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        try:
            client = self._get_client()
            
            payload = {
                "model": model,
                "prompt": request.prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "num_predict": request.max_tokens,
                },
            }
            
            if request.stop_sequences:
                payload["options"]["stop"] = request.stop_sequences
            
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Parse response
            generated_text = data.get("response", "")
            
            # Extract token counts if available
            prompt_tokens = data.get("prompt_eval_count", 0)
            completion_tokens = data.get("eval_count", 0)
            
            # Estimate if not provided
            if prompt_tokens == 0:
                prompt_tokens = self.estimate_tokens(request.prompt)
            if completion_tokens == 0:
                completion_tokens = self.estimate_tokens(generated_text)
            
            return LLMResponse(
                text=generated_text,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                finish_reason=data.get("done_reason", "stop"),
                metadata={
                    "total_duration": data.get("total_duration"),
                    "load_duration": data.get("load_duration"),
                },
            )
            
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Ollama HTTP error",
                status_code=exc.response.status_code,
                error=str(exc),
            )
            return self._create_error_response(
                f"HTTP {exc.response.status_code}: {exc.response.text}"
            )
            
        except httpx.RequestError as exc:
            logger.error("Ollama request error", error=str(exc))
            return self._create_error_response(
                f"Connection error: {str(exc)}"
            )
            
        except Exception as exc:
            logger.error("Ollama generation error", error=str(exc))
            return self._create_error_response(str(exc))
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Chat completion using Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use
            **kwargs: Additional parameters
            
        Returns:
            LLM response
            
        Example:
            >>> messages = [
            ...     {"role": "user", "content": "Hello!"},
            ... ]
            >>> response = await provider.chat(messages, model="llama2")
        """
        model = model or self.default_model
        
        try:
            client = self._get_client()
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
            }
            
            if "temperature" in kwargs:
                payload["options"] = {"temperature": kwargs["temperature"]}
            
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            
            data = response.json()
            message = data.get("message", {})
            
            return LLMResponse(
                text=message.get("content", ""),
                model=model,
                metadata={"done": data.get("done")},
            )
            
        except Exception as exc:
            logger.error("Ollama chat error", error=str(exc))
            return self._create_error_response(str(exc))
    
    async def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry.
        
        Args:
            model: Model name to pull
            
        Returns:
            True if successful
        """
        try:
            client = self._get_client()
            
            logger.info("Pulling model from Ollama", model=model)
            
            response = await client.post(
                f"{self.base_url}/api/pull",
                json={"name": model, "stream": False},
            )
            
            success = response.status_code == 200
            if success:
                logger.info("Model pulled successfully", model=model)
            else:
                logger.error(
                    "Failed to pull model",
                    model=model,
                    status_code=response.status_code,
                )
            
            return success
            
        except Exception as exc:
            logger.error("Error pulling model", model=model, error=str(exc))
            return False
    
    def get_capabilities(self) -> List[ModelCapability]:
        """
        Get Ollama capabilities.
        
        Returns:
            List of supported capabilities
        """
        return [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.CODE_REVIEW,
        ]
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
