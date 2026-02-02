"""Tests for embedding engine."""

import numpy as np
import pytest

from neurogenesis.memory.embeddings import EmbeddingEngine


@pytest.fixture
def embedding_engine():
    """Create embedding engine for testing."""
    return EmbeddingEngine(
        model_name="all-MiniLM-L6-v2",
        dimension=384,
    )


@pytest.mark.asyncio
async def test_single_embedding(embedding_engine: EmbeddingEngine):
    """Test generating a single embedding."""
    text = "Hello, world!"
    
    embedding = await embedding_engine.embed(text)
    
    assert embedding is not None
    assert embedding.shape == (384,)
    assert embedding.dtype == np.float32


@pytest.mark.asyncio
async def test_batch_embedding(embedding_engine: EmbeddingEngine):
    """Test generating batch embeddings."""
    texts = ["Hello", "World", "Test"]
    
    embeddings = await embedding_engine.embed_batch(texts)
    
    assert embeddings is not None
    assert embeddings.shape == (3, 384)


@pytest.mark.asyncio
async def test_embedding_similarity(embedding_engine: EmbeddingEngine):
    """Test that similar texts have similar embeddings."""
    text1 = "The cat sat on the mat"
    text2 = "A cat was sitting on a rug"
    text3 = "Python is a programming language"
    
    emb1 = await embedding_engine.embed(text1)
    emb2 = await embedding_engine.embed(text2)
    emb3 = await embedding_engine.embed(text3)
    
    sim_12 = embedding_engine.cosine_similarity(emb1, emb2)
    sim_13 = embedding_engine.cosine_similarity(emb1, emb3)
    
    # Similar texts should have higher similarity
    assert sim_12 > sim_13


@pytest.mark.asyncio
async def test_embedding_deterministic(embedding_engine: EmbeddingEngine):
    """Test that embeddings are deterministic."""
    text = "Deterministic test"
    
    emb1 = await embedding_engine.embed(text)
    emb2 = await embedding_engine.embed(text)
    
    # Same text should produce same embedding
    np.testing.assert_array_almost_equal(emb1, emb2)


def test_cosine_similarity(embedding_engine: EmbeddingEngine):
    """Test cosine similarity calculation."""
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([1.0, 0.0, 0.0])
    c = np.array([0.0, 1.0, 0.0])
    
    # Same vectors = similarity of 1
    assert embedding_engine.cosine_similarity(a, b) == pytest.approx(1.0)
    
    # Orthogonal vectors = similarity of 0
    assert embedding_engine.cosine_similarity(a, c) == pytest.approx(0.0)


def test_batch_cosine_similarity(embedding_engine: EmbeddingEngine):
    """Test batch cosine similarity."""
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.5, 0.5, 0.0],
    ], dtype=np.float32)
    
    similarities = embedding_engine.batch_cosine_similarity(query, embeddings)
    
    assert len(similarities) == 3
    assert similarities[0] == pytest.approx(1.0, abs=0.1)
    assert similarities[1] == pytest.approx(0.0, abs=0.1)
