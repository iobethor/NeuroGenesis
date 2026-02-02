"""API routes for NeuroGenesis."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from neurogenesis.api.app import get_mind
from neurogenesis.core.mind import Mind
from neurogenesis.core.types import GrowthMetrics, Memory, MemoryType, Thought

router = APIRouter(tags=["mind"])


# ===================
# Request/Response Models
# ===================


class RememberRequest(BaseModel):
    """Request to store a new memory."""
    
    content: str = Field(..., description="Content to remember")
    memory_type: MemoryType = Field(default=MemoryType.SEMANTIC)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RecallRequest(BaseModel):
    """Request to recall memories."""
    
    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100)
    memory_types: list[MemoryType] | None = Field(default=None)
    min_strength: float = Field(default=0.1, ge=0.0, le=1.0)


class ThinkRequest(BaseModel):
    """Request to process a thought."""
    
    content: str = Field(..., description="Thought content")
    context: dict[str, Any] = Field(default_factory=dict)


class MemoryResponse(BaseModel):
    """Memory response model."""
    
    id: UUID
    content: str
    memory_type: MemoryType
    strength: float
    importance: float
    access_count: int
    tags: list[str]
    created_at: str
    
    @classmethod
    def from_memory(cls, memory: Memory) -> "MemoryResponse":
        return cls(
            id=memory.id,
            content=memory.content,
            memory_type=memory.memory_type,
            strength=memory.strength,
            importance=memory.importance,
            access_count=memory.access_count,
            tags=memory.tags,
            created_at=memory.created_at.isoformat(),
        )


class ThoughtResponse(BaseModel):
    """Thought response model."""
    
    id: UUID
    content: str
    response: str | None
    confidence: float
    related_memories: list[UUID]
    timestamp: str
    
    @classmethod
    def from_thought(cls, thought: Thought) -> "ThoughtResponse":
        return cls(
            id=thought.id,
            content=thought.content,
            response=thought.generated_response,
            confidence=thought.confidence,
            related_memories=thought.related_memories,
            timestamp=thought.timestamp.isoformat(),
        )


# ===================
# Memory Endpoints
# ===================


@router.post("/remember", response_model=MemoryResponse)
async def remember(
    request: RememberRequest,
    mind: Mind = Depends(get_mind),
) -> MemoryResponse:
    """
    Store a new memory.
    
    Creates a new memory with the provided content and metadata,
    automatically generating embeddings and associations.
    """
    memory = await mind.remember(
        content=request.content,
        memory_type=request.memory_type,
        importance=request.importance,
        tags=request.tags,
        metadata=request.metadata,
    )
    return MemoryResponse.from_memory(memory)


@router.post("/recall", response_model=list[MemoryResponse])
async def recall(
    request: RecallRequest,
    mind: Mind = Depends(get_mind),
) -> list[MemoryResponse]:
    """
    Recall memories related to a query.
    
    Performs semantic search to find relevant memories.
    """
    memories = await mind.recall(
        query=request.query,
        limit=request.limit,
        memory_types=request.memory_types,
        min_strength=request.min_strength,
    )
    return [MemoryResponse.from_memory(m) for m in memories]


@router.get("/memory/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: UUID,
    mind: Mind = Depends(get_mind),
) -> MemoryResponse:
    """Get a specific memory by ID."""
    memory = await mind._memory_store.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return MemoryResponse.from_memory(memory)


@router.delete("/memory/{memory_id}")
async def forget_memory(
    memory_id: UUID,
    force: bool = Query(default=False),
    mind: Mind = Depends(get_mind),
) -> dict:
    """
    Forget a specific memory.
    
    If force=True, immediately deletes the memory.
    Otherwise, applies gradual decay.
    """
    success = await mind.forget(memory_id, force=force)
    return {"success": success, "memory_id": str(memory_id)}


# ===================
# Thinking Endpoints
# ===================


@router.post("/think", response_model=ThoughtResponse)
async def think(
    request: ThinkRequest,
    mind: Mind = Depends(get_mind),
) -> ThoughtResponse:
    """
    Process a thought and generate a response.
    
    Uses stored memories to form a contextual response.
    """
    thought = await mind.think(
        content=request.content,
        context=request.context,
    )
    return ThoughtResponse.from_thought(thought)


# ===================
# Growth Endpoints
# ===================


@router.post("/grow", response_model=GrowthMetrics)
async def grow(
    mind: Mind = Depends(get_mind),
) -> GrowthMetrics:
    """
    Trigger a growth cycle.
    
    Consolidates memories, applies decay, and strengthens patterns.
    """
    return await mind.grow()


@router.get("/metrics", response_model=GrowthMetrics)
async def get_metrics(
    mind: Mind = Depends(get_mind),
) -> GrowthMetrics:
    """Get current growth metrics."""
    return mind.get_metrics()


# ===================
# Batch Endpoints
# ===================


@router.post("/remember/batch", response_model=list[MemoryResponse])
async def remember_batch(
    memories: list[RememberRequest],
    mind: Mind = Depends(get_mind),
) -> list[MemoryResponse]:
    """Store multiple memories in batch."""
    results = []
    for request in memories:
        memory = await mind.remember(
            content=request.content,
            memory_type=request.memory_type,
            importance=request.importance,
            tags=request.tags,
            metadata=request.metadata,
        )
        results.append(MemoryResponse.from_memory(memory))
    return results
