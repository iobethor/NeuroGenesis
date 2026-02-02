"""Pytest fixtures for NeuroGenesis tests."""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from neurogenesis.core.config import Settings
from neurogenesis.core.mind import Mind


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_settings(temp_dir: Path) -> Settings:
    """Create test settings with temporary paths."""
    return Settings(
        memory_db_path=temp_dir / "test_memory.db",
        vector_store_path=temp_dir / "vectors",
        embedding_model="all-MiniLM-L6-v2",
        embedding_dimension=384,
        consolidation_threshold=10,
        decay_rate=0.01,
        growth_rate=0.1,
        debug=True,
    )


@pytest_asyncio.fixture
async def mind(test_settings: Settings) -> AsyncGenerator[Mind, None]:
    """Create and initialize a Mind instance for testing."""
    async with Mind(config=test_settings) as mind:
        yield mind
