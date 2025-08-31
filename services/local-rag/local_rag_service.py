"""
Local RAG Service for Chonost Desktop App
ใช้ SQLite และ file-based storage แทน Redis/Qdrant
"""

import os
import json
import sqlite3
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging

from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalRAGService:
    """Local RAG Service using SQLite and file-based storage"""
    
    def __init__(self, data_dir: str = "./data/local_rag"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite database
        self.db_path = self.data_dir / "rag_database.db"
        self.init_database()
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
        
        # File paths
        self.embeddings_file = self.data_dir / "embeddings.pkl"
        self.documents_file = self.data_dir / "documents.json"
        
        # Load existing data
        self.embeddings = self.load_embeddings()
        self.documents = self.load_documents()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                content TEXT,
                title TEXT,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create chunks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                content TEXT,
                embedding_id INTEGER,
                chunk_index INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Create embeddings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id INTEGER,
                embedding_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chunk_id) REFERENCES chunks (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def load_embeddings(self) -> Dict[int, np.ndarray]:
        """Load embeddings from pickle file"""
        if self.embeddings_file.exists():
            try:
                with open(self.embeddings_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading embeddings: {e}")
        return {}
        
    def save_embeddings(self):
        """Save embeddings to pickle file"""
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
            
    def load_documents(self) -> Dict[str, Dict]:
        """Load documents from JSON file"""
        if self.documents_file.exists():
            try:
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading documents: {e}")
        return {}
        
    def save_documents(self):
        """Save documents to JSON file"""
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
    
    def add_document(self, file_path: str, content: str, title: str = None, doc_type: str = "text"):
        """Add a document to the RAG system"""
        try:
            # Store document in SQLite
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO documents (file_path, content, title, type, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (file_path, content, title or Path(file_path).name, doc_type, datetime.now()))
            
            document_id = cursor.lastrowid
            
            # Split content into chunks
            chunks = self.split_content(content)
            
            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Store chunk
                cursor.execute('''
                    INSERT INTO chunks (document_id, content, chunk_index)
                    VALUES (?, ?, ?)
                ''', (document_id, chunk, i))
                
                chunk_id = cursor.lastrowid
                
                # Generate embedding
                embedding = self.embedding_model.encode(chunk)
                self.embeddings[chunk_id] = embedding
                
                # Store embedding
                cursor.execute('''
                    INSERT INTO embeddings (chunk_id, embedding_data)
                    VALUES (?, ?)
                ''', (chunk_id, embedding.tobytes()))
            
            conn.commit()
            conn.close()
            
            # Update documents cache
            self.documents[file_path] = {
                'id': document_id,
                'title': title or Path(file_path).name,
                'type': doc_type,
                'chunks': len(chunks),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to files
            self.save_embeddings()
            self.save_documents()
            
            logger.info(f"Added document: {file_path} with {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
            return False
    
    def split_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split content into overlapping chunks"""
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(content):
                # Look for sentence endings
                for i in range(end, max(start, end - 100), -1):
                    if content[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            if start >= len(content):
                break
        
        return chunks
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant documents"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Calculate similarities
            similarities = []
            for chunk_id, embedding in self.embeddings.items():
                similarity = np.dot(query_embedding, embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                )
                similarities.append((chunk_id, similarity))
            
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get top results
            results = []
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for chunk_id, similarity in similarities[:limit]:
                cursor.execute('''
                    SELECT c.content, d.file_path, d.title, c.chunk_index
                    FROM chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE c.id = ?
                ''', (chunk_id,))
                
                row = cursor.fetchone()
                if row:
                    content, file_path, title, chunk_index = row
                    results.append({
                        'file_path': file_path,
                        'title': title,
                        'content': content,
                        'chunk_index': chunk_index,
                        'similarity': float(similarity)
                    })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def get_document_info(self) -> Dict:
        """Get information about stored documents"""
        return {
            'total_documents': len(self.documents),
            'total_chunks': len(self.embeddings),
            'documents': self.documents
        }
    
    def delete_document(self, file_path: str) -> bool:
        """Delete a document from the RAG system"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get document ID
            cursor.execute('SELECT id FROM documents WHERE file_path = ?', (file_path,))
            row = cursor.fetchone()
            if not row:
                return False
            
            document_id = row[0]
            
            # Get chunk IDs
            cursor.execute('SELECT id FROM chunks WHERE document_id = ?', (document_id,))
            chunk_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete embeddings
            for chunk_id in chunk_ids:
                if chunk_id in self.embeddings:
                    del self.embeddings[chunk_id]
            
            # Delete from database
            cursor.execute('DELETE FROM embeddings WHERE chunk_id IN ({})'.format(
                ','.join('?' * len(chunk_ids))), chunk_ids)
            cursor.execute('DELETE FROM chunks WHERE document_id = ?', (document_id,))
            cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
            
            conn.commit()
            conn.close()
            
            # Update cache
            if file_path in self.documents:
                del self.documents[file_path]
            
            # Save to files
            self.save_embeddings()
            self.save_documents()
            
            logger.info(f"Deleted document: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {file_path}: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Initialize RAG service
    rag_service = LocalRAGService()
    
    # Add a test document
    test_content = """
    Chonost is an intelligent writing platform that combines AI with creative tools.
    It features The All-Seeing Eye for file indexing, The Forge for code execution,
    and The Trinity Layout for seamless user experience.
    """
    
    rag_service.add_document("test_doc.md", test_content, "Test Document")
    
    # Search
    results = rag_service.search("AI writing platform")
    print("Search results:", results)
    
    # Get info
    info = rag_service.get_document_info()
    print("Document info:", info)
