"""
FastAPI Server for Local RAG Service
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from local_rag_service import LocalRAGService

# Initialize FastAPI app
app = FastAPI(
    title="Chonost Local RAG API",
    description="Local RAG Service for Chonost Desktop App",
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

# Initialize RAG service
rag_service = LocalRAGService()

# Pydantic models
class DocumentRequest(BaseModel):
    file_path: str
    content: str
    title: Optional[str] = None
    type: str = "text"

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    file_path: str
    title: str
    content: str
    chunk_index: int
    similarity: float

class DocumentInfo(BaseModel):
    id: int
    title: str
    type: str
    chunks: int
    updated_at: str

class RAGInfo(BaseModel):
    total_documents: int
    total_chunks: int
    documents: dict

# API Routes
@app.get("/")
async def root():
    return {"message": "Chonost Local RAG API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "local-rag"}

@app.get("/api/rag/info", response_model=RAGInfo)
async def get_rag_info():
    """Get RAG system information"""
    try:
        info = rag_service.get_document_info()
        return RAGInfo(**info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/documents", response_model=List[DocumentInfo])
async def get_documents():
    """Get all documents"""
    try:
        info = rag_service.get_document_info()
        documents = []
        for file_path, doc_info in info['documents'].items():
            documents.append(DocumentInfo(
                id=doc_info['id'],
                title=doc_info['title'],
                type=doc_info['type'],
                chunks=doc_info['chunks'],
                updated_at=doc_info['updated_at']
            ))
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/documents")
async def add_document(request: DocumentRequest):
    """Add a document to the RAG system"""
    try:
        success = rag_service.add_document(
            file_path=request.file_path,
            content=request.content,
            title=request.title,
            doc_type=request.type
        )
        if success:
            return {"message": "Document added successfully", "file_path": request.file_path}
        else:
            raise HTTPException(status_code=400, detail="Failed to add document")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/rag/documents/{file_path}")
async def delete_document(file_path: str):
    """Delete a document from the RAG system"""
    try:
        success = rag_service.delete_document(file_path)
        if success:
            return {"message": "Document deleted successfully", "file_path": file_path}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rag/search", response_model=List[SearchResult])
async def search_documents(request: SearchRequest):
    """Search for documents"""
    try:
        results = rag_service.search(request.query, request.limit)
        return [SearchResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rag/search")
async def search_documents_get(query: str, limit: int = 5):
    """Search for documents (GET method)"""
    try:
        results = rag_service.search(query, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoints
@app.post("/api/rag/test/add-sample")
async def add_sample_documents():
    """Add sample documents for testing"""
    try:
        sample_docs = [
            {
                "file_path": "sample1.md",
                "content": "Chonost is an intelligent writing platform that combines AI with creative tools. It features The All-Seeing Eye for file indexing, The Forge for code execution, and The Trinity Layout for seamless user experience.",
                "title": "Chonost Overview",
                "type": "markdown"
            },
            {
                "file_path": "sample2.md",
                "content": "The Trinity Layout consists of three main areas: Left Sidebar (Knowledge Explorer), Main Content (Editor/Whiteboard), and Right Sidebar (Assistant Panel). This design provides a seamless workflow for creative writing.",
                "title": "The Trinity Layout",
                "type": "markdown"
            },
            {
                "file_path": "sample3.md",
                "content": "The All-Seeing Eye is the file indexing system that automatically scans and indexes all files in the project. It uses advanced NLP techniques to extract entities and create searchable embeddings.",
                "title": "The All-Seeing Eye",
                "type": "markdown"
            }
        ]
        
        added_count = 0
        for doc in sample_docs:
            success = rag_service.add_document(**doc)
            if success:
                added_count += 1
        
        return {
            "message": f"Added {added_count} sample documents",
            "total_documents": rag_service.get_document_info()['total_documents']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
