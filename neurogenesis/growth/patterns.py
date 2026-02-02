"""Pattern recognition for learning and growth."""

from typing import Any

import numpy as np
import structlog

from neurogenesis.core.types import Memory

logger = structlog.get_logger()


class PatternRecognizer:
    """
    Recognizes patterns across memories to enable learning.
    
    Implements:
    - Semantic pattern detection
    - Temporal sequence recognition
    - Concept abstraction
    """

    def __init__(self, embedding_engine: Any) -> None:
        """
        Initialize pattern recognizer.
        
        Args:
            embedding_engine: Engine for semantic analysis
        """
        self.embedding_engine = embedding_engine
        self._learned_patterns: list[dict[str, Any]] = []

    async def find_patterns(
        self,
        current: np.ndarray,
        memories: list[Memory],
    ) -> list[dict[str, Any]]:
        """
        Find patterns between current input and stored memories.
        
        Args:
            current: Current embedding
            memories: Related memories
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if not memories:
            return patterns
            
        # Collect embeddings
        embeddings = []
        for memory in memories:
            if memory.embedding:
                embeddings.append(np.array(memory.embedding))
                
        if not embeddings:
            return patterns
            
        embeddings_matrix = np.array(embeddings)
        
        # Pattern 1: Semantic clustering
        cluster_pattern = await self._detect_semantic_cluster(
            current, embeddings_matrix, memories
        )
        if cluster_pattern:
            patterns.append(cluster_pattern)
            
        # Pattern 2: Temporal sequence
        temporal_pattern = await self._detect_temporal_sequence(memories)
        if temporal_pattern:
            patterns.append(temporal_pattern)
            
        # Pattern 3: Common themes
        theme_patterns = await self._detect_themes(memories)
        patterns.extend(theme_patterns)
        
        # Pattern 4: Concept abstraction
        abstract_pattern = await self._abstract_concept(memories)
        if abstract_pattern:
            patterns.append(abstract_pattern)
            
        return patterns

    async def _detect_semantic_cluster(
        self,
        current: np.ndarray,
        embeddings: np.ndarray,
        memories: list[Memory],
    ) -> dict[str, Any] | None:
        """Detect if memories form a semantic cluster."""
        if len(embeddings) < 2:
            return None
            
        # Calculate centroid
        centroid = np.mean(embeddings, axis=0)
        
        # Calculate distance from current to centroid
        current_dist = np.linalg.norm(current - centroid)
        
        # Calculate average distance within cluster
        distances = [np.linalg.norm(e - centroid) for e in embeddings]
        avg_dist = np.mean(distances)
        std_dist = np.std(distances)
        
        # Check if current is within cluster bounds
        if current_dist <= avg_dist + std_dist:
            return {
                "type": "semantic_cluster",
                "strength": 1.0 - (current_dist / (avg_dist + std_dist + 0.01)),
                "members": [str(m.id) for m in memories],
                "centroid_distance": float(current_dist),
            }
            
        return None

    async def _detect_temporal_sequence(
        self,
        memories: list[Memory],
    ) -> dict[str, Any] | None:
        """Detect temporal patterns in memories."""
        if len(memories) < 3:
            return None
            
        # Sort by creation time
        sorted_memories = sorted(memories, key=lambda m: m.created_at)
        
        # Check for regular intervals
        intervals = []
        for i in range(1, len(sorted_memories)):
            delta = (
                sorted_memories[i].created_at - sorted_memories[i-1].created_at
            )
            intervals.append(delta.total_seconds())
            
        if not intervals:
            return None
            
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # If intervals are relatively consistent, we have a temporal pattern
        coefficient_of_variation = std_interval / (avg_interval + 0.01)
        
        if coefficient_of_variation < 0.5:  # Low variation = consistent pattern
            return {
                "type": "temporal_sequence",
                "strength": 1.0 - coefficient_of_variation,
                "average_interval": float(avg_interval),
                "sequence": [str(m.id) for m in sorted_memories],
            }
            
        return None

    async def _detect_themes(
        self,
        memories: list[Memory],
    ) -> list[dict[str, Any]]:
        """Detect common themes across memories."""
        patterns = []
        
        # Collect all tags
        tag_counts: dict[str, list[str]] = {}
        for memory in memories:
            for tag in memory.tags:
                if tag not in tag_counts:
                    tag_counts[tag] = []
                tag_counts[tag].append(str(memory.id))
                
        # Find significant themes (appear in multiple memories)
        for tag, memory_ids in tag_counts.items():
            if len(memory_ids) >= 2:
                patterns.append({
                    "type": "theme",
                    "theme": tag,
                    "strength": len(memory_ids) / len(memories),
                    "members": memory_ids,
                })
                
        return patterns

    async def _abstract_concept(
        self,
        memories: list[Memory],
    ) -> dict[str, Any] | None:
        """Attempt to abstract a higher-level concept from memories."""
        if len(memories) < 3:
            return None
            
        # Collect common words from content
        word_counts: dict[str, int] = {}
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "and", "but", "or", "nor", "so", "yet", "both", "either",
            "neither", "not", "only", "own", "same", "than", "too",
            "very", "just", "also",
        }
        
        for memory in memories:
            words = memory.content.lower().split()
            for word in words:
                # Clean word
                word = "".join(c for c in word if c.isalnum())
                if word and word not in stopwords and len(word) > 2:
                    word_counts[word] = word_counts.get(word, 0) + 1
                    
        # Find most common significant words
        if not word_counts:
            return None
            
        common_words = sorted(
            word_counts.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        
        # If we have recurring concepts, form an abstraction
        if common_words and common_words[0][1] >= 2:
            concept_words = [w for w, c in common_words if c >= 2]
            if concept_words:
                return {
                    "type": "concept_abstraction",
                    "concepts": concept_words,
                    "strength": common_words[0][1] / len(memories),
                    "based_on": [str(m.id) for m in memories],
                }
                
        return None

    def learn_pattern(self, pattern: dict[str, Any]) -> None:
        """
        Store a learned pattern for future recognition.
        
        Args:
            pattern: Pattern to learn
        """
        # Avoid duplicates
        for existing in self._learned_patterns:
            if (
                existing["type"] == pattern["type"] and
                existing.get("concepts") == pattern.get("concepts")
            ):
                # Strengthen existing pattern
                existing["strength"] = min(
                    1.0,
                    existing["strength"] + pattern["strength"] * 0.1,
                )
                return
                
        self._learned_patterns.append(pattern)
        logger.info("Learned new pattern", pattern_type=pattern["type"])

    def get_learned_patterns(self) -> list[dict[str, Any]]:
        """Get all learned patterns."""
        return self._learned_patterns.copy()

    async def match_pattern(
        self,
        embedding: np.ndarray,
        pattern_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Find learned patterns that match the current input.
        
        Args:
            embedding: Current input embedding
            pattern_type: Optional filter by pattern type
            
        Returns:
            List of matching patterns
        """
        matches = []
        
        for pattern in self._learned_patterns:
            if pattern_type and pattern["type"] != pattern_type:
                continue
                
            # Simple strength-based matching for now
            if pattern["strength"] > 0.5:
                matches.append(pattern)
                
        return matches
