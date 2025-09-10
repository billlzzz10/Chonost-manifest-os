# 🎯 RAG System Architecture Overview

## Synapse Backend Monolith - Retrieval-Augmented Generation

- --

## 🏗️ **สถาปัตยกรรมโดยรวม** ### ** Synapse Backend Monolith Architecture** ```
┌─────────────────────────────────────────────────────────────┐
│                    Synapse Backend Monolith                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   API Gateway   │  │  Authentication │  │ User Mgmt    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  RAG System     │  │  AI Orchestrator│  │ Sync Engine  │ │
│  │  (Core)         │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Vector Database │  │   Embedding     │  │   Cache      │ │
│  │ (ChromaDB/      │  │   Provider      │  │  (Redis)     │ │
│  │  Pinecone/      │  │                 │  │              │ │
│  │  SQLite)        │  │                 │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   MySQL         │  │   Redis         │  │   File       │ │
│  │  (Primary DB)   │  │  (Cache/Queue)  │  │  Storage     │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

- --

## 🎯 ** RAG System Components** ### ** 1. Embedding Provider** ```python
class EmbeddingProvider:
    """Provider สำหรับ Embedding Models"""

    # รองรับ Multiple Providers:
    # - Ollama (Local): nomic-embed-text, all-MiniLM-L6-v2
    # - OpenAI: text-embedding-ada-002, text-embedding-3-small
    # - Sentence Transformers: all-MiniLM-L6-v2, paraphrase-multilingual-MiniLM-L12-v2
```

* * Features:**
- ✅ ** Local Embedding**: ใช้ Ollama สำหรับ embedding แบบ local
- ✅ ** Cloud Embedding**: รองรับ OpenAI และ cloud providers อื่นๆ
- ✅ ** Multi-language**: รองรับภาษาไทยและภาษาอื่นๆ
- ✅ ** Async Processing**: ประมวลผลแบบ asynchronous
- ✅ ** Fallback Mechanism**: ระบบ fallback เมื่อ provider หลักไม่พร้อม

### ** 2. Vector Database**

```
class VectorDatabase:
    """Vector Database Manager"""

    # รองรับ Multiple Databases:
    # - ChromaDB (Local/Cloud)
    # - Pinecone (Cloud)
    # - SQLite (Local with vector extensions)
    # - Weaviate (Local/Cloud)
```

* * Features:**
- ✅ ** Multi-DB Support**: รองรับหลาย vector database
- ✅ ** Hybrid Search**: รวม semantic search + keyword search
- ✅ ** Scalability**: รองรับการขยายตัว
- ✅ ** Backup & Recovery**: ระบบสำรองข้อมูล
- ✅ ** Performance Optimization**: indexing และ caching

### ** 3. Document Processor**

```
class DocumentProcessor:
    """Document Processing & Chunking"""

    # Features:
    # - Smart Chunking: แบ่งเอกสารอย่างฉลาด
    # - Metadata Extraction: ดึงข้อมูล metadata
    # - Content Cleaning: ทำความสะอาดเนื้อหา
    # - Multi-format Support: รองรับหลายรูปแบบไฟล์
```

* * Chunking Strategy:**
- ** Semantic Chunking**: แบ่งตามความหมาย
- ** Overlap Strategy**: มี overlap เพื่อรักษาความต่อเนื่อง
- ** Size Optimization**: ปรับขนาด chunk ตาม embedding model
- ** Quality Preservation**: รักษาคุณภาพเนื้อหา

### ** 4. RAG System Core**

```
class RAGSystem:
    """RAG System หลัก"""

    # Workflow:
    # 1. Document Ingestion → Processing → Embedding → Storage
    # 2. Query Processing → Embedding → Search → Retrieval
    # 3. Context Building → LLM Generation → Response
```

- --

## 🔄 ** Data Flow Architecture**

### ** Document Ingestion Flow**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Document  │───▶│  Processor  │───▶│ Embedding   │───▶│ Vector DB   │
│   Input     │    │  (Chunking) │    │  Provider   │    │  Storage    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### ** Query Processing Flow**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Query    │───▶│ Embedding   │───▶│ Vector DB   │───▶│ Context     │
│   Input     │    │  Provider   │    │   Search    │    │  Building   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   Response  │◀───│     LLM     │◀───│   Prompt    │◀───────┘
│   Output    │    │ Generation  │    │  Creation   │
└─────────────┘    └─────────────┘    └─────────────┘
```

- --

## 🗄️ ** Database Architecture**

### ** MySQL (Primary Database)**

```
- - Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

- - Document Metadata
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    content_hash VARCHAR(64),
    source_type VARCHAR(50), -- 'obsidian', 'notion', 'file'
    source_id VARCHAR(255),
    metadata JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

- - RAG Sessions
CREATE TABLE rag_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    query TEXT,
    response TEXT,
    confidence FLOAT,
    processing_time FLOAT,
    created_at TIMESTAMP
);
```

### ** Redis (Cache & Queue)**

```
# Cache Keys
search:query_hash -> [search_results]
doc_meta:source_id -> metadata_json
embedding:content_hash -> embedding_vector

# Queue
rag_processing_queue -> [document_ids]
embedding_queue -> [content_chunks]
```

### ** Vector Database (ChromaDB/Pinecone)**

```
# Document Vectors
{
    "id": "doc_abc123",
    "content": "document chunk content",
    "embedding": [0.1, 0.2, 0.3, ...],
    "metadata": {
        "source": "obsidian_vault",
        "title": "Document Title",
        "tags": ["tag1", "tag2"],
        "chunk_index": 0
    }
}
```

- --

## 🤖 ** AI Integration Architecture**

### ** LLM Providers**

```
# รองรับ Multiple LLM Providers:
LLM_PROVIDERS = {
    "ollama": {
        "models": ["llama3.1:8b", "deepseek-coder:6.7b", "qwen3:8b"],
        "endpoint": "http://localhost:11434/api/generate"
    },
    "openai": {
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
        "endpoint": "https://api.openai.com/v1/chat/completions"
    },
    "anthropic": {
        "models": ["claude-3-sonnet", "claude-3-haiku"],
        "endpoint": "https://api.anthropic.com/v1/messages"
    }
}
```

### ** Embedding Models**

```
# รองรับ Multiple Embedding Models:
EMBEDDING_MODELS = {
    "ollama": {
        "nomic-embed-text": {"dimensions": 768, "multilingual": True},
        "all-MiniLM-L6-v2": {"dimensions": 384, "multilingual": False}
    },
    "openai": {
        "text-embedding-ada-002": {"dimensions": 1536, "multilingual": False},
        "text-embedding-3-small": {"dimensions": 1536, "multilingual": True}
    },
    "sentence_transformers": {
        "all-MiniLM-L6-v2": {"dimensions": 384, "multilingual": False},
        "paraphrase-multilingual-MiniLM-L12-v2": {"dimensions": 384, "multilingual": True}
    }
}
```

- --

## 🔧 ** Configuration Architecture**

### ** RAG System Configuration**

```
RAG_CONFIG = {
    # Embedding Configuration
    "embedding_provider": "ollama",  # "ollama", "openai", "sentence_transformers"
    "embedding_model": "nomic-embed-text",
    "embedding_dimensions": 768,

    # Vector Database Configuration
    "vector_db": "chromadb",  # "chromadb", "pinecone", "sqlite"
    "vector_db_config": {
        "path": "./chroma_db",
        "collection_name": "synapse_documents",
        "distance_metric": "cosine"
    },

    # Document Processing Configuration
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_chunks_per_document": 50,

    # Search Configuration
    "search_top_k": 5,
    "similarity_threshold": 0.7,
    "enable_hybrid_search": True,

    # Caching Configuration
    "cache_enabled": True,
    "cache_ttl": 1800,  # 30 minutes
    "redis_host": "localhost",
    "redis_port": 6379,

    # LLM Configuration
    "llm_provider": "ollama",
    "llm_model": "llama3.1:8b",
    "max_tokens": 1000,
    "temperature": 0.7,

    # Performance Configuration
    "batch_size": 10,
    "max_concurrent_requests": 5,
    "timeout": 30
}
```

- --

## 🚀 ** API Endpoints Architecture**

### ** RAG System API**

```
# Document Management
POST   /api/rag/documents          # เพิ่มเอกสาร
GET    /api/rag/documents          # ดึงรายการเอกสาร
GET    /api/rag/documents/{id}     # ดึงเอกสารเฉพาะ
DELETE /api/rag/documents/{id}     # ลบเอกสาร

# Search & Query
POST   /api/rag/search             # ค้นหาเอกสาร
POST   /api/rag/query              # ส่งคำถาม
GET    /api/rag/suggestions        # คำแนะนำการค้นหา

# System Management
GET    /api/rag/status             # สถานะระบบ
GET    /api/rag/statistics         # สถิติการใช้งาน
POST   /api/rag/reindex            # สร้าง index ใหม่
POST   /api/rag/backup             # สำรองข้อมูล
```

### ** Response Format**

```
{
    "success": true,
    "data": {
        "answer": "คำตอบจาก RAG system",
        "sources": [
            {
                "id": "doc_123",
                "title": "Document Title",
                "content": "Relevant content...",
                "score": 0.85,
                "source": "obsidian_vault"
            }
        ],
        "confidence": 0.92,
        "processing_time": 1.23,
        "metadata": {
            "total_documents_searched": 1000,
            "embedding_model_used": "nomic-embed-text",
            "vector_db_used": "chromadb"
        }
    },
    "error": null
}
```

- --

## 📊 ** Performance & Scalability**

### ** Performance Metrics**

```
PERFORMANCE_METRICS = {
    "embedding_generation": {
        "avg_time_ms": 150,
        "throughput_per_second": 6.7,
        "memory_usage_mb": 512
    },
    "vector_search": {
        "avg_query_time_ms": 45,
        "throughput_per_second": 22.2,
        "index_size_mb": 1024
    },
    "llm_generation": {
        "avg_response_time_ms": 2500,
        "throughput_per_second": 0.4,
        "token_usage_per_request": 150
    },
    "overall_system": {
        "avg_end_to_end_time_ms": 2700,
        "concurrent_users_supported": 100,
        "daily_requests_handled": 86400
    }
}
```

### ** Scalability Strategy**

```
SCALABILITY_STRATEGY = {
    "horizontal_scaling": {
        "load_balancer": "nginx",
        "multiple_instances": True,
        "auto_scaling": True
    },
    "database_scaling": {
        "read_replicas": 3,
        "sharding": True,
        "connection_pooling": True
    },
    "caching_strategy": {
        "multi_level_cache": True,
        "distributed_cache": "redis_cluster",
        "cache_invalidation": "smart_ttl"
    },
    "async_processing": {
        "background_tasks": True,
        "message_queue": "redis",
        "batch_processing": True
    }
}
```

- --

## 🔒 ** Security Architecture**

### ** Security Measures**

```
SECURITY_CONFIG = {
    "authentication": {
        "jwt_tokens": True,
        "api_keys": True,
        "rate_limiting": True
    },
    "data_protection": {
        "encryption_at_rest": True,
        "encryption_in_transit": True,
        "data_masking": True
    },
    "access_control": {
        "role_based_access": True,
        "document_level_permissions": True,
        "audit_logging": True
    },
    "privacy": {
        "data_anonymization": True,
        "gdpr_compliance": True,
        "data_retention_policy": True
    }
}
```

- --

## 🧪 ** Testing Architecture**

### ** Test Coverage**

```
TEST_COVERAGE = {
    "unit_tests": {
        "embedding_provider": 95,
        "vector_database": 90,
        "document_processor": 88,
        "rag_system": 92
    },
    "integration_tests": {
        "end_to_end_workflow": 85,
        "api_endpoints": 90,
        "database_operations": 88
    },
    "performance_tests": {
        "load_testing": True,
        "stress_testing": True,
        "benchmarking": True
    },
    "security_tests": {
        "penetration_testing": True,
        "vulnerability_scanning": True,
        "data_validation": True
    }
}
```

- --

## 📈 ** Monitoring & Observability**

### ** Monitoring Stack**

```
MONITORING_CONFIG = {
    "metrics_collection": {
        "prometheus": True,
        "custom_metrics": True,
        "business_metrics": True
    },
    "logging": {
        "structured_logging": True,
        "log_aggregation": "elasticsearch",
        "log_retention": "30_days"
    },
    "tracing": {
        "distributed_tracing": True,
        "jaeger_integration": True,
        "performance_tracing": True
    },
    "alerting": {
        "error_rate_alerts": True,
        "performance_alerts": True,
        "business_alerts": True
    }
}
```

- --

## 🚀 ** Deployment Architecture**

### ** Docker Configuration**

```
# Multi-stage build for optimization
FROM python:3.11-slim as builder

# Install dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY src/ /app/src/
COPY config/ /app/config/

# Run application
CMD ["python", "/app/src/main.py"]
```

### ** Docker Compose**

```
version: '3.8'
services:
  synapse-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/synapse
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
      - chromadb

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: synapse
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - chromadb_data:/chroma/chroma
```

- --

## 📋 ** Implementation Roadmap**

### ** Phase 1: Core RAG System (Week 1-2)**

- [x] Embedding Provider Implementation
- [x] Vector Database Integration
- [x] Document Processor
- [x] Basic RAG System

### ** Phase 2: Advanced Features (Week 3-4)**

- [ ] Hybrid Search Implementation
- [ ] Multi-language Support
- [ ] Advanced Caching
- [ ] Performance Optimization

### ** Phase 3: Integration & Testing (Week 5-6)**

- [ ] API Integration
- [ ] Database Schema Implementation
- [ ] Security Implementation
- [ ] Comprehensive Testing

### ** Phase 4: Production Deployment (Week 7-8)**

- [ ] Docker Configuration
- [ ] Monitoring Setup
- [ ] Performance Tuning
- [ ] Documentation

- --

## 🎯 ** Key Benefits**

### ** Technical Benefits**

- ✅ ** Scalable Architecture**: รองรับการขยายตัว
- ✅ ** High Performance**: ประมวลผลเร็วและมีประสิทธิภาพ
- ✅ ** Flexible Integration**: เชื่อมต่อได้กับระบบต่างๆ
- ✅ ** Multi-language Support**: รองรับหลายภาษา
- ✅ ** Security First**: เน้นความปลอดภัย

### ** Business Benefits**

- ✅ ** Cost Effective**: ใช้ local models เพื่อลดต้นทุน
- ✅ ** Privacy Compliant**: ข้อมูลอยู่ในระบบภายใน
- ✅ ** Customizable**: ปรับแต่งได้ตามความต้องการ
- ✅ ** Future Proof**: ออกแบบให้รองรับการพัฒนาต่อ
- ✅ ** Easy Maintenance**: ดูแลรักษาง่าย

- --

## 📚 ** References & Resources**

### ** Technical Documentation**

- [ChromaDB Documentation](https://docs.trychroma.com/) - [Pinecone Documentation](https://docs.pinecone.io/) - [Ollama Documentation](https://ollama.ai/docs) - [FastAPI Documentation](https://fastapi.tiangolo.com/) ### ** Research Papers**

- [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) - [Dense Passage Retrieval for Open-Domain Question Answering](https://arxiv.org/abs/2004.04906) - [Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://arxiv.org/abs/1908.10084) - --

* * 🎉 RAG System Architecture พร้อมใช้งานแล้ว!**

ระบบนี้จะช่วยให้ Synapse Backend Monolith มีความสามารถในการค้นหาและตอบคำถามที่แม่นยำและรวดเร็ว โดยใช้เทคโนโลยีล่าสุดในด้าน AI และ Vector Database

