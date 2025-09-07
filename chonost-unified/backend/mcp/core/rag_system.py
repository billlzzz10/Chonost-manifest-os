"""
🎯 RAG System - Retrieval-Augmented Generation
ระบบ RAG ที่ครบครันสำหรับ Synapse Backend Monolith

Features:
- Vector Database Integration (ChromaDB, Pinecone, Weaviate)
- Multiple Embedding Models (OpenAI, Ollama, Local)
- Document Processing & Chunking
- Semantic Search & Retrieval
- Context-Aware Generation
- Caching & Performance Optimization
"""

import asyncio
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
import sqlite3
import redis
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

# Vector Database Imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# AI/ML Imports
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaEmbeddingClient:
    """Client สำหรับจัดการ Ollama Embedding API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    async def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อกับ Ollama server"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ ไม่สามารถเชื่อมต่อกับ Ollama server: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """ดึงรายการโมเดล embedding ที่ใช้งานได้"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                # กรองเฉพาะโมเดล embedding
                embedding_models = [
                    model['name'] for model in models 
                    if 'embed' in model['name'].lower() or 
                       model['name'] in ['nomic-embed-text', 'all-minilm']
                ]
                return embedding_models
            else:
                return []
        except Exception as e:
            logger.error(f"❌ ไม่สามารถดึงรายการโมเดลได้: {e}")
            return []
    
    async def get_embedding(self, text: str, model_name: str) -> Optional[List[float]]:
        """สร้าง embedding สำหรับข้อความ"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": model_name,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('embedding', [])
            else:
                logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้าง embedding: {e}")
            return None
    
    async def get_embeddings_batch(self, texts: List[str], model_name: str) -> List[Optional[List[float]]]:
        """สร้าง embedding สำหรับข้อความหลายๆ ตัวพร้อมกัน"""
        try:
            # สร้าง embeddings แบบ batch
            embeddings = []
            for text in texts:
                embedding = await self.get_embedding(text, model_name)
                embeddings.append(embedding)
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้าง batch embeddings: {e}")
            return [None] * len(texts)
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """ดึงข้อมูลโมเดล"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ ไม่สามารถดึงข้อมูลโมเดลได้: {e}")
            return None

@dataclass
class Document:
    """เอกสารสำหรับ RAG System"""
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    chunk_index: int = 0
    embedding: Optional[List[float]] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class SearchResult:
    """ผลลัพธ์การค้นหา"""
    document: Document
    score: float
    relevance: str  # 'high', 'medium', 'low'

@dataclass
class RAGResponse:
    """การตอบกลับจาก RAG System"""
    answer: str
    sources: List[Document]
    confidence: float
    context_used: str
    processing_time: float

class EmbeddingProvider:
    """Provider สำหรับ Embedding Models"""
    
    def __init__(self, provider_type: str = "ollama", model_name: str = "nomic-embed-text"):
        self.provider_type = provider_type
        self.model_name = model_name
        self.model = None
        self.ollama_client = None
        self.setup_model()
    
    def setup_model(self):
        """ตั้งค่า embedding model"""
        try:
            if self.provider_type == "ollama":
                # ใช้ Ollama local embedding
                self.model = "ollama"
                self.ollama_client = OllamaEmbeddingClient()
                logger.info(f"✅ ใช้ Ollama embedding model: {self.model_name}")
                
            elif self.provider_type == "sentence_transformers":
                if SENTENCE_TRANSFORMERS_AVAILABLE:
                    self.model = SentenceTransformer(self.model_name)
                    logger.info(f"✅ ใช้ Sentence Transformers: {self.model_name}")
                else:
                    logger.warning("⚠️ Sentence Transformers ไม่พร้อมใช้งาน")
                    
            elif self.provider_type == "openai":
                # ใช้ OpenAI embedding
                self.model = "openai"
                logger.info(f"✅ ใช้ OpenAI embedding model: {self.model_name}")
                
            else:
                logger.warning(f"⚠️ ไม่รองรับ provider: {self.provider_type}")
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการตั้งค่า embedding model: {e}")
            self.model = None
    
    async def get_available_models(self) -> List[str]:
        """ดึงรายการโมเดล embedding ที่ใช้งานได้"""
        try:
            if self.provider_type == "ollama":
                return await self.ollama_client.get_available_models()
            else:
                return [self.model_name]
        except Exception as e:
            logger.error(f"❌ ไม่สามารถดึงรายการโมเดลได้: {e}")
            return []
    
    async def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อกับ embedding service"""
        try:
            if self.provider_type == "ollama":
                return await self.ollama_client.test_connection()
            else:
                return True
        except Exception as e:
            logger.error(f"❌ การทดสอบการเชื่อมต่อล้มเหลว: {e}")
            return False
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """สร้าง embedding สำหรับข้อความ"""
        if not self.model:
            return None
            
        try:
            if self.provider_type == "ollama":
                return await self._get_ollama_embedding(text)
            elif self.provider_type == "sentence_transformers":
                return await self._get_sentence_transformers_embedding(text)
            elif self.provider_type == "openai":
                return await self._get_openai_embedding(text)
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้าง embedding: {e}")
            return None
    
    async def _get_ollama_embedding(self, text: str) -> Optional[List[float]]:
        """สร้าง embedding ด้วย Ollama"""
        try:
            if self.ollama_client:
                return await self.ollama_client.get_embedding(text, self.model_name)
            else:
                # Fallback to direct API call
                response = requests.post(
                    "http://localhost:11434/api/embeddings",
                    json={"model": self.model_name, "prompt": text},
                    timeout=10
                )
                
                if response.status_code == 200:
                    return response.json().get('embedding', [])
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Ollama embedding error: {e}")
            return None
    
    async def _get_sentence_transformers_embedding(self, text: str) -> Optional[List[float]]:
        """สร้าง embedding ด้วย Sentence Transformers"""
        try:
            # ใช้ ThreadPoolExecutor เพื่อไม่ให้ block event loop
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                embedding = await loop.run_in_executor(
                    executor, 
                    lambda: self.model.encode(text).tolist()
                )
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Sentence Transformers embedding error: {e}")
            return None
    
    async def _get_openai_embedding(self, text: str) -> Optional[List[float]]:
        """สร้าง embedding ด้วย OpenAI"""
        try:
            # ต้องมี OPENAI_API_KEY ใน environment
            import os
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.embeddings.create(
                model=self.model_name,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ OpenAI embedding error: {e}")
            return None

class VectorDatabase:
    """Vector Database Manager"""
    
    def __init__(self, db_type: str = "chromadb", config: Dict[str, Any] = None):
        self.db_type = db_type
        self.config = config or {}
        self.client = None
        self.collection = None
        self.setup_database()
    
    def setup_database(self):
        """ตั้งค่า vector database"""
        try:
            if self.db_type == "chromadb":
                self._setup_chromadb()
            elif self.db_type == "pinecone":
                self._setup_pinecone()
            elif self.db_type == "sqlite":
                self._setup_sqlite_vector()
            else:
                logger.warning(f"⚠️ ไม่รองรับ vector database: {self.db_type}")
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการตั้งค่า vector database: {e}")
    
    def _setup_chromadb(self):
        """ตั้งค่า ChromaDB"""
        if not CHROMADB_AVAILABLE:
            logger.warning("⚠️ ChromaDB ไม่พร้อมใช้งาน")
            return
            
        try:
            self.client = chromadb.PersistentClient(
                path=self.config.get("path", "./chroma_db"),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            collection_name = self.config.get("collection_name", "synapse_documents")
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Synapse RAG Documents"}
            )
            
            logger.info("✅ ChromaDB พร้อมใช้งาน")
            
        except Exception as e:
            logger.error(f"❌ ChromaDB setup error: {e}")
    
    def _setup_pinecone(self):
        """ตั้งค่า Pinecone"""
        if not PINECONE_AVAILABLE:
            logger.warning("⚠️ Pinecone ไม่พร้อมใช้งาน")
            return
            
        try:
            api_key = self.config.get("api_key")
            environment = self.config.get("environment")
            
            if not api_key or not environment:
                logger.warning("⚠️ ต้องการ Pinecone API key และ environment")
                return
            
            pinecone.init(api_key=api_key, environment=environment)
            index_name = self.config.get("index_name", "synapse-rag")
            
            # สร้าง index ถ้ายังไม่มี
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=self.config.get("dimension", 1536),
                    metric="cosine"
                )
            
            self.collection = pinecone.Index(index_name)
            logger.info("✅ Pinecone พร้อมใช้งาน")
            
        except Exception as e:
            logger.error(f"❌ Pinecone setup error: {e}")
    
    def _setup_sqlite_vector(self):
        """ตั้งค่า SQLite สำหรับ vector storage"""
        try:
            db_path = self.config.get("db_path", "./synapse_vectors.db")
            self.client = sqlite3.connect(db_path)
            
            # สร้างตารางสำหรับเก็บ vectors
            self.client.execute("""
                CREATE TABLE IF NOT EXISTS document_vectors (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    metadata TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # สร้าง index สำหรับการค้นหา
            self.client.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_source 
                ON document_vectors(source)
            """)
            
            self.client.commit()
            logger.info("✅ SQLite Vector Database พร้อมใช้งาน")
            
        except Exception as e:
            logger.error(f"❌ SQLite vector setup error: {e}")
    
    async def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อกับ vector database"""
        try:
            if self.db_type == "chromadb":
                return self.client is not None and self.collection is not None
            elif self.db_type == "pinecone":
                return self.collection is not None
            elif self.db_type == "sqlite":
                return self.client is not None
            else:
                return False
        except Exception as e:
            logger.error(f"❌ การทดสอบการเชื่อมต่อ vector database ล้มเหลว: {e}")
            return False
    
    async def add_documents(self, documents: List[Document]) -> bool:
        """เพิ่มเอกสารลงใน vector database"""
        if not self.collection and not self.client:
            logger.error("❌ Vector database ไม่พร้อมใช้งาน")
            return False
        
        try:
            if self.db_type == "chromadb":
                return await self._add_to_chromadb(documents)
            elif self.db_type == "pinecone":
                return await self._add_to_pinecone(documents)
            elif self.db_type == "sqlite":
                return await self._add_to_sqlite(documents)
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการเพิ่มเอกสาร: {e}")
            return False
    
    async def _add_to_chromadb(self, documents: List[Document]) -> bool:
        """เพิ่มเอกสารลงใน ChromaDB"""
        try:
            ids = [doc.id for doc in documents]
            contents = [doc.content for doc in documents]
            embeddings = [doc.embedding for doc in documents if doc.embedding]
            metadatas = [asdict(doc.metadata) for doc in documents]
            
            if embeddings:
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
            else:
                self.collection.add(
                    ids=ids,
                    documents=contents,
                    metadatas=metadatas
                )
            
            logger.info(f"✅ เพิ่มเอกสาร {len(documents)} รายการลงใน ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromaDB add error: {e}")
            return False
    
    async def _add_to_pinecone(self, documents: List[Document]) -> bool:
        """เพิ่มเอกสารลงใน Pinecone"""
        try:
            vectors = []
            for doc in documents:
                if doc.embedding:
                    vectors.append({
                        "id": doc.id,
                        "values": doc.embedding,
                        "metadata": {
                            "content": doc.content,
                            "source": doc.source,
                            **doc.metadata
                        }
                    })
            
            if vectors:
                self.collection.upsert(vectors=vectors)
                logger.info(f"✅ เพิ่มเอกสาร {len(vectors)} รายการลงใน Pinecone")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"❌ Pinecone add error: {e}")
            return False
    
    async def _add_to_sqlite(self, documents: List[Document]) -> bool:
        """เพิ่มเอกสารลงใน SQLite"""
        try:
            cursor = self.client.cursor()
            
            for doc in documents:
                embedding_json = json.dumps(doc.embedding) if doc.embedding else "[]"
                metadata_json = json.dumps(doc.metadata)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO document_vectors 
                    (id, content, embedding, metadata, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (doc.id, doc.content, embedding_json, metadata_json, doc.source))
            
            self.client.commit()
            logger.info(f"✅ เพิ่มเอกสาร {len(documents)} รายการลงใน SQLite")
            return True
            
        except Exception as e:
            logger.error(f"❌ SQLite add error: {e}")
            return False
    
    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        """ค้นหาเอกสารที่คล้ายคลึง"""
        if not self.collection and not self.client:
            logger.error("❌ Vector database ไม่พร้อมใช้งาน")
            return []
        
        try:
            if self.db_type == "chromadb":
                return await self._search_chromadb(query_embedding, top_k)
            elif self.db_type == "pinecone":
                return await self._search_pinecone(query_embedding, top_k)
            elif self.db_type == "sqlite":
                return await self._search_sqlite(query_embedding, top_k)
            else:
                return []
                
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการค้นหา: {e}")
            return []
    
    async def _search_chromadb(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """ค้นหาใน ChromaDB"""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            search_results = []
            for i in range(len(results['ids'][0])):
                doc_id = results['ids'][0][i]
                content = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                # แปลง distance เป็น score (0-1)
                score = 1 - distance
                
                document = Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    source=metadata.get('source', 'unknown')
                )
                
                search_results.append(SearchResult(
                    document=document,
                    score=score,
                    relevance=self._get_relevance(score)
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ ChromaDB search error: {e}")
            return []
    
    async def _search_pinecone(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """ค้นหาใน Pinecone"""
        try:
            results = self.collection.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            search_results = []
            for match in results['matches']:
                metadata = match['metadata']
                
                document = Document(
                    id=match['id'],
                    content=metadata.get('content', ''),
                    metadata=metadata,
                    source=metadata.get('source', 'unknown')
                )
                
                search_results.append(SearchResult(
                    document=document,
                    score=match['score'],
                    relevance=self._get_relevance(match['score'])
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Pinecone search error: {e}")
            return []
    
    async def _search_sqlite(self, query_embedding: List[float], top_k: int) -> List[SearchResult]:
        """ค้นหาใน SQLite (cosine similarity)"""
        try:
            cursor = self.client.cursor()
            cursor.execute("SELECT id, content, embedding, metadata, source FROM document_vectors")
            
            results = []
            query_embedding_np = np.array(query_embedding)
            
            for row in cursor.fetchall():
                doc_id, content, embedding_json, metadata_json, source = row
                
                try:
                    embedding = json.loads(embedding_json)
                    if embedding:
                        embedding_np = np.array(embedding)
                        
                        # คำนวณ cosine similarity
                        similarity = np.dot(query_embedding_np, embedding_np) / (
                            np.linalg.norm(query_embedding_np) * np.linalg.norm(embedding_np)
                        )
                        
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        
                        document = Document(
                            id=doc_id,
                            content=content,
                            metadata=metadata,
                            source=source
                        )
                        
                        results.append(SearchResult(
                            document=document,
                            score=float(similarity),
                            relevance=self._get_relevance(float(similarity))
                        ))
                        
                except Exception as e:
                    logger.warning(f"⚠️ ไม่สามารถประมวลผลเอกสาร {doc_id}: {e}")
                    continue
            
            # เรียงลำดับตาม score และเลือก top_k
            results.sort(key=lambda x: x.score, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ SQLite search error: {e}")
            return []
    
    def _get_relevance(self, score: float) -> str:
        """กำหนดระดับความเกี่ยวข้อง"""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"

class DocumentProcessor:
    """Document Processing & Chunking"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, content: str, metadata: Dict[str, Any], source: str) -> List[Document]:
        """ประมวลผลเอกสารและแบ่งเป็น chunks"""
        try:
            # ทำความสะอาดเนื้อหา
            cleaned_content = self._clean_content(content)
            
            # แบ่งเป็น chunks
            chunks = self._create_chunks(cleaned_content)
            
            # สร้าง Document objects
            documents = []
            for i, chunk in enumerate(chunks):
                doc_id = self._generate_doc_id(source, i, chunk)
                
                document = Document(
                    id=doc_id,
                    content=chunk,
                    metadata={
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk)
                    },
                    source=source,
                    chunk_index=i
                )
                
                documents.append(document)
            
            logger.info(f"✅ ประมวลผลเอกสาร {source} เป็น {len(documents)} chunks")
            return documents
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการประมวลผลเอกสาร: {e}")
            return []
    
    def _clean_content(self, content: str) -> str:
        """ทำความสะอาดเนื้อหา"""
        # ลบ whitespace ที่ไม่จำเป็น
        content = " ".join(content.split())
        
        # ลบ special characters ที่ไม่ต้องการ
        import re
        content = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', content)
        
        return content.strip()
    
    def _create_chunks(self, content: str) -> List[str]:
        """แบ่งเนื้อหาเป็น chunks"""
        if len(content) <= self.chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.chunk_size
            
            # หาจุดแบ่งที่เหมาะสม (ประโยคหรือย่อหน้า)
            if end < len(content):
                # หาจุดสิ้นสุดประโยคที่ใกล้ที่สุด
                sentence_end = content.rfind('.', start, end)
                paragraph_end = content.rfind('\n\n', start, end)
                
                if paragraph_end > sentence_end and paragraph_end > start:
                    end = paragraph_end
                elif sentence_end > start:
                    end = sentence_end + 1
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # เลื่อนไปยัง chunk ถัดไป (มี overlap)
            start = end - self.chunk_overlap
            if start >= len(content):
                break
        
        return chunks
    
    def _generate_doc_id(self, source: str, chunk_index: int, content: str) -> str:
        """สร้าง ID สำหรับเอกสาร"""
        # ใช้ hash ของ source + chunk_index + content
        content_hash = hashlib.md5(f"{source}_{chunk_index}_{content}".encode()).hexdigest()
        return f"doc_{content_hash[:12]}"

class RAGSystem:
    """RAG System หลัก"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.embedding_provider = EmbeddingProvider(
            provider_type=self.config.get("embedding_provider", "ollama"),
            model_name=self.config.get("embedding_model", "nomic-embed-text")
        )
        
        self.vector_db = VectorDatabase(
            db_type=self.config.get("vector_db", "chromadb"),
            config=self.config.get("vector_db_config", {})
        )
        
        self.document_processor = DocumentProcessor(
            chunk_size=self.config.get("chunk_size", 1000),
            chunk_overlap=self.config.get("chunk_overlap", 200)
        )
        
        # Cache system
        self.cache = redis.Redis(
            host=self.config.get("redis_host", "localhost"),
            port=self.config.get("redis_port", 6379),
            db=self.config.get("redis_db", 0),
            decode_responses=True
        )
        
        logger.info("🚀 RAG System พร้อมใช้งาน")
    
    async def initialize_system(self) -> Dict[str, Any]:
        """เริ่มต้นระบบและทดสอบการเชื่อมต่อ"""
        status = {
            "embedding_provider": False,
            "vector_database": False,
            "cache_system": False,
            "available_models": [],
            "system_ready": False
        }
        
        try:
            # ทดสอบ embedding provider
            logger.info("🔍 ทดสอบการเชื่อมต่อ Embedding Provider...")
            status["embedding_provider"] = await self.embedding_provider.test_connection()
            
            if status["embedding_provider"]:
                # ดึงรายการโมเดลที่ใช้งานได้
                status["available_models"] = await self.embedding_provider.get_available_models()
                logger.info(f"✅ พบโมเดล embedding: {status['available_models']}")
            
            # ทดสอบ vector database
            logger.info("🔍 ทดสอบการเชื่อมต่อ Vector Database...")
            status["vector_database"] = await self.vector_db.test_connection()
            
            # ทดสอบ cache system
            logger.info("🔍 ทดสอบการเชื่อมต่อ Cache System...")
            try:
                self.cache.ping()
                status["cache_system"] = True
                logger.info("✅ Cache System พร้อมใช้งาน")
            except Exception as e:
                logger.warning(f"⚠️ Cache System ไม่พร้อมใช้งาน: {e}")
            
            # ตรวจสอบว่าระบบพร้อมใช้งานหรือไม่
            status["system_ready"] = status["embedding_provider"] and status["vector_database"]
            
            if status["system_ready"]:
                logger.info("🎉 RAG System พร้อมใช้งานอย่างสมบูรณ์!")
            else:
                logger.warning("⚠️ RAG System ไม่พร้อมใช้งานบางส่วน")
            
            return status
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการเริ่มต้นระบบ: {e}")
            return status
    
    async def get_embedding_models(self) -> List[Dict[str, Any]]:
        """ดึงรายการโมเดล embedding พร้อมข้อมูล"""
        try:
            models = await self.embedding_provider.get_available_models()
            model_info = []
            
            for model_name in models:
                if hasattr(self.embedding_provider, 'ollama_client') and self.embedding_provider.ollama_client:
                    info = await self.embedding_provider.ollama_client.get_model_info(model_name)
                    model_info.append({
                        "name": model_name,
                        "type": "ollama",
                        "info": info
                    })
                else:
                    model_info.append({
                        "name": model_name,
                        "type": self.embedding_provider.provider_type,
                        "info": None
                    })
            
            return model_info
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถดึงรายการโมเดลได้: {e}")
            return []
    
    async def switch_embedding_model(self, model_name: str) -> bool:
        """เปลี่ยนโมเดล embedding"""
        try:
            # ตรวจสอบว่าโมเดลมีอยู่หรือไม่
            available_models = await self.embedding_provider.get_available_models()
            if model_name not in available_models:
                logger.error(f"❌ ไม่พบโมเดล: {model_name}")
                return False
            
            # เปลี่ยนโมเดล
            self.embedding_provider.model_name = model_name
            logger.info(f"✅ เปลี่ยนเป็นโมเดล embedding: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถเปลี่ยนโมเดลได้: {e}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """ดึงสถานะระบบ"""
        try:
            status = {
                "embedding_provider": {
                    "type": self.embedding_provider.provider_type,
                    "model": self.embedding_provider.model_name,
                    "connected": await self.embedding_provider.test_connection()
                },
                "vector_database": {
                    "type": self.vector_db.db_type,
                    "connected": await self.vector_db.test_connection()
                },
                "cache_system": {
                    "connected": False
                },
                "document_processor": {
                    "chunk_size": self.document_processor.chunk_size,
                    "chunk_overlap": self.document_processor.chunk_overlap
                }
            }
            
            # ทดสอบ cache
            try:
                self.cache.ping()
                status["cache_system"]["connected"] = True
            except:
                pass
            
            return status
            
        except Exception as e:
            logger.error(f"❌ ไม่สามารถดึงสถานะระบบได้: {e}")
            return {}
    
    async def add_document(self, content: str, metadata: Dict[str, Any], source: str) -> bool:
        """เพิ่มเอกสารลงใน RAG system"""
        try:
            # ประมวลผลเอกสาร
            documents = self.document_processor.process_document(content, metadata, source)
            
            if not documents:
                return False
            
            # สร้าง embeddings
            for doc in documents:
                doc.embedding = await self.embedding_provider.get_embedding(doc.content)
            
            # เพิ่มลงใน vector database
            success = await self.vector_db.add_documents(documents)
            
            if success:
                # Cache metadata
                cache_key = f"doc_meta:{source}"
                self.cache.setex(cache_key, 3600, json.dumps(metadata))
                
                logger.info(f"✅ เพิ่มเอกสาร {source} สำเร็จ ({len(documents)} chunks)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการเพิ่มเอกสาร: {e}")
            return False
    
    async def search(self, query: str, top_k: int = 5, use_cache: bool = True) -> List[SearchResult]:
        """ค้นหาเอกสารที่เกี่ยวข้อง"""
        try:
            # ตรวจสอบ cache
            if use_cache:
                cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    logger.info("✅ ใช้ผลลัพธ์จาก cache")
                    return [SearchResult(**json.loads(item)) for item in json.loads(cached_result)]
            
            # สร้าง query embedding
            query_embedding = await self.embedding_provider.get_embedding(query)
            if not query_embedding:
                logger.error("❌ ไม่สามารถสร้าง query embedding ได้")
                return []
            
            # ค้นหาใน vector database
            results = await self.vector_db.search(query_embedding, top_k)
            
            # Cache ผลลัพธ์
            if use_cache and results:
                cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
                cache_data = json.dumps([asdict(result) for result in results])
                self.cache.setex(cache_key, 1800, cache_data)  # Cache 30 นาที
            
            return results
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการค้นหา: {e}")
            return []
    
    async def generate_response(self, query: str, context_documents: List[Document], 
                              llm_provider: str = "ollama") -> RAGResponse:
        """สร้างการตอบกลับโดยใช้ RAG"""
        try:
            start_time = datetime.now()
            
            # สร้าง context จากเอกสารที่เกี่ยวข้อง
            context = self._build_context(context_documents)
            
            # สร้าง prompt สำหรับ LLM
            prompt = self._create_rag_prompt(query, context)
            
            # เรียกใช้ LLM
            answer = await self._call_llm(prompt, llm_provider)
            
            # คำนวณ confidence score
            confidence = self._calculate_confidence(context_documents)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RAGResponse(
                answer=answer,
                sources=context_documents,
                confidence=confidence,
                context_used=context[:500] + "..." if len(context) > 500 else context,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการสร้างการตอบกลับ: {e}")
            return RAGResponse(
                answer="ขออภัย เกิดข้อผิดพลาดในการประมวลผล",
                sources=[],
                confidence=0.0,
                context_used="",
                processing_time=0.0
            )
    
    def _build_context(self, documents: List[Document]) -> str:
        """สร้าง context จากเอกสาร"""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"เอกสาร {i} (จาก {doc.source}):\n{doc.content}\n")
        
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str) -> str:
        """สร้าง prompt สำหรับ RAG"""
        return f"""
คุณเป็น AI Assistant ที่ช่วยตอบคำถามโดยใช้ข้อมูลจากเอกสารที่ให้มา

ข้อมูลที่เกี่ยวข้อง:
{context}

คำถาม: {query}

กรุณาตอบคำถามโดยใช้ข้อมูลจากเอกสารที่ให้มาเท่านั้น หากไม่มีข้อมูลที่เกี่ยวข้อง ให้บอกว่าไม่สามารถตอบได้

คำตอบ:
"""
    
    async def _call_llm(self, prompt: str, provider: str) -> str:
        """เรียกใช้ LLM"""
        try:
            if provider == "ollama":
                return await self._call_ollama(prompt)
            elif provider == "openai":
                return await self._call_openai(prompt)
            else:
                return "ไม่รองรับ LLM provider นี้"
                
        except Exception as e:
            logger.error(f"❌ LLM call error: {e}")
            return "เกิดข้อผิดพลาดในการเรียกใช้ LLM"
    
    async def _call_ollama(self, prompt: str) -> str:
        """เรียกใช้ Ollama"""
        try:
            model = self.config.get("ollama_model", "llama3.1:8b")
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return "ไม่สามารถเชื่อมต่อกับ Ollama ได้"
                
        except Exception as e:
            logger.error(f"❌ Ollama call error: {e}")
            return "เกิดข้อผิดพลาดในการเรียกใช้ Ollama"
    
    async def _call_openai(self, prompt: str) -> str:
        """เรียกใช้ OpenAI"""
        try:
            import os
            from openai import OpenAI
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model = self.config.get("openai_model", "gpt-3.5-turbo")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ OpenAI call error: {e}")
            return "เกิดข้อผิดพลาดในการเรียกใช้ OpenAI"
    
    def _calculate_confidence(self, documents: List[Document]) -> float:
        """คำนวณ confidence score"""
        if not documents:
            return 0.0
        
        # คำนวณจากจำนวนเอกสารที่เกี่ยวข้องและความหลากหลายของแหล่งข้อมูล
        unique_sources = len(set(doc.source for doc in documents))
        total_docs = len(documents)
        
        # Confidence = (จำนวนเอกสาร * ความหลากหลายของแหล่งข้อมูล) / 10
        confidence = (total_docs * unique_sources) / 10.0
        
        return min(confidence, 1.0)  # จำกัดไม่เกิน 1.0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """ดึงสถิติของ RAG system"""
        try:
            stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "embedding_provider": self.embedding_provider.provider_type,
                "vector_db_type": self.vector_db.db_type,
                "cache_status": "connected" if self.cache.ping() else "disconnected"
            }
            
            # ดึงสถิติจาก vector database
            if self.vector_db.db_type == "chromadb" and self.vector_db.collection:
                stats["total_chunks"] = self.vector_db.collection.count()
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ เกิดข้อผิดพลาดในการดึงสถิติ: {e}")
            return {"error": str(e)}

# Factory function สำหรับสร้าง RAG System
def create_rag_system(config: Dict[str, Any] = None) -> RAGSystem:
    """สร้าง RAG System instance"""
    return RAGSystem(config)

# Example usage
if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    config = {
        "embedding_provider": "ollama",
        "embedding_model": "nomic-embed-text",
        "vector_db": "chromadb",
        "vector_db_config": {
            "path": "./chroma_db",
            "collection_name": "synapse_documents"
        },
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "redis_host": "localhost",
        "redis_port": 6379,
        "ollama_model": "llama3.1:8b"
    }
    
    async def test_rag():
        rag = create_rag_system(config)
        
        # เพิ่มเอกสารตัวอย่าง
        sample_content = """
        Synapse Backend Monolith เป็นสถาปัตยกรรมที่ออกแบบมาเพื่อเป็นศูนย์กลางของระบบทั้งหมด
        ระบบนี้จะช่วยให้การพัฒนาระยะแรกทำได้อย่างรวดเร็ว และสามารถทยอยแยกส่วนประกอบที่สำคัญ
        ออกเป็น Microservices ในภายหลังได้
        
        ระบบใช้ Python ร่วมกับ FastAPI เป็นแกนหลัก เนื่องจากเป็น Framework ที่มีประสิทธิภาพสูง
        และเหมาะกับการทำงานด้าน API และ AI เป็นอย่างยิ่ง
        """
        
        metadata = {
            "title": "Synapse Architecture",
            "author": "Orion Senior Dev",
            "category": "architecture"
        }
        
        success = await rag.add_document(sample_content, metadata, "architecture_doc")
        print(f"เพิ่มเอกสารสำเร็จ: {success}")
        
        # ทดสอบการค้นหา
        results = await rag.search("สถาปัตยกรรม Synapse", top_k=3)
        print(f"พบเอกสารที่เกี่ยวข้อง: {len(results)} รายการ")
        
        for result in results:
            print(f"- {result.document.source}: {result.score:.3f}")
        
        # ทดสอบการสร้างการตอบกลับ
        if results:
            response = await rag.generate_response(
                "Synapse Backend Monolith คืออะไร?",
                [result.document for result in results]
            )
            print(f"\nคำตอบ: {response.answer}")
            print(f"ความเชื่อมั่น: {response.confidence:.3f}")
            print(f"เวลาในการประมวลผล: {response.processing_time:.2f} วินาที")
    
    # รัน test
    asyncio.run(test_rag())
