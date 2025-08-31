"""
Simple API Server for Testing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Chonost Simple API",
    description="Simple API for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple routes
@app.get("/")
async def root():
    return {"message": "Chonost Simple API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "simple-api"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working!", "data": "test"}

@app.get("/api/rag/info")
async def get_rag_info():
    total_chunks = sum(doc.get("chunks", 0) for doc in documents_storage.values())
    return {
        "total_documents": len(documents_storage),
        "total_chunks": total_chunks,
        "documents": documents_storage
    }

# Global storage for documents
documents_storage = {
    "doc_1.md": {
        "id": 1,
        "title": "Chonost Development Roadmap",
        "type": "markdown",
        "chunks": 15,
        "updated_at": "2025-09-01T03:11:59.519347"
    },
    "doc_2.md": {
        "id": 2,
        "title": "The Trinity Layout Design",
        "type": "markdown",
        "chunks": 8,
        "updated_at": "2025-09-01T03:10:30.123456"
    },
    "doc_3.md": {
        "id": 3,
        "title": "AI Integration Guide",
        "type": "markdown",
        "chunks": 12,
        "updated_at": "2025-09-01T03:09:15.789012"
    }
}

@app.post("/api/rag/documents")
async def add_document(document_data: dict):
    """Add a document to the RAG system"""
    try:
        file_path = document_data.get("file_path", "")
        title = document_data.get("title", "")
        content = document_data.get("content", "")
        doc_type = document_data.get("type", "text")
        
        # Add to storage
        documents_storage[file_path] = {
            "id": len(documents_storage) + 1,
            "title": title,
            "type": doc_type,
            "chunks": len(content.split()) // 100 + 1,  # Simple chunk calculation
            "updated_at": "2025-09-01T03:11:59.519347"
        }
        
        return {"message": "Document added successfully", "file_path": file_path}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/rag/search")
async def search_documents(query: str = "", limit: int = 5):
    # Mock search results
    mock_results = [
        {
            "file_path": "DEVELOPMENT_ROADMAP.md",
            "title": "Chonost Development Roadmap",
            "content": "Phase 2: Advanced AI & Background Services - The All-Seeing Eye for file indexing...",
            "chunk_index": 0,
            "similarity": 0.95
        },
        {
            "file_path": "The Trinity Layout Design.md",
            "title": "The Trinity Layout Design",
            "content": "The Trinity Layout consists of three main areas: Left Sidebar (Knowledge Explorer)...",
            "chunk_index": 1,
            "similarity": 0.87
        }
    ]
    
    # Filter based on query
    if query:
        filtered_results = [r for r in mock_results if query.lower() in r['title'].lower() or query.lower() in r['content'].lower()]
        return filtered_results[:limit]
    
    return mock_results[:limit]

if __name__ == "__main__":
    print("🚀 Starting Simple API Server...")
    print("📡 Server will be available at http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
