"""
The All-Seeing Eye - File Watcher & Indexing System
ตาม DEVELOPMENT_ROADMAP.md Phase 2.1
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent, FileDeletedEvent
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

import dramatiq
from dramatiq.brokers.redis import RedisBroker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis broker for background tasks
redis_broker = RedisBroker(host="localhost", port=6379)
dramatiq.set_broker(redis_broker)

# Initialize Qdrant client
qdrant_client = QdrantClient("localhost", port=6333)

# Initialize sentence transformer for embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Using a more compatible model

class FileIndex:
    """File indexing and metadata management"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.index_file = self.project_root / ".chonost" / "file_index.json"
        self.index_file.parent.mkdir(exist_ok=True)
        self.file_metadata: Dict[str, Dict] = self._load_index()
        
    def _load_index(self) -> Dict[str, Dict]:
        """Load existing file index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading file index: {e}")
        return {}
    
    def _save_index(self):
        """Save file index to disk"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving file index: {e}")
    
    def add_file(self, file_path: str, metadata: Dict):
        """Add or update file metadata"""
        relative_path = str(Path(file_path).relative_to(self.project_root))
        self.file_metadata[relative_path] = {
            **metadata,
            'last_modified': datetime.now().isoformat(),
            'indexed_at': datetime.now().isoformat()
        }
        self._save_index()
        logger.info(f"Indexed file: {relative_path}")
    
    def remove_file(self, file_path: str):
        """Remove file from index"""
        relative_path = str(Path(file_path).relative_to(self.project_root))
        if relative_path in self.file_metadata:
            del self.file_metadata[relative_path]
            self._save_index()
            logger.info(f"Removed file from index: {relative_path}")
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict]:
        """Get file metadata"""
        relative_path = str(Path(file_path).relative_to(self.project_root))
        return self.file_metadata.get(relative_path)

class EntityExtractor:
    """Entity extraction using NER model"""
    
    def __init__(self):
        from transformers import pipeline
        self.ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text"""
        try:
            entities = self.ner_pipeline(text)
            return [
                {
                    'text': entity['word'],
                    'type': entity['entity_group'],
                    'score': entity['score'],
                    'start': entity['start'],
                    'end': entity['end']
                }
                for entity in entities
            ]
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []

@dramatiq.actor
def process_file_async(file_path: str, project_root: str):
    """Background task for file processing"""
    try:
        # Initialize components
        file_index = FileIndex(project_root)
        entity_extractor = EntityExtractor()
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract entities
        entities = entity_extractor.extract_entities(content)
        
        # Generate embeddings
        embedding = embedding_model.encode(content).tolist()
        
        # Store in Qdrant
        collection_name = "chonost_files"
        try:
            qdrant_client.get_collection(collection_name)
        except:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
        
        # Add to vector database
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=hash(file_path),
                    vector=embedding,
                    payload={
                        'file_path': str(Path(file_path).relative_to(project_root)),
                        'content': content[:1000],  # First 1000 chars
                        'entities': entities,
                        'file_size': len(content),
                        'last_modified': datetime.now().isoformat()
                    }
                )
            ]
        )
        
        # Update file index
        metadata = {
            'file_size': len(content),
            'entities': entities,
            'embedding_generated': True
        }
        file_index.add_file(file_path, metadata)
        
        logger.info(f"Successfully processed file: {file_path}")
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

class ChonostFileHandler(FileSystemEventHandler):
    """File system event handler for The All-Seeing Eye"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.file_index = FileIndex(project_root)
        self.ignored_patterns = {
            '.git', '__pycache__', 'node_modules', '.venv', 
            '.pytest_cache', '.mypy_cache', '*.pyc', '*.pyo',
            '.DS_Store', 'Thumbs.db'
        }
    
    def _should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored"""
        path = Path(file_path)
        for pattern in self.ignored_patterns:
            if pattern in path.parts or path.match(pattern):
                return True
        return False
    
    def on_created(self, event):
        """Handle file creation"""
        if not event.is_directory and not self._should_ignore(event.src_path):
            logger.info(f"File created: {event.src_path}")
            # Schedule background processing
            process_file_async.send(event.src_path, self.project_root)
    
    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory and not self._should_ignore(event.src_path):
            logger.info(f"File modified: {event.src_path}")
            # Schedule background processing
            process_file_async.send(event.src_path, self.project_root)
    
    def on_deleted(self, event):
        """Handle file deletion"""
        if not event.is_directory and not self._should_ignore(event.src_path):
            logger.info(f"File deleted: {event.src_path}")
            # Remove from index
            self.file_index.remove_file(event.src_path)

class AllSeeingEye:
    """The All-Seeing Eye - Main file watcher and indexing system"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.observer = Observer()
        self.file_handler = ChonostFileHandler(str(self.project_root))
        self.file_index = FileIndex(str(self.project_root))
        
    def start(self):
        """Start file watching"""
        logger.info(f"Starting The All-Seeing Eye for: {self.project_root}")
        
        # Schedule the observer
        self.observer.schedule(
            self.file_handler,
            str(self.project_root),
            recursive=True
        )
        
        # Start the observer
        self.observer.start()
        logger.info("The All-Seeing Eye is now watching for file changes")
    
    def stop(self):
        """Stop file watching"""
        self.observer.stop()
        self.observer.join()
        logger.info("The All-Seeing Eye stopped")
    
    def index_existing_files(self):
        """Index all existing files in the project"""
        logger.info("Indexing existing files...")
        
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and not self.file_handler._should_ignore(str(file_path)):
                logger.info(f"Indexing existing file: {file_path}")
                process_file_async.send(str(file_path), str(self.project_root))
        
        logger.info("Finished indexing existing files")
    
    def search_files(self, query: str, limit: int = 10) -> List[Dict]:
        """Search files using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = embedding_model.encode(query).tolist()
            
            # Search in Qdrant
            results = qdrant_client.search(
                collection_name="chonost_files",
                query_vector=query_embedding,
                limit=limit
            )
            
            return [
                {
                    'file_path': result.payload['file_path'],
                    'score': result.score,
                    'content_preview': result.payload['content'],
                    'entities': result.payload.get('entities', [])
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    project_root = "F:/repos/chonost-manuscript-os"
    all_seeing_eye = AllSeeingEye(project_root)
    
    try:
        # Index existing files first
        all_seeing_eye.index_existing_files()
        
        # Start watching for changes
        all_seeing_eye.start()
        
        # Keep running
        while True:
            asyncio.sleep(1)
            
    except KeyboardInterrupt:
        all_seeing_eye.stop()
        logger.info("The All-Seeing Eye stopped by user")
