"""
Embeddings for Brain module.

This module provides text embedding generation using sentence-transformers
and OpenAI embeddings.
"""

from typing import List, Optional
import os

from backend.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingEngine:
    """
    Embedding engine for text vectorization.
    
    Supports multiple embedding providers including local models
    and OpenAI API.
    """
    
    def __init__(
        self,
        provider: str = "local",
        model_name: Optional[str] = None
    ):
        """
        Initialize the embedding engine.
        
        Args:
            provider: Embedding provider (local, openai)
            model_name: Model name to use
        """
        self._provider = provider
        self._model_name = model_name or self._get_default_model()
        self._model = None
        self._logger = get_logger(__name__)
    
    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        if self._provider == "openai":
            return "text-embedding-3-small"
        return "all-MiniLM-L6-v2"
    
    async def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: Texts to embed
            
        Returns:
            List of embeddings
        """
        if self._provider == "openai":
            return await self._embed_openai(texts)
        else:
            return await self._embed_local(texts)
    
    async def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model."""
        try:
            from sentence_transformers import SentenceTransformer
            
            if self._model is None:
                self._logger.info(
                    "Loading local embedding model",
                    model=self._model_name
                )
                self._model = SentenceTransformer(self._model_name)
            
            embeddings = self._model.encode(texts)
            return [emb.tolist() for emb in embeddings]
            
        except ImportError:
            self._logger.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise
    
    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API."""
        try:
            import openai
            
            client = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            response = await client.embeddings.create(
                model=self._model_name,
                input=texts
            )
            
            return [item.embedding for item in response.data]
            
        except ImportError:
            self._logger.error(
                "openai not installed. "
                "Install with: pip install openai"
            )
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension."""
        dimensions = {
            "all-MiniLM-L6-v2": 384,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072
        }
        return dimensions.get(self._model_name, 384)
