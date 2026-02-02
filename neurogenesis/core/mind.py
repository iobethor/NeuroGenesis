"""The Mind - central orchestrator of NeuroGenesis."""

import asyncio
from typing import Any
from uuid import UUID

import structlog

from neurogenesis.core.config import Settings, settings
from neurogenesis.core.types import (
    GrowthMetrics,
    Memory,
    MemoryType,
    Thought,
)
from neurogenesis.memory.store import MemoryStore
from neurogenesis.memory.embeddings import EmbeddingEngine
from neurogenesis.growth.consolidator import MemoryConsolidator
from neurogenesis.growth.patterns import PatternRecognizer

logger = structlog.get_logger()


class Mind:
    """
    The central mind of NeuroGenesis.
    
    Orchestrates memory storage, retrieval, growth, and learning processes.
    """

    def __init__(self, config: Settings | None = None) -> None:
        """Initialize the Mind with given configuration."""
        self.config = config or settings
        self.config.ensure_directories()
        
        # Core components
        self._memory_store: MemoryStore | None = None
        self._embedding_engine: EmbeddingEngine | None = None
        self._consolidator: MemoryConsolidator | None = None
        self._pattern_recognizer: PatternRecognizer | None = None
        
        # State
        self._initialized = False
        self._metrics = GrowthMetrics()
        
        logger.info("Mind created", config=self.config.model_dump())

    async def initialize(self) -> None:
        """Initialize all mind components."""
        if self._initialized:
            return
            
        logger.info("Initializing mind...")
        
        # Initialize embedding engine
        self._embedding_engine = EmbeddingEngine(
            model_name=self.config.embedding_model,
            dimension=self.config.embedding_dimension,
        )
        await self._embedding_engine.initialize()
        
        # Initialize memory store
        self._memory_store = MemoryStore(
            db_path=self.config.memory_db_path,
            vector_path=self.config.vector_store_path,
            embedding_engine=self._embedding_engine,
        )
        await self._memory_store.initialize()
        
        # Initialize growth components
        self._consolidator = MemoryConsolidator(
            memory_store=self._memory_store,
            threshold=self.config.consolidation_threshold,
        )
        
        self._pattern_recognizer = PatternRecognizer(
            embedding_engine=self._embedding_engine,
        )
        
        self._initialized = True
        logger.info("Mind initialized successfully")

    async def close(self) -> None:
        """Cleanup and close all resources."""
        if self._memory_store:
            await self._memory_store.close()
        self._initialized = False
        logger.info("Mind closed")

    async def __aenter__(self) -> "Mind":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    # ===================
    # Memory Operations
    # ===================

    async def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SEMANTIC,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """
        Store a new memory.
        
        Args:
            content: The content to remember
            memory_type: Type of memory (semantic, episodic, etc.)
            importance: Importance score (0-1)
            tags: Optional tags for categorization
            metadata: Optional additional metadata
            
        Returns:
            The created Memory object
        """
        self._ensure_initialized()
        
        # Create embedding
        embedding = await self._embedding_engine.embed(content)
        
        # Create memory
        memory = Memory(
            content=content,
            memory_type=memory_type,
            embedding=embedding.tolist(),
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        # Store memory
        await self._memory_store.store(memory)
        
        # Find and create associations
        similar_memories = await self._memory_store.search(
            embedding=embedding,
            limit=5,
            threshold=0.7,
        )
        
        for similar in similar_memories:
            if similar.id != memory.id:
                await self._memory_store.create_association(
                    source_id=memory.id,
                    target_id=similar.id,
                    strength=0.5,
                )
                memory.associations.append(similar.id)
        
        # Update metrics
        self._metrics.total_memories += 1
        self._metrics.active_memories += 1
        
        # Check for consolidation
        if self._metrics.total_memories % self.config.consolidation_threshold == 0:
            asyncio.create_task(self._consolidate())
        
        logger.info("Memory stored", memory_id=str(memory.id), type=memory_type)
        return memory

    async def recall(
        self,
        query: str,
        limit: int = 10,
        memory_types: list[MemoryType] | None = None,
        min_strength: float = 0.1,
    ) -> list[Memory]:
        """
        Recall memories related to a query.
        
        Args:
            query: The search query
            limit: Maximum number of memories to return
            memory_types: Filter by memory types
            min_strength: Minimum memory strength threshold
            
        Returns:
            List of relevant memories
        """
        self._ensure_initialized()
        
        # Create query embedding
        query_embedding = await self._embedding_engine.embed(query)
        
        # Search memories
        memories = await self._memory_store.search(
            embedding=query_embedding,
            limit=limit,
            memory_types=memory_types,
            min_strength=min_strength,
        )
        
        # Reinforce accessed memories
        for memory in memories:
            memory.reinforce()
            await self._memory_store.update(memory)
        
        logger.info("Recalled memories", query=query[:50], count=len(memories))
        return memories

    async def think(self, content: str, context: dict[str, Any] | None = None) -> Thought:
        """
        Process a thought and generate a response based on memories.
        
        Args:
            content: The thought content
            context: Optional context for the thought
            
        Returns:
            Processed Thought object with related memories
        """
        self._ensure_initialized()
        
        # Create thought
        thought = Thought(content=content, context=context or {})
        
        # Get embedding
        embedding = await self._embedding_engine.embed(content)
        thought.embedding = embedding.tolist()
        
        # Find related memories
        memories = await self.recall(content, limit=5)
        thought.related_memories = [m.id for m in memories]
        
        # Recognize patterns
        patterns = await self._pattern_recognizer.find_patterns(
            current=embedding,
            memories=memories,
        )
        
        # Generate response based on memories and patterns
        if memories:
            most_relevant = memories[0]
            thought.generated_response = self._synthesize_response(
                query=content,
                memories=memories,
                patterns=patterns,
            )
            thought.confidence = most_relevant.strength * 0.8
        else:
            thought.generated_response = "I don't have relevant memories for this."
            thought.confidence = 0.1
        
        logger.info(
            "Thought processed",
            thought_id=str(thought.id),
            related_memories=len(memories),
        )
        return thought

    async def forget(self, memory_id: UUID, force: bool = False) -> bool:
        """
        Forget a specific memory.
        
        Args:
            memory_id: ID of memory to forget
            force: If True, immediately delete; otherwise decay gradually
            
        Returns:
            True if memory was forgotten
        """
        self._ensure_initialized()
        
        if force:
            await self._memory_store.delete(memory_id)
            self._metrics.total_memories -= 1
            logger.info("Memory forcefully forgotten", memory_id=str(memory_id))
            return True
        
        # Gradual decay
        memory = await self._memory_store.get(memory_id)
        if memory:
            memory.decay(self.config.decay_rate * 10)
            if not memory.is_active:
                await self._memory_store.delete(memory_id)
                self._metrics.active_memories -= 1
                return True
            await self._memory_store.update(memory)
        
        return False

    # ===================
    # Growth Operations
    # ===================

    async def _consolidate(self) -> None:
        """Run memory consolidation process."""
        if self._consolidator:
            result = await self._consolidator.consolidate()
            self._metrics.consolidation_cycles += 1
            logger.info("Consolidation complete", result=result)

    async def grow(self) -> GrowthMetrics:
        """
        Trigger a growth cycle.
        
        This includes:
        - Memory consolidation
        - Decay of unused memories
        - Pattern strengthening
        - Association refinement
        """
        self._ensure_initialized()
        
        logger.info("Starting growth cycle...")
        
        # Apply decay to all memories
        all_memories = await self._memory_store.get_all()
        for memory in all_memories:
            memory.decay(self.config.decay_rate)
            if not memory.is_active:
                await self._memory_store.delete(memory.id)
                self._metrics.active_memories -= 1
            else:
                await self._memory_store.update(memory)
        
        # Consolidate memories
        await self._consolidate()
        
        # Update metrics
        self._metrics.average_memory_strength = sum(
            m.strength for m in await self._memory_store.get_all()
        ) / max(1, self._metrics.active_memories)
        
        self._metrics.growth_history.append({
            "cycle": self._metrics.consolidation_cycles,
            "total_memories": self._metrics.total_memories,
            "active_memories": self._metrics.active_memories,
            "avg_strength": self._metrics.average_memory_strength,
        })
        
        logger.info("Growth cycle complete", metrics=self._metrics.model_dump())
        return self._metrics

    def get_metrics(self) -> GrowthMetrics:
        """Get current growth metrics."""
        return self._metrics

    # ===================
    # Helper Methods
    # ===================

    def _ensure_initialized(self) -> None:
        """Ensure the mind is initialized before operations."""
        if not self._initialized:
            raise RuntimeError("Mind not initialized. Call initialize() first.")

    def _synthesize_response(
        self,
        query: str,
        memories: list[Memory],
        patterns: list[dict[str, Any]],
    ) -> str:
        """Synthesize a response from memories and patterns."""
        if not memories:
            return "No relevant information found."
        
        # Combine most relevant memories
        response_parts = []
        for memory in memories[:3]:
            response_parts.append(f"• {memory.content}")
        
        response = "Based on my memories:\n" + "\n".join(response_parts)
        
        if patterns:
            response += f"\n\nI also notice {len(patterns)} related patterns."
        
        return response
