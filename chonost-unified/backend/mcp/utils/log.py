"""
Logging configuration สำหรับ MCP Orchestrator
รองรับ structlog และ standard logging
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", use_structlog: bool = True) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_structlog: Whether to use structlog for structured logging

    Returns:
        Configured logger instance
    """
    # Convert string level to logging level
    log_level = getattr(logging, level.upper(), logging.INFO)

    if use_structlog:
        try:
            import structlog

            # Configure structlog
            structlog.configure(
                processors=[
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer(),
                ],
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

            # Get structlog logger
            logger = structlog.get_logger()
            logger.setLevel(log_level)

            # Also configure standard logging
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                stream=sys.stdout,
            )

            return logger

        except ImportError:
            # Fallback to standard logging if structlog not available
            logging.basicConfig(
                level=log_level,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                stream=sys.stdout,
            )
            return logging.getLogger("orchestrator")
    else:
        # Use standard logging
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        return logging.getLogger("orchestrator")


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (optional)

    Returns:
        Logger instance
    """
    try:
        import structlog

        if name:
            return structlog.get_logger(name)
        else:
            return structlog.get_logger()
    except ImportError:
        if name:
            return logging.getLogger(name)
        else:
            return logging.getLogger("orchestrator")


# Default logger
logger = get_logger("orchestrator")
