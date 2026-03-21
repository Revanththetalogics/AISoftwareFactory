"""
OpenAI LLM provider for AI Software Factory.

This module implements the LLM provider interface for OpenAI,
enabling cloud-based LLM execution with circuit breaker protection
and configurable timeouts.
"""

import os
import time
from collections.abc import AsyncIterator
from typing import Any

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.infrastructure.metrics import get_metrics_collector
from backend.llm.base_provider import BaseLLMProvider
from backend.utils.resilience import (
    CircuitBreakerOpenError,
    llm_circuit_breaker,
    with_timeout,
)

logger = get_logger(__name__)
metrics = get_metrics_collector()


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM provider for cloud model execution.
    """

    def __init__(self, config: dict[str, Any] | None = None):
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
            except ImportError as exc:
                raise ImportError(
                    "OpenAI package not installed. "
                    "Install with: pip install openai"
                ) from exc
        return self._client

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> str:
        """
        Generate text using OpenAI with circuit breaker and timeout.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        settings = get_settings()
        start_time = time.time()

        async def _do_generate():
            client = self._get_client()
            messages = [{"role": "user", "content": prompt}]
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""

        try:
            # Apply circuit breaker and timeout
            result = await llm_circuit_breaker.call(
                lambda: with_timeout(
                    _do_generate(),
                    settings.LLM_TIMEOUT_SECONDS,
                    f"OpenAI generate ({self.model})"
                )
            )

            # Record success metrics
            duration = time.time() - start_time
            metrics.record_llm_call(
                provider="openai",
                operation="generate",
                duration=duration,
                status="success"
            )
            metrics.record_circuit_breaker_success(llm_circuit_breaker.name)
            metrics.record_circuit_breaker_state(
                llm_circuit_breaker.name,
                llm_circuit_breaker.get_state_value()
            )

            return result

        except CircuitBreakerOpenError:
            metrics.record_circuit_breaker_rejection(llm_circuit_breaker.name)
            logger.error("OpenAI circuit breaker is open")
            raise
        except TimeoutError:
            metrics.record_timeout(f"openai_generate_{self.model}")
            metrics.record_llm_call(
                provider="openai",
                operation="generate",
                duration=time.time() - start_time,
                status="timeout"
            )
            raise
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_llm_call(
                provider="openai",
                operation="generate",
                duration=duration,
                status="error"
            )
            metrics.record_circuit_breaker_failure(llm_circuit_breaker.name)
            logger.error(f"OpenAI generation error: {e}")
            raise

    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
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
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs
    ) -> str:
        """
        Generate chat response with circuit breaker and timeout.

        Args:
            messages: List of messages with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        settings = get_settings()
        start_time = time.time()

        async def _do_chat():
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content or ""

        try:
            result = await llm_circuit_breaker.call(
                lambda: with_timeout(
                    _do_chat(),
                    settings.LLM_TIMEOUT_SECONDS,
                    f"OpenAI chat ({self.model})"
                )
            )

            duration = time.time() - start_time
            metrics.record_llm_call(
                provider="openai",
                operation="chat",
                duration=duration,
                status="success"
            )
            metrics.record_circuit_breaker_success(llm_circuit_breaker.name)

            return result

        except CircuitBreakerOpenError:
            metrics.record_circuit_breaker_rejection(llm_circuit_breaker.name)
            logger.error("OpenAI circuit breaker is open")
            raise
        except TimeoutError:
            metrics.record_timeout(f"openai_chat_{self.model}")
            metrics.record_llm_call(
                provider="openai",
                operation="chat",
                duration=time.time() - start_time,
                status="timeout"
            )
            raise
        except Exception as e:
            metrics.record_llm_call(
                provider="openai",
                operation="chat",
                duration=time.time() - start_time,
                status="error"
            )
            metrics.record_circuit_breaker_failure(llm_circuit_breaker.name)
            logger.error(f"OpenAI chat error: {e}")
            raise

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
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

    async def embed(self, text: str) -> list[float]:
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
