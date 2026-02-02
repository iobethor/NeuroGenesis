"""Embedding generation for semantic memory."""

import asyncio
from functools import lru_cache
from typing import Sequence

import numpy as np
import structlog

logger = structlog.get_logger()


class EmbeddingEngine:
    """
    Engine for generating text embeddings.
    
    Uses sentence-transformers for high-quality semantic embeddings.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        dimension: int = 384,
    ) -> None:
        """
        Initialize the embedding engine.
        
        Args:
            model_name: Name of the sentence-transformer model
            dimension: Expected embedding dimension
        """
        self.model_name = model_name
        self.dimension = dimension
        self._model = None
        self._initialized = False

    async def initialize(self) -> None:
        """Load the embedding model."""
        if self._initialized:
            return
            
        logger.info("Loading embedding model...", model=self.model_name)
        
        # Load model in executor to not block event loop
        loop = asyncio.get_event_loop()
        self._model = await loop.run_in_executor(None, self._load_model)
        
        self._initialized = True
        logger.info("Embedding model loaded", dimension=self.dimension)

    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer(self.model_name)
        except ImportError:
            logger.warning(
                "sentence-transformers not installed, using random embeddings"
            )
            return None

    async def embed(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of shape (dimension,)
        """
        if not self._initialized:
            await self.initialize()
            
        if self._model is None:
            # Fallback to random embeddings for testing
            return self._random_embedding(text)
        
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, lambda: self._model.encode(text, normalize_embeddings=True)
        )
        return np.array(embedding, dtype=np.float32)

    async def embed_batch(self, texts: Sequence[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of shape (n_texts, dimension)
        """
        if not self._initialized:
            await self.initialize()
            
        if self._model is None:
            return np.array([self._random_embedding(t) for t in texts])
        
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self._model.encode(
                list(texts),
                normalize_embeddings=True,
                show_progress_bar=False,
            ),
        )
        return np.array(embeddings, dtype=np.float32)

    @lru_cache(maxsize=1000)
    def _random_embedding(self, text: str) -> np.ndarray:
        """Generate deterministic random embedding based on text hash."""
        # Use text hash as seed for reproducibility
        seed = hash(text) % (2**32)
        rng = np.random.RandomState(seed)
        embedding = rng.randn(self.dimension).astype(np.float32)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

    def cosine_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between -1 and 1
        """
        return float(np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        ))

    def batch_cosine_similarity(
        self,
        query: np.ndarray,
        embeddings: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate cosine similarity between query and multiple embeddings.
        
        Args:
            query: Query embedding of shape (dimension,)
            embeddings: Matrix of embeddings of shape (n, dimension)
            
        Returns:
            Array of similarities of shape (n,)
        """
        # Normalize query
        query_norm = query / np.linalg.norm(query)
        # Normalize embeddings
        emb_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings_norm = embeddings / emb_norms
        # Dot product
        return np.dot(embeddings_norm, query_norm)
