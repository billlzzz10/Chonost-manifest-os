#!/usr/bin/env python3
"""
File System Watcher for Project Manifest System - Phase 2

Monitors file system changes and triggers entity extraction for the project manifest.
Uses watchdog for file monitoring and dramatiq for async processing.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import dramatiq
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent
import redis

# Dramatiq broker setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)
dramatiq.set_broker(dramatiq.brokers.RedisBroker(client=redis_client))

class FileChangeHandler(FileSystemEventHandler):
    """
    Handles file system events and queues them for processing.

    Attributes:
        watcher (FileSystemWatcher): The parent watcher instance.
        watched_extensions (Set[str]): File extensions to monitor.
        exclude_patterns (List[str]): Patterns to exclude from monitoring.
    """

    def __init__(self, watcher: 'FileSystemWatcher'):
        """
        Initialize the file change handler.

        Args:
            watcher (FileSystemWatcher): The parent watcher instance.
        """
        self.watcher = watcher
        self.watched_extensions = {'.py', '.js', '.ts', '.tsx', '.md', '.txt', '.json', '.yaml', '.yml'}
        self.exclude_patterns = ['__pycache__', '.git', 'node_modules', '.venv', 'dist', 'build']

    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._queue_file_event(event.src_path, 'created')

    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._queue_file_event(event.src_path, 'modified')

    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._queue_file_event(event.src_path, 'deleted')

    def _should_process_file(self, file_path: str) -> bool:
        """
        Determine if a file should be processed.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if the file should be processed.
        """
        path = Path(file_path)

        # Check extension
        if path.suffix.lower() not in self.watched_extensions:
            return False

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in str(path):
                return False

        # Skip hidden files and system files
        if path.name.startswith('.'):
            return False

        return True

    def _queue_file_event(self, file_path: str, event_type: str):
        """
        Queue a file event for processing.

        Args:
            file_path (str): Path to the file.
            event_type (str): Type of event ('created', 'modified', 'deleted').
        """
        try:
            # Send to dramatiq queue
            process_file_change.send(file_path, event_type)
            logging.info(f"Queued {event_type} event for: {file_path}")

        except Exception as e:
            logging.error(f"Failed to queue file event {file_path}: {e}")

class FileSystemWatcher:
    """
    Main file system watcher for the Project Manifest System.

    Monitors project directories for changes and triggers entity extraction.
    Uses dramatiq for async processing to avoid blocking the watcher.

    Attributes:
        project_root (Path): Root directory of the project to monitor.
        observer (Observer): Watchdog observer instance.
        event_handler (FileChangeHandler): File event handler.
        running (bool): Whether the watcher is currently running.
        stats (Dict[str, Any]): Statistics about watcher operations.
    """

    def __init__(self, project_root: str):
        """
        Initialize the file system watcher.

        Args:
            project_root (str): Root directory path to monitor.
        """
        self.project_root = Path(project_root).resolve()
        self.observer = Observer()
        self.event_handler = FileChangeHandler(self)
        self.running = False

        # Setup logging
        self._setup_logging()

        # Initialize statistics
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'files_processed': 0,
            'events_queued': 0,
            'errors': 0
        }

        logging.info(f"Initialized FileSystemWatcher for: {self.project_root}")

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"fs_watcher_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

    def start(self):
        """Start the file system watcher."""
        try:
            logging.info("🚀 Starting File System Watcher...")

            # Schedule the observer
            self.observer.schedule(self.event_handler, str(self.project_root), recursive=True)

            # Start observing
            self.observer.start()
            self.running = True

            logging.info(f"✅ Watcher started successfully - monitoring: {self.project_root}")
            logging.info("📋 Watching extensions: .py, .js, .ts, .tsx, .md, .txt, .json, .yaml, .yml")

        except Exception as e:
            logging.error(f"❌ Failed to start watcher: {e}")
            raise

    def stop(self):
        """Stop the file system watcher."""
        try:
            logging.info("🛑 Stopping File System Watcher...")

            self.running = False
            self.observer.stop()
            self.observer.join(timeout=5)

            # Save final statistics
            self._save_stats()

            logging.info("✅ Watcher stopped successfully")

        except Exception as e:
            logging.error(f"❌ Error stopping watcher: {e}")

    def _save_stats(self):
        """Save watcher statistics to file."""
        try:
            stats_file = self.project_root / "logs" / "fs_watcher_stats.json"
            stats_data = {
                'stats': self.stats,
                'end_time': datetime.now().isoformat(),
                'project_root': str(self.project_root)
            }

            import json
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=2)

            logging.info(f"📊 Statistics saved to: {stats_file}")

        except Exception as e:
            logging.error(f"Failed to save statistics: {e}")

    def is_running(self) -> bool:
        """
        Check if the watcher is currently running.

        Returns:
            bool: True if running, False otherwise.
        """
        return self.running

# Dramatiq task for processing file changes
@dramatiq.actor(queue_name="file_changes")
def process_file_change(file_path: str, event_type: str):
    """
    Process a file change event asynchronously.

    This task is executed by dramatiq workers and handles the actual
    entity extraction and manifest updating.

    Args:
        file_path (str): Path to the changed file.
        event_type (str): Type of change ('created', 'modified', 'deleted').
    """
    try:
        logging.info(f"🔍 Processing {event_type} event for: {file_path}")

        # Import here to avoid circular imports
        from .entity_extraction import EntityExtractor
        from .vector_db import VectorDatabase

        # Initialize components
        extractor = EntityExtractor()
        vector_db = VectorDatabase()

        if event_type in ['created', 'modified']:
            # Extract entities from the file
            entities = extractor.extract_entities(file_path)

            if entities:
                logging.info(f"📝 Extracted {len(entities)} entities from {file_path}")

                # Store entities in vector database
                stored_count = vector_db.store_entities_batch(entities)
                logging.info(f"💾 Stored {stored_count} entities in vector database")

            else:
                logging.info(f"ℹ️ No entities found in {file_path}")

        elif event_type == 'deleted':
            # Handle file deletion - remove from manifest
            logging.info(f"🗑️ File deleted: {file_path}")
            # Remove entities from vector database
            success = vector_db.delete_by_file(file_path)
            if success:
                logging.info(f"🗑️ Removed entities from vector database for: {file_path}")
            else:
                logging.warning(f"⚠️ Failed to remove entities from vector database for: {file_path}")

        logging.info(f"✅ Successfully processed {event_type} event for: {file_path}")

    except Exception as e:
        logging.error(f"❌ Failed to process file change {file_path}: {e}")
        # TODO: Implement retry logic or dead letter queue

def main():
    """Main entry point for running the file system watcher."""
    # Default to current directory if no path provided
    project_root = os.getcwd()

    try:
        # Create and start watcher
        watcher = FileSystemWatcher(project_root)

        # Start the watcher
        watcher.start()

        # Keep running until interrupted
        try:
            while watcher.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal...")

        # Stop the watcher
        watcher.stop()

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())