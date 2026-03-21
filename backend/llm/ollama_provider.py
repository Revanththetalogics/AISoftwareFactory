"""
Ollama LLM provider for AI Software Factory.

This module implements the LLM provider interface for Ollama,
enabling local LLM execution with circuit breaker protection
and configurable timeouts.
"""

import os
import time
from typing import Any, AsyncIterator, Dict, List, Optional

import aiohttp

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


class OllamaProvider(BaseLLMProvider):
    """
    Ollama LLM provider for local model execution.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Ollama provider.

        Args:
            config: Provider configuration with optional 'base_url' and 'model'
        """
        super().__init__(config)
        self.base_url = self.config.get("base_url", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
        self.model = self.config.get("model", os.getenv("OLLAMA_MODEL", "llama3.2"))
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Ollama with circuit breaker and timeout.

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
            session = await self._get_session()

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("response", "")

        try:
            result = await llm_circuit_breaker.call(
                lambda: with_timeout(
                    _do_generate(),
                    settings.LLM_TIMEOUT_SECONDS,
                    f"Ollama generate ({self.model})"
                )
            )

            duration = time.time() - start_time
            metrics.record_llm_call(
                provider="ollama",
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
            logger.error("Ollama circuit breaker is open")
            raise
        except TimeoutError:
            metrics.record_timeout(f"ollama_generate_{self.model}")
            metrics.record_llm_call(
                provider="ollama",
                operation="generate",
                duration=time.time() - start_time,
                status="timeout"
            )
            raise
        except Exception as e:
            duration = time.time() - start_time
            metrics.record_llm_call(
                provider="ollama",
                operation="generate",
                duration=duration,
                status="error"
            )
            metrics.record_circuit_breaker_failure(llm_circuit_breaker.name)
            logger.error(f"Ollama generation error: {e}")
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
        session = await self._get_session()

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
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
            session = await self._get_session()

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("message", {}).get("content", "")

        try:
            result = await llm_circuit_breaker.call(
                lambda: with_timeout(
                    _do_chat(),
                    settings.LLM_TIMEOUT_SECONDS,
                    f"Ollama chat ({self.model})"
                )
            )

            duration = time.time() - start_time
            metrics.record_llm_call(
                provider="ollama",
                operation="chat",
                duration=duration,
                status="success"
            )
            metrics.record_circuit_breaker_success(llm_circuit_breaker.name)

            return result

        except CircuitBreakerOpenError:
            metrics.record_circuit_breaker_rejection(llm_circuit_breaker.name)
            logger.error("Ollama circuit breaker is open")
            raise
        except TimeoutError:
            metrics.record_timeout(f"ollama_chat_{self.model}")
            metrics.record_llm_call(
                provider="ollama",
                operation="chat",
                duration=time.time() - start_time,
                status="timeout"
            )
            raise
        except Exception as e:
            metrics.record_llm_call(
                provider="ollama",
                operation="chat",
                duration=time.time() - start_time,
                status="error"
            )
            metrics.record_circuit_breaker_failure(llm_circuit_breaker.name)
            logger.error(f"Ollama chat error: {e}")
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
        session = await self._get_session()

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        import json
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Ollama chat streaming error: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings using Ollama.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        session = await self._get_session()

        payload = {
            "model": self.model,
            "prompt": text
        }

        try:
            async with session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("embedding", [])
        except Exception as e:
            logger.error(f"Ollama embedding error: {e}")
            raise

    async def health_check(self) -> bool:
        """
        Check if Ollama is available.

        Returns:
            True if available
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                return response.status == 200
        except Exception:
            return False

    @property
    def name(self) -> str:
        """Get provider name."""
        return f"ollama:{self.model}"

    @property
    def supports_streaming(self) -> bool:
        """Check if streaming is supported."""
        return True

    @property
    def supports_embeddings(self) -> bool:
        """Check if embeddings are supported."""
        return True
