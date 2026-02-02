"""Memory consolidation for the growing mind."""

from typing import Any
from uuid import UUID

import structlog

from neurogenesis.core.types import Memory, MemoryType

logger = structlog.get_logger()


class MemoryConsolidator:
    """
    Consolidates memories to improve storage efficiency and recall.
    
    Implements memory consolidation patterns inspired by:
    - Sleep consolidation (strengthening important memories)
    - Semantic clustering (grouping related concepts)
    - Forgetting (pruning weak/unused memories)
    """

    def __init__(
        self,
        memory_store: Any,  # MemoryStore, avoiding circular import
        threshold: int = 100,
    ) -> None:
        """
        Initialize consolidator.
        
        Args:
            memory_store: Memory store instance
            threshold: Number of memories before consolidation triggers
        """
        self.memory_store = memory_store
        self.threshold = threshold
        self._consolidation_count = 0

    async def consolidate(self) -> dict[str, Any]:
        """
        Run a full consolidation cycle.
        
        Returns:
            Dict with consolidation statistics
        """
        logger.info("Starting memory consolidation...")
        
        stats = {
            "memories_processed": 0,
            "memories_pruned": 0,
            "memories_strengthened": 0,
            "clusters_formed": 0,
            "associations_created": 0,
        }
        
        # Get all active memories
        memories = await self.memory_store.get_all()
        stats["memories_processed"] = len(memories)
        
        # Phase 1: Prune weak memories
        pruned = await self._prune_weak_memories(memories)
        stats["memories_pruned"] = pruned
        
        # Phase 2: Strengthen important memories
        strengthened = await self._strengthen_important(memories)
        stats["memories_strengthened"] = strengthened
        
        # Phase 3: Form semantic clusters
        clusters = await self._form_clusters(memories)
        stats["clusters_formed"] = len(clusters)
        
        # Phase 4: Create new associations
        associations = await self._create_associations(clusters)
        stats["associations_created"] = associations
        
        self._consolidation_count += 1
        
        logger.info("Consolidation complete", stats=stats)
        return stats

    async def _prune_weak_memories(self, memories: list[Memory]) -> int:
        """
        Prune memories that are too weak to be useful.
        
        Memories are pruned if:
        - Strength < 0.1
        - Never accessed and low importance
        """
        pruned = 0
        for memory in memories:
            should_prune = (
                memory.strength < 0.1 or
                (memory.access_count == 0 and memory.importance < 0.3)
            )
            
            if should_prune:
                await self.memory_store.delete(memory.id)
                pruned += 1
                logger.debug("Pruned weak memory", memory_id=str(memory.id))
                
        return pruned

    async def _strengthen_important(self, memories: list[Memory]) -> int:
        """
        Strengthen memories that are frequently accessed or important.
        
        Strengthening criteria:
        - High access count
        - High importance score
        - Strong emotional valence
        """
        strengthened = 0
        
        for memory in memories:
            strength_boost = 0.0
            
            # Boost for frequent access
            if memory.access_count > 5:
                strength_boost += 0.05
            if memory.access_count > 20:
                strength_boost += 0.05
                
            # Boost for importance
            if memory.importance > 0.7:
                strength_boost += 0.05
                
            # Boost for emotional salience
            if memory.emotional_valence.value != "neutral":
                strength_boost += 0.03
                
            if strength_boost > 0:
                memory.reinforce(strength_boost)
                await self.memory_store.update(memory)
                strengthened += 1
                
        return strengthened

    async def _form_clusters(
        self,
        memories: list[Memory],
    ) -> list[list[Memory]]:
        """
        Group related memories into clusters.
        
        Uses tag similarity and content overlap.
        """
        clusters: list[list[Memory]] = []
        
        # Group by memory type first
        type_groups: dict[MemoryType, list[Memory]] = {}
        for memory in memories:
            if memory.memory_type not in type_groups:
                type_groups[memory.memory_type] = []
            type_groups[memory.memory_type].append(memory)
        
        # Within each type, group by shared tags
        for memory_type, type_memories in type_groups.items():
            tag_groups: dict[str, list[Memory]] = {}
            
            for memory in type_memories:
                for tag in memory.tags:
                    if tag not in tag_groups:
                        tag_groups[tag] = []
                    tag_groups[tag].append(memory)
            
            # Create clusters from tag groups with 2+ memories
            for tag, group in tag_groups.items():
                if len(group) >= 2:
                    clusters.append(group)
                    
        return clusters

    async def _create_associations(
        self,
        clusters: list[list[Memory]],
    ) -> int:
        """
        Create associations between memories in the same cluster.
        """
        associations_created = 0
        
        for cluster in clusters:
            for i, memory1 in enumerate(cluster):
                for memory2 in cluster[i + 1:]:
                    # Check if association already exists
                    existing = await self.memory_store.get_associations(memory1.id)
                    already_associated = any(
                        a.target_id == memory2.id or a.source_id == memory2.id
                        for a in existing
                    )
                    
                    if not already_associated:
                        await self.memory_store.create_association(
                            source_id=memory1.id,
                            target_id=memory2.id,
                            strength=0.5,
                            association_type="cluster",
                        )
                        associations_created += 1
                    else:
                        # Strengthen existing association
                        await self.memory_store.strengthen_association(
                            source_id=memory1.id,
                            target_id=memory2.id,
                            amount=0.05,
                        )
                        
        return associations_created

    async def merge_similar(
        self,
        threshold: float = 0.95,
    ) -> int:
        """
        Merge very similar memories into single entries.
        
        Args:
            threshold: Similarity threshold for merging
            
        Returns:
            Number of memories merged
        """
        merged = 0
        memories = await self.memory_store.get_all()
        
        # Track which memories have been merged
        merged_ids: set[UUID] = set()
        
        for i, memory1 in enumerate(memories):
            if memory1.id in merged_ids:
                continue
                
            for memory2 in memories[i + 1:]:
                if memory2.id in merged_ids:
                    continue
                    
                # Check similarity
                if memory1.embedding and memory2.embedding:
                    import numpy as np
                    emb1 = np.array(memory1.embedding)
                    emb2 = np.array(memory2.embedding)
                    similarity = np.dot(emb1, emb2) / (
                        np.linalg.norm(emb1) * np.linalg.norm(emb2)
                    )
                    
                    if similarity >= threshold:
                        # Merge: keep the stronger/more accessed memory
                        if (
                            memory2.strength > memory1.strength or
                            memory2.access_count > memory1.access_count
                        ):
                            keep, remove = memory2, memory1
                        else:
                            keep, remove = memory1, memory2
                            
                        # Transfer attributes
                        keep.tags = list(set(keep.tags + remove.tags))
                        keep.associations.extend(remove.associations)
                        keep.reinforce(remove.strength * 0.5)
                        
                        await self.memory_store.update(keep)
                        await self.memory_store.delete(remove.id)
                        
                        merged_ids.add(remove.id)
                        merged += 1
                        
        logger.info("Merged similar memories", count=merged)
        return merged
