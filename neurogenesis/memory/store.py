"""Memory storage with SQLite backend and vector search."""

import asyncio
import json
from pathlib import Path
from typing import Sequence
from uuid import UUID

import aiosqlite
import numpy as np
import structlog

from neurogenesis.core.types import Association, Memory, MemoryType
from neurogenesis.memory.embeddings import EmbeddingEngine
from neurogenesis.memory.vector_store import VectorStore

logger = structlog.get_logger()


class MemoryStore:
    """
    Persistent memory storage combining SQLite and vector search.
    
    Provides efficient storage and retrieval of memories with
    both metadata filtering and semantic similarity search.
    """

    def __init__(
        self,
        db_path: Path,
        vector_path: Path,
        embedding_engine: EmbeddingEngine,
    ) -> None:
        """
        Initialize memory store.
        
        Args:
            db_path: Path to SQLite database
            vector_path: Path to vector store directory
            embedding_engine: Engine for generating embeddings
        """
        self.db_path = db_path
        self.vector_path = vector_path
        self.embedding_engine = embedding_engine
        
        self._vector_store: VectorStore | None = None
        self._db: aiosqlite.Connection | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize database and vector store."""
        if self._initialized:
            return
            
        logger.info("Initializing memory store...")
        
        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite
        self._db = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        
        # Initialize vector store
        self._vector_store = VectorStore(
            path=self.vector_path,
            dimension=self.embedding_engine.dimension,
        )
        await self._vector_store.initialize()
        
        self._initialized = True
        logger.info("Memory store initialized")

    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        await self._db.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                strength REAL DEFAULT 1.0,
                importance REAL DEFAULT 0.5,
                emotional_valence TEXT DEFAULT 'neutral',
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}'
            );
            
            CREATE TABLE IF NOT EXISTS associations (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                association_type TEXT DEFAULT 'semantic',
                created_at TEXT NOT NULL,
                PRIMARY KEY (source_id, target_id),
                FOREIGN KEY (source_id) REFERENCES memories(id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES memories(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_memories_strength ON memories(strength);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
            CREATE INDEX IF NOT EXISTS idx_associations_source ON associations(source_id);
            CREATE INDEX IF NOT EXISTS idx_associations_target ON associations(target_id);
        """)
        await self._db.commit()

    async def close(self) -> None:
        """Close database and save vector store."""
        if self._vector_store:
            await self._vector_store.save()
        if self._db:
            await self._db.close()
        self._initialized = False
        logger.info("Memory store closed")

    # ===================
    # Memory Operations
    # ===================

    async def store(self, memory: Memory) -> None:
        """
        Store a memory.
        
        Args:
            memory: Memory to store
        """
        if not self._initialized:
            await self.initialize()
            
        # Store in SQLite
        await self._db.execute(
            """
            INSERT OR REPLACE INTO memories
            (id, content, memory_type, created_at, last_accessed,
             access_count, strength, importance, emotional_valence, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(memory.id),
                memory.content,
                memory.memory_type.value,
                memory.created_at.isoformat(),
                memory.last_accessed.isoformat(),
                memory.access_count,
                memory.strength,
                memory.importance,
                memory.emotional_valence.value,
                json.dumps(memory.tags),
                json.dumps(memory.metadata),
            ),
        )
        await self._db.commit()
        
        # Store embedding in vector store
        if memory.embedding:
            embedding = np.array(memory.embedding, dtype=np.float32)
            await self._vector_store.add(memory.id, embedding)

    async def get(self, memory_id: UUID) -> Memory | None:
        """
        Get a memory by ID.
        
        Args:
            memory_id: UUID of memory to retrieve
            
        Returns:
            Memory or None if not found
        """
        if not self._initialized:
            await self.initialize()
            
        cursor = await self._db.execute(
            "SELECT * FROM memories WHERE id = ?",
            (str(memory_id),),
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
            
        return self._row_to_memory(row)

    async def get_all(
        self,
        memory_types: list[MemoryType] | None = None,
        min_strength: float = 0.0,
        limit: int | None = None,
    ) -> list[Memory]:
        """
        Get all memories with optional filtering.
        
        Args:
            memory_types: Filter by memory types
            min_strength: Minimum strength threshold
            limit: Maximum number of memories
            
        Returns:
            List of memories
        """
        if not self._initialized:
            await self.initialize()
            
        query = "SELECT * FROM memories WHERE strength >= ?"
        params: list = [min_strength]
        
        if memory_types:
            placeholders = ",".join("?" * len(memory_types))
            query += f" AND memory_type IN ({placeholders})"
            params.extend(t.value for t in memory_types)
            
        query += " ORDER BY last_accessed DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        cursor = await self._db.execute(query, params)
        rows = await cursor.fetchall()
        
        return [self._row_to_memory(row) for row in rows]

    async def update(self, memory: Memory) -> None:
        """
        Update an existing memory.
        
        Args:
            memory: Memory with updated values
        """
        await self.store(memory)

    async def delete(self, memory_id: UUID) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: UUID of memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self._initialized:
            await self.initialize()
            
        cursor = await self._db.execute(
            "DELETE FROM memories WHERE id = ?",
            (str(memory_id),),
        )
        await self._db.commit()
        
        # Remove from vector store
        await self._vector_store.remove(memory_id)
        
        return cursor.rowcount > 0

    async def search(
        self,
        embedding: np.ndarray,
        limit: int = 10,
        threshold: float = 0.5,
        memory_types: list[MemoryType] | None = None,
        min_strength: float = 0.1,
    ) -> list[Memory]:
        """
        Search for similar memories using vector similarity.
        
        Args:
            embedding: Query embedding
            limit: Maximum results
            threshold: Minimum similarity threshold
            memory_types: Filter by memory types
            min_strength: Minimum strength threshold
            
        Returns:
            List of similar memories sorted by relevance
        """
        if not self._initialized:
            await self.initialize()
            
        # Get candidates from vector store
        candidates = await self._vector_store.search(
            query=embedding,
            k=limit * 2,  # Get more for filtering
            threshold=threshold,
        )
        
        # Fetch full memories and filter
        memories = []
        for uuid, similarity in candidates:
            memory = await self.get(uuid)
            if memory and memory.strength >= min_strength:
                if memory_types is None or memory.memory_type in memory_types:
                    memories.append(memory)
                    if len(memories) >= limit:
                        break
                        
        return memories

    # ===================
    # Association Operations
    # ===================

    async def create_association(
        self,
        source_id: UUID,
        target_id: UUID,
        strength: float = 0.5,
        association_type: str = "semantic",
    ) -> Association:
        """
        Create an association between two memories.
        
        Args:
            source_id: Source memory UUID
            target_id: Target memory UUID
            strength: Association strength
            association_type: Type of association
            
        Returns:
            Created Association
        """
        if not self._initialized:
            await self.initialize()
            
        from datetime import datetime
        
        association = Association(
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            association_type=association_type,
        )
        
        await self._db.execute(
            """
            INSERT OR REPLACE INTO associations
            (source_id, target_id, strength, association_type, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(source_id),
                str(target_id),
                strength,
                association_type,
                datetime.utcnow().isoformat(),
            ),
        )
        await self._db.commit()
        
        return association

    async def get_associations(self, memory_id: UUID) -> list[Association]:
        """
        Get all associations for a memory.
        
        Args:
            memory_id: Memory UUID
            
        Returns:
            List of associations
        """
        if not self._initialized:
            await self.initialize()
            
        cursor = await self._db.execute(
            """
            SELECT source_id, target_id, strength, association_type, created_at
            FROM associations
            WHERE source_id = ? OR target_id = ?
            """,
            (str(memory_id), str(memory_id)),
        )
        rows = await cursor.fetchall()
        
        return [
            Association(
                source_id=UUID(row[0]),
                target_id=UUID(row[1]),
                strength=row[2],
                association_type=row[3],
            )
            for row in rows
        ]

    async def strengthen_association(
        self,
        source_id: UUID,
        target_id: UUID,
        amount: float = 0.1,
    ) -> None:
        """Strengthen an association between memories."""
        await self._db.execute(
            """
            UPDATE associations
            SET strength = MIN(1.0, strength + ?)
            WHERE source_id = ? AND target_id = ?
            """,
            (amount, str(source_id), str(target_id)),
        )
        await self._db.commit()

    # ===================
    # Helper Methods
    # ===================

    def _row_to_memory(self, row: tuple) -> Memory:
        """Convert database row to Memory object."""
        from datetime import datetime
        from neurogenesis.core.types import EmotionalValence
        
        return Memory(
            id=UUID(row[0]),
            content=row[1],
            memory_type=MemoryType(row[2]),
            created_at=datetime.fromisoformat(row[3]),
            last_accessed=datetime.fromisoformat(row[4]),
            access_count=row[5],
            strength=row[6],
            importance=row[7],
            emotional_valence=EmotionalValence(row[8]),
            tags=json.loads(row[9]),
            metadata=json.loads(row[10]),
        )
