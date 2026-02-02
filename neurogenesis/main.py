"""Main entry point for NeuroGenesis."""

import uvicorn

from neurogenesis.api.app import app
from neurogenesis.core.config import settings
from neurogenesis.utils.logging import setup_logging


def main() -> None:
    """Run the NeuroGenesis API server."""
    # Setup logging
    setup_logging(
        level=settings.log_level,
        format_type=settings.log_format,
    )
    
    # Run server
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
