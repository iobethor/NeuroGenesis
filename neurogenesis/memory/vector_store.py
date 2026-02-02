"""Vector store for efficient similarity search."""

import asyncio
from pathlib import Path
from typing import Sequence
from uuid import UUID

import numpy as np
import structlog

logger = structlog.get_logger()


class VectorStore:
    """
    Vector store using FAISS for efficient similarity search.
    
    Supports both in-memory and persistent storage.
    """

    def __init__(
        self,
        path: Path,
        dimension: int = 384,
        use_gpu: bool = False,
    ) -> None:
        """
        Initialize vector store.
        
        Args:
            path: Path for persistent storage
            dimension: Embedding dimension
            use_gpu: Whether to use GPU acceleration
        """
        self.path = path
        self.dimension = dimension
        self.use_gpu = use_gpu
        
        self._index = None
        self._id_map: dict[int, UUID] = {}  # FAISS index -> UUID
        self._uuid_map: dict[UUID, int] = {}  # UUID -> FAISS index
        self._next_idx = 0
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize or load the vector store."""
        if self._initialized:
            return
            
        logger.info("Initializing vector store...", path=str(self.path))
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._init_index)
        
        # Try to load existing index
        index_file = self.path / "index.faiss"
        if index_file.exists():
            await loop.run_in_executor(None, self._load_index)
        
        self._initialized = True
        logger.info("Vector store initialized", dimension=self.dimension)

    def _init_index(self) -> None:
        """Create FAISS index."""
        try:
            import faiss
            
            # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self._index = faiss.IndexFlatIP(self.dimension)
            
            if self.use_gpu:
                try:
                    res = faiss.StandardGpuResources()
                    self._index = faiss.index_cpu_to_gpu(res, 0, self._index)
                    logger.info("Using GPU acceleration")
                except Exception:
                    logger.warning("GPU not available, using CPU")
                    
        except ImportError:
            logger.warning("FAISS not installed, using numpy fallback")
            self._index = None
            self._embeddings: list[np.ndarray] = []

    def _load_index(self) -> None:
        """Load existing index from disk."""
        try:
            import faiss
            import json
            
            index_file = self.path / "index.faiss"
            map_file = self.path / "id_map.json"
            
            self._index = faiss.read_index(str(index_file))
            
            if map_file.exists():
                with open(map_file) as f:
                    data = json.load(f)
                    self._id_map = {int(k): UUID(v) for k, v in data["id_map"].items()}
                    self._uuid_map = {UUID(v): int(k) for k, v in data["id_map"].items()}
                    self._next_idx = data.get("next_idx", len(self._id_map))
                    
            logger.info("Loaded existing vector index", vectors=len(self._id_map))
            
        except Exception as e:
            logger.error("Failed to load index", error=str(e))

    async def save(self) -> None:
        """Save index to disk."""
        if not self._initialized:
            return
            
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_index)

    def _save_index(self) -> None:
        """Persist index to disk."""
        try:
            import faiss
            import json
            
            self.path.mkdir(parents=True, exist_ok=True)
            
            index_file = self.path / "index.faiss"
            map_file = self.path / "id_map.json"
            
            if self._index is not None:
                faiss.write_index(self._index, str(index_file))
            
            with open(map_file, "w") as f:
                json.dump({
                    "id_map": {str(k): str(v) for k, v in self._id_map.items()},
                    "next_idx": self._next_idx,
                }, f)
                
            logger.info("Saved vector index", vectors=len(self._id_map))
            
        except Exception as e:
            logger.error("Failed to save index", error=str(e))

    async def add(self, uuid: UUID, embedding: np.ndarray) -> int:
        """
        Add a vector to the store.
        
        Args:
            uuid: Unique identifier for this vector
            embedding: The embedding vector
            
        Returns:
            Internal index of the added vector
        """
        if not self._initialized:
            await self.initialize()
            
        # Normalize for cosine similarity
        embedding = embedding / np.linalg.norm(embedding)
        embedding = embedding.reshape(1, -1).astype(np.float32)
        
        idx = self._next_idx
        
        if self._index is not None:
            self._index.add(embedding)
        else:
            self._embeddings.append(embedding.flatten())
        
        self._id_map[idx] = uuid
        self._uuid_map[uuid] = idx
        self._next_idx += 1
        
        return idx

    async def add_batch(
        self,
        uuids: Sequence[UUID],
        embeddings: np.ndarray,
    ) -> list[int]:
        """
        Add multiple vectors to the store.
        
        Args:
            uuids: List of unique identifiers
            embeddings: Matrix of embeddings (n, dimension)
            
        Returns:
            List of internal indices
        """
        if not self._initialized:
            await self.initialize()
            
        # Normalize all embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = (embeddings / norms).astype(np.float32)
        
        indices = []
        start_idx = self._next_idx
        
        if self._index is not None:
            self._index.add(embeddings)
        
        for i, uuid in enumerate(uuids):
            idx = start_idx + i
            if self._index is None:
                self._embeddings.append(embeddings[i])
            self._id_map[idx] = uuid
            self._uuid_map[uuid] = idx
            indices.append(idx)
        
        self._next_idx = start_idx + len(uuids)
        return indices

    async def search(
        self,
        query: np.ndarray,
        k: int = 10,
        threshold: float = 0.0,
    ) -> list[tuple[UUID, float]]:
        """
        Search for similar vectors.
        
        Args:
            query: Query embedding
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (uuid, similarity) tuples
        """
        if not self._initialized:
            await self.initialize()
            
        if len(self._id_map) == 0:
            return []
            
        # Normalize query
        query = query / np.linalg.norm(query)
        query = query.reshape(1, -1).astype(np.float32)
        
        if self._index is not None:
            similarities, indices = self._index.search(query, min(k, len(self._id_map)))
            results = []
            for sim, idx in zip(similarities[0], indices[0]):
                if idx >= 0 and sim >= threshold and idx in self._id_map:
                    results.append((self._id_map[idx], float(sim)))
            return results
        else:
            # Numpy fallback
            if not self._embeddings:
                return []
            emb_matrix = np.array(self._embeddings)
            similarities = np.dot(emb_matrix, query.T).flatten()
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                sim = similarities[idx]
                if sim >= threshold and idx in self._id_map:
                    results.append((self._id_map[idx], float(sim)))
            return results

    async def remove(self, uuid: UUID) -> bool:
        """
        Remove a vector from the store.
        
        Note: FAISS doesn't support efficient removal, so we mark as removed.
        
        Args:
            uuid: UUID of vector to remove
            
        Returns:
            True if removed, False if not found
        """
        if uuid not in self._uuid_map:
            return False
            
        idx = self._uuid_map[uuid]
        del self._uuid_map[uuid]
        del self._id_map[idx]
        
        return True

    async def get_vector(self, uuid: UUID) -> np.ndarray | None:
        """
        Get a vector by UUID.
        
        Args:
            uuid: UUID of the vector
            
        Returns:
            The embedding or None if not found
        """
        if uuid not in self._uuid_map:
            return None
            
        idx = self._uuid_map[uuid]
        
        if self._index is not None:
            try:
                import faiss
                return self._index.reconstruct(idx)
            except Exception:
                return None
        else:
            return self._embeddings[idx] if idx < len(self._embeddings) else None

    def __len__(self) -> int:
        """Return number of vectors in store."""
        return len(self._id_map)
