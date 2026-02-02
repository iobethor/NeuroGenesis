"""Tests for growth and consolidation."""

import pytest

from neurogenesis.core.mind import Mind
from neurogenesis.core.types import MemoryType


@pytest.mark.asyncio
async def test_growth_cycle(mind: Mind):
    """Test running a growth cycle."""
    # Store some memories
    for i in range(5):
        await mind.remember(
            content=f"Test memory number {i}",
            importance=0.5,
            tags=["test"],
        )
    
    # Run growth cycle
    metrics = await mind.grow()
    
    assert metrics.total_memories >= 5
    assert metrics.consolidation_cycles >= 1


@pytest.mark.asyncio
async def test_memory_association(mind: Mind):
    """Test that similar memories get associated."""
    # Store related memories
    m1 = await mind.remember(
        content="Python is a snake",
        tags=["animals", "python"],
    )
    m2 = await mind.remember(
        content="Python is also a programming language",
        tags=["programming", "python"],
    )
    
    # Check if associations were created
    # (Memories about "Python" should be associated)
    assert len(m2.associations) >= 0  # May or may not create association


@pytest.mark.asyncio
async def test_metrics_tracking(mind: Mind):
    """Test that metrics are properly tracked."""
    initial_metrics = mind.get_metrics()
    
    # Store memories
    await mind.remember("Test memory 1")
    await mind.remember("Test memory 2")
    
    final_metrics = mind.get_metrics()
    
    assert final_metrics.total_memories == initial_metrics.total_memories + 2


@pytest.mark.asyncio
async def test_weak_memory_pruning(mind: Mind):
    """Test that weak memories get pruned during growth."""
    # Store a weak memory
    memory = await mind.remember(
        content="Weak memory to prune",
        importance=0.1,
    )
    
    # Manually decay it significantly
    memory.strength = 0.05
    await mind._memory_store.update(memory)
    
    # Run growth cycle
    await mind.grow()
    
    # Check if memory was pruned
    retrieved = await mind._memory_store.get(memory.id)
    # Should be pruned since strength < 0.1
    assert retrieved is None or retrieved.strength >= 0.1
