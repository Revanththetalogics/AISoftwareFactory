"""
OpenAI LLM provider for AI Software Factory.

This module implements the LLM provider interface for OpenAI,
enabling cloud-based LLM execution.
"""

import os
from typing import Any, AsyncIterator, Dict, List, Optional

from backend.core.logging import get_logger
from backend.llm.base_provider import BaseLLMProvider

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider for cloud model execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            config: Provider configuration with optional 'api_key' and 'model'
        """
        super().__init__(config)
        self.api_key = self.config.get("api_key", os.getenv("OPENAI_API_KEY"))
        self.model = self.config.get("model", os.getenv("OPENAI_MODEL", "gpt-4"))
        self.base_url = self.config.get("base_url", "https://api.openai.com/v1")
        self._client = None
    
    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. "
                    "Install with: pip install openai"
                )
        return self._client
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenAI.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        client = self._get_client()
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate text with streaming.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Text chunks
        """
        client = self._get_client()
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate chat response.
        
        Args:
            messages: List of messages with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        client = self._get_client()
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate chat response with streaming.
        
        Args:
            messages: List of messages with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        client = self._get_client()
        
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"OpenAI chat streaming error: {e}")
            raise
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings using OpenAI.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        client = self._get_client()
        
        try:
            response = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Check if OpenAI API is available.
        
        Returns:
            True if available
        """
        if not self.api_key:
            return False
        
        try:
            client = self._get_client()
            # Try a simple models list call
            await client.models.list()
            return True
        except Exception:
            return False
    
    @property
    def name(self) -> str:
        """Get provider name."""
        return f"openai:{self.model}"
    
    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True
    
    @property
    def supports_embeddings(self) -> bool:
        """Check if embeddings are supported."""
        return True
