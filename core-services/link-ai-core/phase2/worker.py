#!/usr/bin/env python3
"""
Dramatiq Worker for Project Manifest System - Phase 2

Runs dramatiq workers to process file change events asynchronously.
Handles entity extraction and vector database operations.
"""

import os
import logging
from pathlib import Path

def setup_logging():
    """Setup logging configuration for the worker."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"worker_{Path(__file__).stem}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point for running the dramatiq worker."""
    setup_logging()

    logging.info("🚀 Starting Dramatiq Worker for Project Manifest System")

    try:
        # Import dramatiq modules to register actors
        from .file_system_watcher import process_file_change

        # Start dramatiq worker
        import dramatiq
        from dramatiq.cli import main as dramatiq_main
        import sys

        # Set up command line arguments for dramatiq
        sys.argv = [
            'dramatiq',
            'core_services.link_ai_core.phase2.file_system_watcher',
            '--processes', '2',  # Number of worker processes
            '--threads', '4',    # Number of threads per process
            '--queues', 'file_changes',  # Queue to consume from
            '--verbose'
        ]

        logging.info("📋 Worker configuration:")
        logging.info("  - Processes: 2")
        logging.info("  - Threads per process: 4")
        logging.info("  - Queues: file_changes")
        logging.info("  - Log level: INFO")

        # Run dramatiq worker
        dramatiq_main()

    except KeyboardInterrupt:
        logging.info("🛑 Worker stopped by user")
    except Exception as e:
        logging.error(f"❌ Worker failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())