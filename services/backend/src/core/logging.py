#!/usr/bin/env python3
"""
Logging configuration for Chonost
"""

import logging
import sys
from pathlib import Path

def setup_logging(name: str = "chonost") -> logging.Logger:
    """
    Sets up the logging configuration for the application.

    This function creates a logger that outputs to both the console (INFO level)
    and a file (`logs/chonost.log`, DEBUG level).

    Args:
        name (str, optional): The name of the logger. Defaults to "chonost".

    Returns:
        logging.Logger: The configured logger instance.
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / "chonost.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
