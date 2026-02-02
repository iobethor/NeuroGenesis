"""Logging configuration for NeuroGenesis."""

import logging
import sys
from typing import Literal

import structlog


def setup_logging(
    level: str = "INFO",
    format_type: Literal["json", "text"] = "json",
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        format_type: Output format (json or text)
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Configure structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    
    if format_type == "json":
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
