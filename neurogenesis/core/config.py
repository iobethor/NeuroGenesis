"""Configuration management for NeuroGenesis."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")

    # Memory Settings
    memory_db_path: Path = Field(
        default=Path("./data/memory.db"),
        description="Path to SQLite database for memory storage",
    )
    vector_store_path: Path = Field(
        default=Path("./data/vectors"),
        description="Path to vector store directory",
    )

    # Embedding Settings
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for embeddings",
    )
    embedding_dimension: int = Field(
        default=384,
        description="Embedding vector dimension",
    )

    # Growth Settings
    consolidation_threshold: int = Field(
        default=100,
        description="Number of memories before consolidation",
    )
    decay_rate: float = Field(
        default=0.01,
        description="Memory decay rate per cycle",
    )
    growth_rate: float = Field(
        default=0.1,
        description="Learning growth rate",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.memory_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
