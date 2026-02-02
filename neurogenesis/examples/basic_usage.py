"""Basic usage example for NeuroGenesis."""

import asyncio

from neurogenesis import Mind
from neurogenesis.core.types import MemoryType


async def main() -> None:
    """Demonstrate basic NeuroGenesis functionality."""
    print("=== NeuroGenesis Basic Usage ===\n")
    
    # Create and initialize the mind
    async with Mind() as mind:
        # 1. Store some memories
        print("1. Storing memories...")
        
        memories = [
            ("Python is a high-level programming language", ["programming", "python"]),
            ("Machine learning is a subset of artificial intelligence", ["ml", "ai"]),
            ("Neural networks are inspired by biological neurons", ["ml", "neural"]),
            ("Deep learning uses multiple layers of neural networks", ["ml", "deep-learning"]),
            ("The capital of France is Paris", ["geography", "france"]),
        ]
        
        for content, tags in memories:
            memory = await mind.remember(
                content=content,
                memory_type=MemoryType.SEMANTIC,
                importance=0.7,
                tags=tags,
            )
            print(f"  Stored: {content[:50]}...")
        
        print()
        
        # 2. Recall memories
        print("2. Recalling memories about 'artificial intelligence'...")
        recalled = await mind.recall(
            query="artificial intelligence and machine learning",
            limit=3,
        )
        
        for memory in recalled:
            print(f"  - {memory.content}")
            print(f"    Strength: {memory.strength:.2f}, Tags: {memory.tags}")
        
        print()
        
        # 3. Process a thought
        print("3. Processing a thought...")
        thought = await mind.think("What do I know about neural networks?")
        
        print(f"  Query: {thought.content}")
        print(f"  Response: {thought.generated_response}")
        print(f"  Confidence: {thought.confidence:.2f}")
        print(f"  Related memories: {len(thought.related_memories)}")
        
        print()
        
        # 4. Run growth cycle
        print("4. Running growth cycle...")
        metrics = await mind.grow()
        
        print(f"  Total memories: {metrics.total_memories}")
        print(f"  Active memories: {metrics.active_memories}")
        print(f"  Consolidation cycles: {metrics.consolidation_cycles}")
        print(f"  Average strength: {metrics.average_memory_strength:.2f}")
        
        print()
        
        # 5. Try recalling unrelated topic
        print("5. Recalling memories about 'geography'...")
        geography = await mind.recall(
            query="European capitals and cities",
            limit=2,
        )
        
        for memory in geography:
            print(f"  - {memory.content}")
        
        print("\n=== Done ===")


if __name__ == "__main__":
    asyncio.run(main())
