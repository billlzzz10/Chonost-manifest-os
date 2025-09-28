#!/usr/bin/env python3
"""
Test script for Entity Extraction pipeline - Phase 2

Tests the entity extraction functionality with sample files.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase2.entity_extraction import EntityExtractor

def test_entity_extraction():
    """Test entity extraction with sample content."""

    # Create a test file with sample content
    test_content = """
    # Project Manifest System

    This is a comprehensive system for managing project manifests using AI-powered entity extraction.

    ## Features

    - File system monitoring with watchdog
    - Entity extraction using spaCy and transformers
    - Vector database integration with Qdrant
    - Async processing with Dramatiq and Redis

    ## Classes

    The system includes several key classes:
    - FileSystemWatcher: Monitors file changes
    - EntityExtractor: Extracts entities from text
    - VectorDatabase: Manages vector embeddings

    ## Functions

    Key functions include:
    - extract_entities(): Extracts named entities
    - store_entities_batch(): Stores entities in vector DB
    - process_file_change(): Processes file system events

    ## Configuration

    The system uses environment variables for configuration:
    - REDIS_URL: Redis connection URL
    - QDRANT_URL: Qdrant vector database URL
    - WATCH_PATH: Path to monitor for changes
    """

    # Create test file
    test_file = Path("test_sample.md")
    test_file.write_text(test_content)

    try:
        # Initialize extractor
        extractor = EntityExtractor()

        # Extract entities
        entities = extractor.extract_entities(str(test_file))

        print("Entity Extraction Test Results:")
        print(f"File: {test_file}")
        print(f"Entities found: {len(entities)}")

        if entities:
            print("\nExtracted Entities:")
            for i, entity in enumerate(entities[:10], 1):  # Show first 10
                # Handle spaCy Entity objects
                if hasattr(entity, 'text'):
                    text = entity.text
                    label = getattr(entity, 'label_', str(entity))
                    print(f"  {i}. {text} ({label})")
                else:
                    # Handle other formats
                    print(f"  {i}. {str(entity)}")
            if len(entities) > 10:
                print(f"  ... and {len(entities) - 10} more")
        else:
            print("No entities found")

        print("\nEntity extraction test completed successfully!")

    except Exception as e:
        print(f"Entity extraction test failed: {e}")
        return False

    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()

    return True

if __name__ == "__main__":
    success = test_entity_extraction()
    sys.exit(0 if success else 1)