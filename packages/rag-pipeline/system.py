"""
🎯 RAG System - Retrieval-Augmented Generation (refactor-min)
- ลดการทำซ้ำ
- จัดสถาปัตยกรรมให้ชัด
- เสริมความทนทาน I/O และแคช
"""

import asyncio
import json
import logging
import hashlib
import time
import re
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np

# Optional deps flags
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMADB_AVAILABLE = True
except Exception:
    CHROMADB_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except Exception:
    PINECONE_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except Exception:
    EXCEL_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    HTML_AVAILABLE = True
except Exception:
    HTML_AVAILABLE = False

try:
    import redis  # noqa
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False

# Unified AI Client
from packages.ai_clients.unified_ai_client import get_client

# ----------------------------- Logging ---------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag")

# ----------------------------- Config ----------------------------------
@dataclass(frozen=True)
class RAGConfig:
    embedding_provider: str = "ollama"
    embedding_model: str = "nomic-embed-text"
    vector_db: str = "chromadb"  # chromadb | pinecone | sqlite
    vector_db_config: dict = field(
        default_factory=lambda: {"path": "./chroma_db", "collection_name": "synapse_documents"}
    )
    chunk_size: int = 1000
    chunk_overlap: int = 200
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    llm_provider: str = "ollama"
    llm_model: Optional[str] = "llama3.1:8b"  # optional

# ----------------------------- DTOs ------------------------------------
@dataclass
class PerformanceMetrics:
    start_time: float = 0.0
    end_time: float = 0.0
    files_processed: int = 0
    documents_extracted: int = 0
    embeddings_generated: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def total_time(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    @property
    def files_per_second(self) -> float:
        return self.files_processed / self.total_time if self.total_time > 0 else 0.0

    @property
    def documents_per_second(self) -> float:
        return self.documents_extracted / self.total_time if self.total_time > 0 else 0.0


@dataclass
class DocumentContent:
    file_path: str
    content_type: str
    content: str
    metadata: Dict[str, Any]
    extracted_at: datetime
    file_size: int
    processing_time: float


@dataclass
class Document:
    id: str
    content: str
    metadata: Dict[str, Any]
    source: str
    chunk_index: int = 0
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SearchResult:
    document: Document
    score: float
    relevance: str  # 'high' | 'medium' | 'low'


@dataclass
class RAGResponse:
    answer: str
    sources: List[Document]
    confidence: float
    context_used: str
    processing_time: float

# ----------------------------- Utils -----------------------------------
from concurrent.futures import ThreadPoolExecutor

class IO:
    _pool = ThreadPoolExecutor(max_workers=min(32, (os.cpu_count() or 1) + 4))

    @staticmethod
    async def run(func, *a, **kw):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(IO._pool, lambda: func(*a, **kw))


def read_text_any(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    return path.read_bytes().decode("utf-8", errors="ignore")


# ------------------------ IntelligentFileProcessor ----------------------
EXT_KIND = {
    # text
    ".txt": "text",
    ".md": "text",
    ".rst": "text",
    ".log": "text",
    # code
    ".py": "code",
    ".js": "code",
    ".ts": "code",
    ".jsx": "code",
    ".tsx": "code",
    ".java": "code",
    ".cpp": "code",
    ".c": "code",
    ".h": "code",
    ".hpp": "code",
    ".cs": "code",
    ".php": "code",
    ".rb": "code",
    ".go": "code",
    ".rs": "code",
    ".swift": "code",
    ".kt": "code",
    ".scala": "code",
    ".dart": "code",
    ".html": "code",
    ".css": "code",
    ".scss": "code",
    ".sass": "code",
    ".xml": "code",
    ".json": "code",
    ".yaml": "code",
    ".yml": "code",
    ".toml": "code",
    ".ini": "code",
    ".cfg": "code",
    ".conf": "code",
    ".sh": "code",
    ".bat": "code",
    ".ps1": "code",
    ".sql": "code",
    # documents
    ".pdf": "document",
    ".docx": "document",
    ".doc": "document",
    ".xlsx": "document",
    ".xls": "document",
    ".pptx": "document",
    ".ppt": "document",
    ".odt": "document",
    ".ods": "document",
    # data
    ".csv": "data",
    ".tsv": "data",
}

SIZE_LIMIT = {
    "text": 10 * 1024 * 1024,
    "code": 5 * 1024 * 1024,
    "document": 50 * 1024 * 1024,
    "data": 100 * 1024 * 1024,
    "config": 1 * 1024 * 1024,
}


class Extractors:
    registry: Dict[str, Any] = {}

    @classmethod
    def register(cls, key):
        def wrap(fn):
            cls.registry[key] = fn
            return fn
        return wrap

    @staticmethod
    async def extract(path: Path, kind: str) -> Optional[str]:
        fn = Extractors.registry.get(kind)
        return await fn(path) if fn else None


@Extractors.register("text")
async def _extract_text(path: Path) -> Optional[str]:
    return await IO.run(read_text_any, path)


@Extractors.register("code")
async def _extract_code(path: Path) -> Optional[str]:
    raw = await IO.run(read_text_any, path)
    if not raw:
        return None
    return f"// File: {path.name}\n// Content:\n{raw}"


@Extractors.register("document")
async def _extract_document(path: Path) -> Optional[str]:
    ext = path.suffix.lower()
    if ext == ".pdf" and PDF_AVAILABLE:
        def _pdf():
            with open(path, "rb") as f:
                r = PyPDF2.PdfReader(f)
                return "\n".join((p.extract_text() or "") for p in r.pages)
        return await IO.run(_pdf)
    if ext == ".docx" and DOCX_AVAILABLE:
        def _docx():
            d = docx.Document(path)
            return "\n".join(p.text for p in d.paragraphs)
        return await IO.run(_docx)
    # fallback
    return await IO.run(read_text_any, path)


@Extractors.register("data")
async def _extract_data(path: Path) -> Optional[str]:
    ext = path.suffix.lower()
    if ext == ".csv":
        raw = await IO.run(read_text_any, path)
        lines = raw.splitlines()
        hdr = lines[0] if lines else ""
        return f"CSV:{path.name}\nHEADER:{hdr}\nROWS:{max(0,len(lines)-1)}\nPREVIEW:\n" + "\n".join(lines[:100])
    if ext == ".json":
        raw = await IO.run(read_text_any, path)
        try:
            obj = json.loads(raw)
            typ = type(obj).__name__
            keys = list(obj.keys()) if isinstance(obj, dict) else []
            meta = f"JSON:{path.name} TYPE:{typ} KEYS:{','.join(map(str,keys))}"
            return f"{meta}\nCONTENT:\n{raw}"
        except Exception:
            return raw
    if ext == ".xml" and HTML_AVAILABLE:
        raw = await IO.run(read_text_any, path)
        soup = BeautifulSoup(raw, "xml")
        root = soup.find().name if soup.find() else "None"
        return f"XML:{path.name} ROOT:{root}\nTEXT:\n{soup.get_text()}"
    return await IO.run(read_text_any, path)


def detect_kind(p: Path) -> Optional[str]:
    return EXT_KIND.get(p.suffix.lower())


class IntelligentFileProcessor:
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        logger.info(f"FileProcessor ready (Workers:{self.max_workers})")

    def _find_files(self, root: str, include: List[str], exclude: List[str]) -> List[str]:
        rootp = Path(root)
        files: List[str] = []
        for pat in include:
            for fp in rootp.rglob(pat):
                if not fp.is_file():
                    continue
                ignore = any(fp.match(ex) for ex in exclude)
                if not ignore:
                    files.append(str(fp))
        return list(dict.fromkeys(files))

    async def process_directory_deep(
        self,
        root_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[DocumentContent]:
        t0 = time.time()
        include = include_patterns or ["*"]
        exclude = exclude_patterns or [
            "*.exe", "*.dll", "*.so", "*.dylib", "*.bin",
            "*.zip", "*.tar", "*.gz", "*.rar", "*.7z",
            "*.mp3", "*.mp4", "*.avi", "*.mov", "*.wmv",
            "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp",
            "*.iso", "*.img", "*.vmdk", "*.vhd",
        ]
        paths = self._find_files(root_path, include, exclude)
        logger.info(f"Found {len(paths)} files in {root_path}")

        docs: List[DocumentContent] = []
        for p in paths:
            try:
                dc = await self._process_single_file(p)
                if dc:
                    docs.append(dc)
            except Exception as e:
                logger.warning(f"skip {p}: {e}")
        logger.info(f"Processed {len(docs)} files in {time.time()-t0:.2f}s")
        return docs

    async def _process_single_file(self, file_path: str) -> Optional[DocumentContent]:
        t0 = time.time()
        p = Path(file_path)
        if not p.exists() or p.stat().st_size == 0:
            return None
        kind = detect_kind(p)
        if not kind:
            return None
        if p.stat().st_size > SIZE_LIMIT.get(kind, 1024 * 1024):
            logger.info(f"skip large file {p} ({p.stat().st_size} bytes)")
            return None
        content = await Extractors.extract(p, kind)
        if not content:
            return None
        md = {
            "file_name": p.name,
            "file_path": str(p),
            "content_type": kind,
            "file_extension": p.suffix.lower(),
            "created_time": datetime.fromtimestamp(p.stat().st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(p.stat().st_mtime).isoformat(),
            "parent_directory": str(p.parent),
        }
        return DocumentContent(
            file_path=str(p),
            content_type=kind,
            content=content,
            metadata=md,
            extracted_at=datetime.now(),
            file_size=p.stat().st_size,
            processing_time=time.time() - t0,
        )

# --------------------------- Chunker ------------------------------------
class Chunker:
    def __init__(self, size=1000, overlap=200):
        self.size = size
        self.overlap = overlap

    def split(self, text: str) -> List[str]:
        txt = re.sub(r"\s+", " ", text).strip()
        if len(txt) <= self.size:
            return [txt] if txt else []
        chunks, i = [], 0
        n = len(txt)
        while i < n:
            j = min(i + self.size, n)
            cut = txt.rfind(".", i, j)
            if cut == -1 or cut <= i:
                cut = j
            chunk = txt[i:cut].strip()
            if chunk:
                chunks.append(chunk)
            if cut >= n:
                break
            nxt = max(cut - self.overlap, i + 1)  # guard loop
            if nxt <= i:
                nxt = cut
            i = nxt
        return chunks

# --------------------------- Embeddings ---------------------------------
class EmbeddingProvider:
    def __init__(self, provider_type: str, model_name: str):
        self.provider_type = provider_type
        self.model_name = model_name
        self.ai_client = get_client()
        self.is_ready = bool(self.ai_client.get_provider(self.provider_type))
        if not self.is_ready:
            logger.warning(f"Embedding provider '{provider_type}' unavailable")

    async def test_connection(self) -> bool:
        if not self.is_ready:
            return False
        try:
            r = self.ai_client.embed(self.provider_type, "ping", model=self.model_name)
            return bool(r and r.get("success"))
        except Exception as e:
            logger.error(f"embed test fail: {e}")
            return False

    async def embed_one(self, text: str) -> Optional[List[float]]:
        if not self.is_ready:
            return None
        try:
            r = self.ai_client.embed(self.provider_type, text, model=self.model_name)
            if r and r.get("success"):
                return r.get("embedding")
        except Exception as e:
            logger.error(f"embed error: {e}")
        return None

    async def embed_many(self, texts: List[str]) -> List[Optional[List[float]]]:
        # naive loop; replace with batch call if client supports
        outs: List[Optional[List[float]]] = []
        for t in texts:
            outs.append(await self.embed_one(t))
        return outs

# --------------------------- Vector DB ----------------------------------
import sqlite3

class VectorDatabase:
    def __init__(self, db_type: str, config: Dict[str, Any]):
        self.db_type = db_type
        self.config = config or {}
        self.client = None
        self.collection = None
        self._setup()

    def _setup(self):
        if self.db_type == "chromadb":
            if not CHROMADB_AVAILABLE:
                logger.warning("ChromaDB not available")
                return
            try:
                self.client = chromadb.PersistentClient(
                    path=self.config.get("path", "./chroma_db"),
                    settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
                )
                self.collection = self.client.get_or_create_collection(
                    name=self.config.get("collection_name", "synapse_documents"),
                    metadata={"description": "Synapse RAG Documents"},
                )
                logger.info("ChromaDB ready")
            except Exception as e:
                logger.error(f"Chroma setup error: {e}")

        elif self.db_type == "pinecone":
            if not PINECONE_AVAILABLE:
                logger.warning("Pinecone not available")
                return
            try:
                api_key = self.config.get("api_key")
                environment = self.config.get("environment")
                if not api_key or not environment:
                    logger.warning("Pinecone api_key/environment required")
                    return
                pinecone.init(api_key=api_key, environment=environment)
                index_name = self.config.get("index_name", "synapse-rag")
                if index_name not in pinecone.list_indexes():
                    pinecone.create_index(
                        name=index_name,
                        dimension=self.config.get("dimension", 1536),
                        metric="cosine",
                    )
                self.collection = pinecone.Index(index_name)
                logger.info("Pinecone ready")
            except Exception as e:
                logger.error(f"Pinecone setup error: {e}")

        elif self.db_type == "sqlite":
            try:
                db_path = self.config.get("db_path", "./synapse_vectors.db")
                self.client = sqlite3.connect(db_path)
                self.client.execute(
                    """
                    CREATE TABLE IF NOT EXISTS document_vectors (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        embedding TEXT NOT NULL,
                        metadata TEXT,
                        source TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )
                self.client.execute(
                    "CREATE INDEX IF NOT EXISTS idx_document_source ON document_vectors(source)"
                )
                self.client.commit()
                logger.info("SQLite vector ready")
            except Exception as e:
                logger.error(f"SQLite setup error: {e}")

        else:
            logger.warning(f"Vector DB '{self.db_type}' not supported")

    async def test_connection(self) -> bool:
        try:
            if self.db_type == "chromadb":
                return self.client is not None and self.collection is not None
            if self.db_type == "pinecone":
                return self.collection is not None
            if self.db_type == "sqlite":
                return self.client is not None
        except Exception:
            return False
        return False

    def _rel(self, s: float) -> str:
        return "high" if s >= 0.8 else "medium" if s >= 0.6 else "low"

    async def add_documents(self, docs: List[Document]) -> bool:
        if not docs:
            return False
        try:
            if self.db_type == "chromadb" and self.collection:
                ids = [d.id for d in docs]
                texts = [d.content for d in docs]
                metas = [d.metadata for d in docs]
                has_all = all(d.embedding is not None for d in docs)
                if has_all:
                    embs = [d.embedding for d in docs]
                    self.collection.add(ids=ids, documents=texts, metadatas=metas, embeddings=embs)
                else:
                    self.collection.add(ids=ids, documents=texts, metadatas=metas)
                return True

            if self.db_type == "pinecone" and self.collection:
                vecs = []
                for d in docs:
                    if d.embedding is None:
                        continue
                    vecs.append(
                        {
                            "id": d.id,
                            "values": d.embedding,
                            "metadata": {"content": d.content, "source": d.source, **d.metadata},
                        }
                    )
                if vecs:
                    self.collection.upsert(vectors=vecs)
                    return True
                return False

            if self.db_type == "sqlite" and self.client:
                cur = self.client.cursor()
                for d in docs:
                    emb = json.dumps(d.embedding or [])
                    meta = json.dumps(d.metadata or {})
                    cur.execute(
                        "INSERT OR REPLACE INTO document_vectors (id, content, embedding, metadata, source) VALUES (?, ?, ?, ?, ?)",
                        (d.id, d.content, emb, meta, d.source),
                    )
                self.client.commit()
                return True
        except Exception as e:
            logger.error(f"add_documents error: {e}")
            return False
        return False

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        if not query_embedding:
            return []
        try:
            if self.db_type == "chromadb" and self.collection:
                res = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
                out: List[SearchResult] = []
                ids = res.get("ids", [[]])[0]
                docs = res.get("documents", [[]])[0]
                metas = res.get("metadatas", [[]])[0]
                dists = res.get("distances", [[]])[0]
                for i in range(len(ids)):
                    score = 1.0 - float(dists[i])
                    md = metas[i] or {}
                    doc = Document(
                        id=ids[i],
                        content=docs[i],
                        metadata=md,
                        source=md.get("source", md.get("file_path", "unknown")),
                        chunk_index=int(md.get("chunk_index", 0)),
                    )
                    out.append(SearchResult(document=doc, score=score, relevance=self._rel(score)))
                return out

            if self.db_type == "pinecone" and self.collection:
                res = self.collection.query(vector=query_embedding, top_k=top_k, include_metadata=True)
                out: List[SearchResult] = []
                for m in res.get("matches", []):
                    md = m.get("metadata", {}) or {}
                    doc = Document(
                        id=m["id"],
                        content=md.get("content", ""),
                        metadata=md,
                        source=md.get("source", "unknown"),
                        chunk_index=int(md.get("chunk_index", 0)),
                    )
                    sc = float(m.get("score", 0.0))
                    out.append(SearchResult(document=doc, score=sc, relevance=self._rel(sc)))
                return out

            if self.db_type == "sqlite" and self.client:
                cur = self.client.cursor()
                cur.execute("SELECT id, content, embedding, metadata, source FROM document_vectors")
                q = np.array(query_embedding, dtype=np.float32)
                outs: List[SearchResult] = []
                for (id_, content, emb_json, meta_json, src) in cur.fetchall():
                    try:
                        e = np.array(json.loads(emb_json), dtype=np.float32)
                        if e.size == 0:
                            continue
                        sim = float(np.dot(q, e) / (np.linalg.norm(q) * np.linalg.norm(e)))
                        md = json.loads(meta_json or "{}")
                        doc = Document(id=id_, content=content, metadata=md, source=src, chunk_index=int(md.get("chunk_index", 0)))
                        outs.append(SearchResult(document=doc, score=sim, relevance=self._rel(sim)))
                    except Exception:
                        continue
                outs.sort(key=lambda x: x.score, reverse=True)
                return outs[:top_k]
        except Exception as e:
            logger.error(f"search error: {e}")
            return []
        return []

# ------------------------------ RAG Core --------------------------------
class DocumentProcessor:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunker = Chunker(chunk_size, chunk_overlap)

    def process_document(self, content: str, metadata: Dict[str, Any], source: str) -> List[Document]:
        txt = re.sub(r"\s+", " ", content or "").strip()
        if not txt:
            return []
        chunks = self.chunker.split(txt)
        docs: List[Document] = []
        for i, ch in enumerate(chunks):
            doc_id = hashlib.md5(f"{source}:{i}:{ch}".encode()).hexdigest()[:12]
            md = {**(metadata or {}), "chunk_index": i, "total_chunks": len(chunks), "chunk_size": len(ch)}
            docs.append(Document(id=f"doc_{doc_id}", content=ch, metadata=md, source=source, chunk_index=i))
        return docs


def pack_results(results: List[SearchResult]) -> str:
    return json.dumps(
        [
            {
                "document": {
                    "id": r.document.id,
                    "content": r.document.content,
                    "metadata": r.document.metadata,
                    "source": r.document.source,
                    "chunk_index": r.document.chunk_index,
                },
                "score": r.score,
                "relevance": r.relevance,
            }
            for r in results
        ]
    )


def unpack_results(s: str) -> List[SearchResult]:
    arr = json.loads(s)
    outs: List[SearchResult] = []
    for it in arr:
        d = it["document"]
        doc = Document(
            id=d["id"],
            content=d["content"],
            metadata=d.get("metadata", {}),
            source=d.get("source", "unknown"),
            chunk_index=d.get("chunk_index", 0),
        )
        outs.append(SearchResult(document=doc, score=it["score"], relevance=it["relevance"]))
    return outs


class RAGSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = RAGConfig(**(config or {}))

        self.embedding_provider = EmbeddingProvider(self.config.embedding_provider, self.config.embedding_model)
        self.vector_db = VectorDatabase(self.config.vector_db, self.config.vector_db_config)
        self.document_processor = DocumentProcessor(self.config.chunk_size, self.config.chunk_overlap)
        self.file_processor = IntelligentFileProcessor()

        self.metrics = PerformanceMetrics()

        self.cache = None
        if REDIS_AVAILABLE:
            try:
                import redis
                self.cache = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    db=self.config.redis_db,
                    decode_responses=True,
                )
                self.cache.ping()
                logger.info("Redis cache ready")
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
                self.cache = None

        self.ai_client = get_client()
        logger.info("RAGSystem ready")

    async def initialize_system(self) -> Dict[str, Any]:
        st = {
            "embedding_provider": await self.embedding_provider.test_connection(),
            "vector_database": await self.vector_db.test_connection(),
            "cache_system": bool(self.cache),
        }
        st["system_ready"] = st["embedding_provider"] and st["vector_database"]
        return st

    async def get_system_status(self) -> Dict[str, Any]:
        return {
            "embedding_provider": {
                "type": self.embedding_provider.provider_type,
                "model": self.embedding_provider.model_name,
                "connected": await self.embedding_provider.test_connection(),
            },
            "vector_database": {"type": self.vector_db.db_type, "connected": await self.vector_db.test_connection()},
            "cache_system": {"connected": bool(self.cache)},
            "document_processor": {
                "chunk_size": self.config.chunk_size,
                "chunk_overlap": self.config.chunk_overlap,
            },
        }

    async def scan_directory_deep(
        self, root_path: str, include_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        self.metrics.start_time = time.time()
        docs = await self.file_processor.process_directory_deep(root_path, include_patterns, exclude_patterns)
        self.metrics.files_processed = len(docs)

        total_chunks = 0
        for dc in docs:
            if await self.add_document(dc.content, dc.metadata, dc.file_path):
                total_chunks += 1  # corrected below by embeddings count

        self.metrics.end_time = time.time()
        self.metrics.documents_extracted = len(docs)
        return self._create_scan_report(docs)

    def _create_scan_report(self, documents: List[DocumentContent]) -> Dict[str, Any]:
        content_types: Dict[str, int] = {}
        file_exts: Dict[str, int] = {}
        total_size = 0
        for d in documents:
            content_types[d.content_type] = content_types.get(d.content_type, 0) + 1
            ext = d.metadata.get("file_extension", "unknown")
            file_exts[ext] = file_exts.get(ext, 0) + 1
            total_size += d.file_size

        perf = {
            "total_time": self.metrics.total_time,
            "files_per_second": self.metrics.files_per_second,
            "documents_per_second": self.metrics.documents_per_second,
            "embeddings_generated": self.metrics.embeddings_generated,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
        }
        return {
            "summary": {
                "total_documents": len(documents),
                "total_size_mb": total_size / (1024 * 1024),
                "content_types": content_types,
                "file_extensions": dict(sorted(file_exts.items(), key=lambda x: x[1], reverse=True)[:20]),
                "performance": perf,
            },
            "documents": [
                {"file_path": d.file_path, "content_type": d.content_type, "file_size": d.file_size}
                for d in documents[:100]
            ],
            "errors": self.metrics.errors,
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        hits = self.metrics.cache_hits
        misses = self.metrics.cache_misses
        denom = hits + misses
        return {
            "total_time": self.metrics.total_time,
            "files_processed": self.metrics.files_processed,
            "cache_hit_rate": hits / denom if denom > 0 else 0.0,
            "errors": self.metrics.errors,
        }

    async def add_document(self, content: str, metadata: Dict[str, Any], source: str) -> bool:
        docs = self.document_processor.process_document(content, metadata, source)
        if not docs:
            return False
        embs = await self.embedding_provider.embed_many([d.content for d in docs])
        gen_count = 0
        for d, e in zip(docs, embs):
            d.embedding = e
            if e is not None:
                gen_count += 1
        self.metrics.embeddings_generated += gen_count

        saved = await self.vector_db.add_documents(docs)
        if saved and self.cache:
            try:
                self.cache.setex(f"doc_meta:{source}", 3600, json.dumps(metadata or {}))
            except Exception:
                pass
        return saved

    async def search(self, query: str, top_k: int = 5, use_cache: bool = True) -> List[SearchResult]:
        key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
        if use_cache and self.cache:
            cached = self.cache.get(key)
            if cached:
                self.metrics.cache_hits += 1
                try:
                    return unpack_results(cached)
                except Exception:
                    pass
            else:
                self.metrics.cache_misses += 1

        qemb = await self.embedding_provider.embed_one(query)
        if not qemb:
            return []
        results = await self.vector_db.search(qemb, top_k)
        if use_cache and self.cache and results:
            try:
                self.cache.setex(key, 1800, pack_results(results))
            except Exception:
                pass
        return results

    def _build_context(self, docs: List[Document]) -> str:
        parts: List[str] = []
        for i, d in enumerate(docs, 1):
            head = d.content[:800]
            src = Path(d.source).name if d.source else "unknown"
            parts.append(f"[{i}] Source:{src} Chunk:{d.chunk_index}\n{head}\n")
        return "\n".join(parts)

    def _create_rag_prompt(self, query: str, context: str) -> str:
        return (
            "You are an AI assistant that answers ONLY from the given documents.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer concisely. If not in context, say you cannot answer.\n"
        )

    async def _call_llm(self, prompt: str, provider: Optional[str] = None) -> str:
        prov = provider or self.config.llm_provider
        if not self.ai_client.get_provider(prov):
            return f"LLM provider '{prov}' not configured."
        try:
            messages = [{"role": "user", "content": prompt}]
            result = self.ai_client.generate_response(prov, messages, model=self.config.llm_model)
            if result and result.get("success"):
                return result.get("content", "").strip() or "No content."
            return f"LLM error: {result.get('error','unknown')}"
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            return "LLM call failed."

    def _confidence(self, docs: List[Document]) -> float:
        if not docs:
            return 0.0
        unique_sources = len({d.source for d in docs})
        total_docs = len(docs)
        return float(min(1.0, (total_docs * unique_sources) / 10.0))

    async def generate_response(self, query: str, context_documents: List[Document], llm_provider: Optional[str] = None) -> RAGResponse:
        t0 = time.time()
        try:
            context = self._build_context(context_documents)
            prompt = self._create_rag_prompt(query, context)
            answer = await self._call_llm(prompt, ll_provider)
            conf = self._confidence(context_documents)
            used = context[:500] + "..." if len(context) > 500 else context
            return RAGResponse(answer=answer, sources=context_documents, confidence=conf, context_used=used, processing_time=time.time() - t0)
        except Exception as e:
            logger.error(f"generate_response error: {e}")
            return RAGResponse(answer="Error occurred.", sources=[], confidence=0.0, context_used="", processing_time=0.0)

    async def get_statistics(self) -> Dict[str, Any]:
        try:
            stats = {
                "total_chunks": 0,
                "embedding_provider": self.embedding_provider.provider_type,
                "vector_db_type": self.vector_db.db_type,
                "cache_status": "connected" if self.cache else "disconnected",
            }
            if self.vector_db.db_type == "chromadb" and self.vector_db.collection:
                stats["total_chunks"] = self.vector_db.collection.count()
            return stats
        except Exception as e:
            logger.error(f"stats error: {e}")
            return {"error": str(e)}


# ----------------------------- Factory ----------------------------------
def create_rag_system(config: Optional[Dict[str, Any]] = None) -> RAGSystem:
    return RAGSystem(config)


# ----------------------------- Example ----------------------------------
if __name__ == "__main__":
    async def demo():
        cfg = {
            "embedding_provider": "ollama",
            "embedding_model": "nomic-embed-text",
            "vector_db": "chromadb",
            "vector_db_config": {"path": "./chroma_db", "collection_name": "synapse_documents"},
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "redis_host": "localhost",
            "redis_port": 6379,
            "llm_model": "llama3.1:8b",
        }
        rag = create_rag_system(cfg)
        status = await rag.initialize_system()
        print("Status:", status)

        sample = (
            "The Synapse Backend Monolith is the central hub. "
            "It enables rapid development then allows migration to microservices. "
            "The core is Python with FastAPI for high-performance API and AI work."
        )
        meta = {"title": "Synapse Architecture", "author": "Orion Senior Dev", "category": "architecture"}
        ok = await rag.add_document(sample, meta, "architecture_doc")
        print("Added:", ok)

        results = await rag.search("What is the Synapse architecture?", top_k=3)
        print("Results:", [(r.document.source, round(r.score, 3)) for r in results])

        if results:
            resp = await rag.generate_response("What is the Synapse Backend Monolith?", [r.document for r in results])
            print("Answer:", resp.answer)
            print("Confidence:", round(resp.confidence, 3), "Time:", round(resp.processing_time, 2), "s")

    asyncio.run(demo())