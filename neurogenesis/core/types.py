"""Core types and data structures for NeuroGenesis."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import numpy as np
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memories in the system."""

    EPISODIC = "episodic"  # Specific events/experiences
    SEMANTIC = "semantic"  # Facts and concepts
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"  # Short-term active memory


class EmotionalValence(str, Enum):
    """Emotional coloring of memories."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Memory(BaseModel):
    """A single memory unit in the system."""

    id: UUID = Field(default_factory=uuid4)
    content: str = Field(..., description="The textual content of the memory")
    memory_type: MemoryType = Field(default=MemoryType.SEMANTIC)
    embedding: list[float] | None = Field(default=None, description="Vector embedding")
    
    # Temporal information
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    access_count: int = Field(default=0)
    
    # Memory strength and relevance
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_valence: EmotionalValence = Field(default=EmotionalValence.NEUTRAL)
    
    # Connections to other memories
    associations: list[UUID] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def decay(self, rate: float) -> None:
        """Apply memory decay based on time since last access."""
        self.strength = max(0.0, self.strength - rate)

    def reinforce(self, amount: float = 0.1) -> None:
        """Reinforce memory strength through access."""
        self.strength = min(1.0, self.strength + amount)
        self.access_count += 1
        self.last_accessed = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Check if memory is still active (not fully decayed)."""
        return self.strength > 0.1

    def to_vector(self) -> np.ndarray | None:
        """Convert embedding to numpy array."""
        if self.embedding:
            return np.array(self.embedding, dtype=np.float32)
        return None


class Thought(BaseModel):
    """A thought or query processed by the mind."""

    id: UUID = Field(default_factory=uuid4)
    content: str = Field(..., description="The thought content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Processing results
    embedding: list[float] | None = Field(default=None)
    related_memories: list[UUID] = Field(default_factory=list)
    generated_response: str | None = Field(default=None)
    
    # Context
    context: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class Association(BaseModel):
    """Connection between two memories."""

    source_id: UUID
    target_id: UUID
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    association_type: str = Field(default="semantic")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def strengthen(self, amount: float = 0.1) -> None:
        """Strengthen the association."""
        self.strength = min(1.0, self.strength + amount)

    def weaken(self, amount: float = 0.1) -> None:
        """Weaken the association."""
        self.strength = max(0.0, self.strength - amount)


class GrowthMetrics(BaseModel):
    """Metrics tracking the growth of the mind."""

    total_memories: int = 0
    active_memories: int = 0
    total_associations: int = 0
    average_memory_strength: float = 0.0
    consolidation_cycles: int = 0
    knowledge_domains: dict[str, int] = Field(default_factory=dict)
    growth_history: list[dict[str, Any]] = Field(default_factory=list)
