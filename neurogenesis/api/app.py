"""FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from neurogenesis.api.routes import router
from neurogenesis.core.config import settings
from neurogenesis.core.mind import Mind

# Global mind instance
_mind: Mind | None = None


def get_mind() -> Mind:
    """Get the global mind instance."""
    if _mind is None:
        raise RuntimeError("Mind not initialized")
    return _mind


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    global _mind
    
    # Startup
    _mind = Mind(config=settings)
    await _mind.initialize()
    
    yield
    
    # Shutdown
    if _mind:
        await _mind.close()
        _mind = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="NeuroGenesis API",
        description="Growing Mind with Active Semantic Memory",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router, prefix="/api/v1")
    
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy", "version": "0.1.0"}
    
    return app


# Create default app instance
app = create_app()
