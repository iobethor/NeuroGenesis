"""Tests for memory operations."""

import pytest

from neurogenesis.core.mind import Mind
from neurogenesis.core.types import Memory, MemoryType


@pytest.mark.asyncio
async def test_remember_and_recall(mind: Mind):
    """Test storing and retrieving memories."""
    # Store a memory
    memory = await mind.remember(
        content="Python is a programming language",
        memory_type=MemoryType.SEMANTIC,
        importance=0.8,
        tags=["programming", "python"],
    )
    
    assert memory.id is not None
    assert memory.content == "Python is a programming language"
    assert memory.memory_type == MemoryType.SEMANTIC
    assert memory.importance == 0.8
    assert "programming" in memory.tags
    assert memory.embedding is not None


@pytest.mark.asyncio
async def test_recall_similar_memories(mind: Mind):
    """Test semantic search for memories."""
    # Store multiple related memories
    await mind.remember(
        content="Machine learning is a subset of AI",
        tags=["ml", "ai"],
    )
    await mind.remember(
        content="Deep learning uses neural networks",
        tags=["ml", "deep-learning"],
    )
    await mind.remember(
        content="Cooking pasta requires boiling water",
        tags=["cooking"],
    )
    
    # Recall related memories
    memories = await mind.recall("What is artificial intelligence?", limit=2)
    
    # Should find ML-related memories, not cooking
    assert len(memories) >= 1
    contents = [m.content for m in memories]
    assert any("AI" in c or "learning" in c for c in contents)


@pytest.mark.asyncio
async def test_memory_decay(mind: Mind):
    """Test that memories decay over time."""
    memory = await mind.remember(
        content="Test memory for decay",
        importance=0.5,
    )
    
    initial_strength = memory.strength
    
    # Apply decay
    memory.decay(0.1)
    
    assert memory.strength < initial_strength
    assert memory.strength == initial_strength - 0.1


@pytest.mark.asyncio
async def test_memory_reinforcement(mind: Mind):
    """Test that accessing memories reinforces them."""
    memory = await mind.remember(
        content="Reinforcement test memory",
        importance=0.5,
    )
    
    # Access the memory
    memories = await mind.recall("Reinforcement test", limit=1)
    
    assert len(memories) >= 1
    # Memory should have been accessed
    assert memories[0].access_count >= 1


@pytest.mark.asyncio
async def test_forget_memory(mind: Mind):
    """Test forgetting memories."""
    memory = await mind.remember(
        content="Memory to forget",
        importance=0.5,
    )
    
    # Force forget
    result = await mind.forget(memory.id, force=True)
    
    assert result is True
    
    # Verify memory is gone
    retrieved = await mind._memory_store.get(memory.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_memory_types(mind: Mind):
    """Test different memory types."""
    # Store different types
    semantic = await mind.remember(
        content="The Earth orbits the Sun",
        memory_type=MemoryType.SEMANTIC,
    )
    episodic = await mind.remember(
        content="Yesterday I learned about astronomy",
        memory_type=MemoryType.EPISODIC,
    )
    procedural = await mind.remember(
        content="To observe stars, use a telescope at night",
        memory_type=MemoryType.PROCEDURAL,
    )
    
    # Verify types
    assert semantic.memory_type == MemoryType.SEMANTIC
    assert episodic.memory_type == MemoryType.EPISODIC
    assert procedural.memory_type == MemoryType.PROCEDURAL
    
    # Recall with type filter
    semantic_memories = await mind.recall(
        "astronomy",
        memory_types=[MemoryType.SEMANTIC],
        limit=10,
    )
    
    # Should only get semantic memories
    for m in semantic_memories:
        assert m.memory_type == MemoryType.SEMANTIC
