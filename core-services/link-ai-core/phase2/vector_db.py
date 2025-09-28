#!/usr/bin/env python3
"""
Vector Database Integration for Project Manifest System - Phase 2

Manages vector storage and retrieval for entities extracted from the project.
Uses Qdrant for vector database operations and sentence transformers for embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

from .entity_extraction import Entity

class VectorDatabase:
    """
    Vector database manager for storing and retrieving entity embeddings.

    Uses Qdrant as the vector database and sentence transformers for
    generating embeddings from entity data.

    Attributes:
        client (QdrantClient): Qdrant client instance.
        encoder (SentenceTransformer): Sentence transformer model.
        collection_name (str): Name of the Qdrant collection.
    """

    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "project_manifest"):
        """
        Initialize the vector database.

        Args:
            host (str): Qdrant server host.
            port (int): Qdrant server port.
            collection_name (str): Name of the collection to use.
        """
        self.collection_name = collection_name

        # Initialize Qdrant client
        try:
            self.client = QdrantClient(host=host, port=port)
            logging.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            logging.error(f"Failed to connect to Qdrant: {e}")
            raise

        # Initialize sentence transformer
        try:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            logging.info("Loaded sentence transformer model")
        except Exception as e:
            logging.error(f"Failed to load sentence transformer: {e}")
            raise

        # Create collection if it doesn't exist
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,  # Dimension for all-MiniLM-L6-v2
                        distance=models.Distance.COSINE
                    )
                )
                logging.info(f"Created collection: {self.collection_name}")
            else:
                logging.info(f"Collection already exists: {self.collection_name}")

        except Exception as e:
            logging.error(f"Failed to ensure collection exists: {e}")
            raise

    def store_entity(self, entity: Entity) -> bool:
        """
        Store an entity in the vector database.

        Args:
            entity (Entity): The entity to store.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Generate embedding for the entity
            embedding = self._generate_entity_embedding(entity)

            # Prepare payload
            payload = {
                'name': entity.name,
                'type': entity.type,
                'confidence': entity.confidence,
                'context': entity.context,
                'file_path': entity.file_path,
                'line_number': entity.line_number,
                'metadata': entity.metadata,
                'timestamp': entity.metadata.get('timestamp', None)
            }

            # Generate unique ID from entity properties
            entity_id = hash(f"{entity.file_path}:{entity.line_number}:{entity.name}")

            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=abs(entity_id),  # Ensure positive ID
                        vector=embedding.tolist(),
                        payload=payload
                    )
                ]
            )

            logging.info(f"Stored entity: {entity.name} ({entity.type})")
            return True

        except Exception as e:
            logging.error(f"Failed to store entity {entity.name}: {e}")
            return False

    def store_entities_batch(self, entities: List[Entity]) -> int:
        """
        Store multiple entities in batch.

        Args:
            entities (List[Entity]): List of entities to store.

        Returns:
            int: Number of successfully stored entities.
        """
        successful = 0

        try:
            points = []

            for entity in entities:
                try:
                    # Generate embedding
                    embedding = self._generate_entity_embedding(entity)

                    # Prepare payload
                    payload = {
                        'name': entity.name,
                        'type': entity.type,
                        'confidence': entity.confidence,
                        'context': entity.context,
                        'file_path': entity.file_path,
                        'line_number': entity.line_number,
                        'metadata': entity.metadata,
                        'timestamp': entity.metadata.get('timestamp', None)
                    }

                    # Generate unique ID
                    entity_id = hash(f"{entity.file_path}:{entity.line_number}:{entity.name}")

                    points.append(
                        models.PointStruct(
                            id=abs(entity_id),
                            vector=embedding.tolist(),
                            payload=payload
                        )
                    )

                except Exception as e:
                    logging.error(f"Failed to prepare entity {entity.name}: {e}")
                    continue

            if points:
                # Batch upsert
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                successful = len(points)
                logging.info(f"Batch stored {successful} entities")

        except Exception as e:
            logging.error(f"Failed to batch store entities: {e}")

        return successful

    def search_similar(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Search for entities similar to the query.

        Args:
            query (str): Search query.
            limit (int): Maximum number of results.
            score_threshold (float): Minimum similarity score.

        Returns:
            List[Dict[str, Any]]: List of similar entities with scores.
        """
        try:
            # Generate embedding for query
            query_embedding = self.encoder.encode(query).tolist()

            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )

            # Format results
            results = []
            for hit in search_result:
                result = {
                    'entity': {
                        'name': hit.payload['name'],
                        'type': hit.payload['type'],
                        'confidence': hit.payload['confidence'],
                        'context': hit.payload['context'],
                        'file_path': hit.payload['file_path'],
                        'line_number': hit.payload['line_number'],
                        'metadata': hit.payload['metadata']
                    },
                    'score': hit.score,
                    'id': hit.id
                }
                results.append(result)

            logging.info(f"Found {len(results)} similar entities for query: {query}")
            return results

        except Exception as e:
            logging.error(f"Failed to search similar entities: {e}")
            return []

    def search_by_type(self, entity_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search entities by type.

        Args:
            entity_type (str): Type of entities to search for.
            limit (int): Maximum number of results.

        Returns:
            List[Dict[str, Any]]: List of entities of the specified type.
        """
        try:
            # Search with filter
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="type",
                            match=models.MatchValue(value=entity_type)
                        )
                    ]
                ),
                limit=limit
            )

            # Format results
            results = []
            for hit in search_result[0]:  # scroll returns (points, next_page_offset)
                result = {
                    'entity': {
                        'name': hit.payload['name'],
                        'type': hit.payload['type'],
                        'confidence': hit.payload['confidence'],
                        'context': hit.payload['context'],
                        'file_path': hit.payload['file_path'],
                        'line_number': hit.payload['line_number'],
                        'metadata': hit.payload['metadata']
                    },
                    'id': hit.id
                }
                results.append(result)

            logging.info(f"Found {len(results)} entities of type: {entity_type}")
            return results

        except Exception as e:
            logging.error(f"Failed to search by type {entity_type}: {e}")
            return []

    def search_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Search all entities from a specific file.

        Args:
            file_path (str): Path to the file.

        Returns:
            List[Dict[str, Any]]: List of entities from the file.
        """
        try:
            # Search with filter
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="file_path",
                            match=models.MatchValue(value=file_path)
                        )
                    ]
                ),
                limit=1000  # Large limit for file contents
            )

            # Format results
            results = []
            for hit in search_result[0]:
                result = {
                    'entity': {
                        'name': hit.payload['name'],
                        'type': hit.payload['type'],
                        'confidence': hit.payload['confidence'],
                        'context': hit.payload['context'],
                        'file_path': hit.payload['file_path'],
                        'line_number': hit.payload['line_number'],
                        'metadata': hit.payload['metadata']
                    },
                    'id': hit.id
                }
                results.append(result)

            logging.info(f"Found {len(results)} entities in file: {file_path}")
            return results

        except Exception as e:
            logging.error(f"Failed to search by file {file_path}: {e}")
            return []

    def delete_by_file(self, file_path: str) -> bool:
        """
        Delete all entities from a specific file.

        Args:
            file_path (str): Path to the file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Delete with filter
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="file_path",
                                match=models.MatchValue(value=file_path)
                            )
                        ]
                    )
                )
            )

            logging.info(f"Deleted entities from file: {file_path}")
            return True

        except Exception as e:
            logging.error(f"Failed to delete entities from file {file_path}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dict[str, Any]: Database statistics.
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                'collection_name': self.collection_name,
                'vectors_count': collection_info.vectors_count,
                'points_count': collection_info.points_count,
                'status': 'active'
            }
        except Exception as e:
            logging.error(f"Failed to get stats: {e}")
            return {'error': str(e)}

    def _generate_entity_embedding(self, entity: Entity) -> np.ndarray:
        """
        Generate embedding for an entity.

        Args:
            entity (Entity): The entity to embed.

        Returns:
            np.ndarray: The embedding vector.
        """
        # Combine entity information for embedding
        text_parts = [
            entity.name,
            entity.type,
            entity.context,
            str(entity.metadata)
        ]

        # Filter out None values and join
        text = ' '.join(filter(None, text_parts))

        # Generate embedding
        embedding = self.encoder.encode(text)

        return embedding

    def clear_collection(self) -> bool:
        """
        Clear all data from the collection.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Delete all points
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[]
                    )
                )
            )

            logging.info(f"Cleared collection: {self.collection_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to clear collection: {e}")
            return False

def main():
    """Test the vector database functionality."""
    try:
        # Initialize database
        db = VectorDatabase()

        # Get stats
        stats = db.get_stats()
        print(f"Database stats: {stats}")

        # Test search (should be empty initially)
        results = db.search_similar("test query")
        print(f"Search results: {len(results)}")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    main()