# 📚 API Documentation - Chonost Manuscript OS

## Overview
Chonost Manuscript OS v2.1.0 provides a comprehensive API for document management, AI integration, and creative writing tools. This documentation covers all available endpoints and their usage.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.chonost.com`

## Authentication
Most endpoints require authentication. Include your API key in the request headers:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Health Check
```http
GET /health
```
Returns the health status of the API server.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-01T00:00:00Z",
  "version": "2.1.0"
}
```

### RAG (Retrieval-Augmented Generation) API

#### Get RAG Information
```http
GET /api/rag/info
```
Returns information about the RAG system including document count and statistics.

**Response:**
```json
{
  "total_documents": 3,
  "total_chunks": 35,
  "documents": {
    "doc_1.md": {
      "id": 1,
      "title": "Chonost Development Roadmap",
      "type": "markdown",
      "chunks": 15,
      "updated_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### Search Documents
```http
GET /api/rag/search?query=your_search_query&limit=10
```
Search for documents using semantic search.

**Parameters:**
- `query` (required): Search query
- `limit` (optional): Maximum number of results (default: 10)

**Response:**
```json
{
  "query": "AI Integration",
  "results": [
    {
      "document_id": 1,
      "title": "AI Integration Guide",
      "content": "This guide covers...",
      "score": 0.95,
      "chunk_id": 5
    }
  ],
  "total_results": 1
}
```

#### Add Document
```http
POST /api/rag/documents
```
Add a new document to the RAG system.

**Request Body:**
```json
{
  "file_path": "path/to/document.md",
  "title": "Document Title",
  "content": "Document content...",
  "type": "markdown"
}
```

**Response:**
```json
{
  "message": "Document added successfully",
  "file_path": "path/to/document.md"
}
```

### Document Management API

#### List Documents
```http
GET /api/documents
```
Retrieve a list of all documents.

**Response:**
```json
{
  "documents": [
    {
      "id": "1",
      "title": "My Document",
      "content": "Document content...",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Document
```http
GET /api/documents/{id}
```
Retrieve a specific document by ID.

**Response:**
```json
{
  "id": "1",
  "title": "My Document",
  "content": "Document content...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Create Document
```http
POST /api/documents
```
Create a new document.

**Request Body:**
```json
{
  "title": "New Document",
  "content": "Document content..."
}
```

#### Update Document
```http
PUT /api/documents/{id}
```
Update an existing document.

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

#### Delete Document
```http
DELETE /api/documents/{id}
```
Delete a document.

### AI Integration API

#### Send Message
```http
POST /api/ai/chat
```
Send a message to the AI assistant.

**Request Body:**
```json
{
  "message": "Hello, how can you help me?",
  "context": "optional_context"
}
```

**Response:**
```json
{
  "response": "Hello! I'm here to help you with your writing and creative tasks.",
  "suggestions": [
    "Try using the whiteboard for brainstorming",
    "Search your documents for relevant content"
  ],
  "confidence": 0.95
}
```

#### Get Quick Actions
```http
GET /api/ai/quick-actions
```
Get available quick actions for the AI assistant.

**Response:**
```json
{
  "actions": [
    {
      "id": "summarize",
      "title": "Summarize Document",
      "description": "Create a summary of the current document"
    },
    {
      "id": "improve",
      "title": "Improve Writing",
      "description": "Suggest improvements for the current text"
    }
  ]
}
```

### File Management API

#### Upload File
```http
POST /api/files/upload
```
Upload a file to the system.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File data

**Response:**
```json
{
  "file_id": "123",
  "filename": "document.pdf",
  "size": 1024,
  "uploaded_at": "2024-01-01T00:00:00Z"
}
```

#### List Files
```http
GET /api/files
```
List all uploaded files.

**Response:**
```json
{
  "files": [
    {
      "id": "123",
      "filename": "document.pdf",
      "size": 1024,
      "uploaded_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Export/Import API

#### Export Document
```http
GET /api/export/{document_id}?format=pdf
```
Export a document in various formats.

**Parameters:**
- `format`: Export format (pdf, docx, md, txt)

**Response:**
- File download

#### Import Document
```http
POST /api/import
```
Import a document from various formats.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File data

**Response:**
```json
{
  "document_id": "456",
  "title": "Imported Document",
  "imported_at": "2024-01-01T00:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Invalid request parameters",
  "details": "Specific error details"
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "message": "Please provide valid API key"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "The requested resource does not exist"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

## Rate Limiting
- **Standard**: 100 requests per minute
- **Premium**: 1000 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @chonost/api-client
```

```javascript
import { ChonostClient } from '@chonost/api-client';

const client = new ChonostClient({
  apiKey: 'your-api-key',
  baseUrl: 'http://localhost:8000'
});

// Search documents
const results = await client.rag.search('AI Integration');

// Create document
const document = await client.documents.create({
  title: 'New Document',
  content: 'Content...'
});
```

### Python
```bash
pip install chonost-api
```

```python
from chonost_api import ChonostClient

client = ChonostClient(
    api_key='your-api-key',
    base_url='http://localhost:8000'
)

# Search documents
results = client.rag.search('AI Integration')

# Create document
document = client.documents.create(
    title='New Document',
    content='Content...'
)
```

## WebSocket API

For real-time features, connect to the WebSocket endpoint:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send message
ws.send(JSON.stringify({
  type: 'chat_message',
  content: 'Hello!'
}));
```

## WebSocket Events

### Chat Message
```json
{
  "type": "chat_message",
  "content": "Message content",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Document Update
```json
{
  "type": "document_update",
  "document_id": "123",
  "changes": {
    "title": "Updated Title"
  }
}
```

### System Notification
```json
{
  "type": "notification",
  "message": "System message",
  "level": "info"
}
```

## Testing

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Search documents
curl "http://localhost:8000/api/rag/search?query=AI"

# Add document
curl -X POST http://localhost:8000/api/rag/documents \
  -H "Content-Type: application/json" \
  -d '{"file_path":"test.md","title":"Test","content":"Content","type":"markdown"}'
```

### Using Postman
Import the following collection:
```json
{
  "info": {
    "name": "Chonost API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/health"
      }
    }
  ]
}
```

## Support

For API support and questions:
- **Email**: api-support@chonost.com
- **Documentation**: https://docs.chonost.com/api
- **GitHub**: https://github.com/chonost/chonost-api

## Changelog

### v2.1.0 (2025-09-01)
- **Enhanced RAG System**: Improved document indexing and search capabilities
- **Advanced AI Integration**: Enhanced chat functionality with context awareness
- **Comprehensive Security**: Added security guidelines and environment management
- **Project Configuration**: Complete setup of development tools and linting
- **Documentation Overhaul**: Updated API docs with current endpoints
- **Desktop App Focus**: Shifted to desktop-first approach with Tauri integration
- **Local Development**: Simplified local development with SQLite and file-based storage
- **UI/UX Improvements**: Enhanced Trinity Layout with view switching
- **Testing Infrastructure**: Added comprehensive testing scripts and automation
- **Version Management**: Added support for multiple language versions

### v2.0.0 (2025-08-30)
- **Major Architecture Update**: Restructured project for desktop-first approach
- **RAG Integration**: Implemented local RAG service with FastAPI backend
- **AI Services**: Added AI chat and knowledge management
- **UI Components**: Enhanced Editor, Whiteboard, and KnowledgeExplorer
- **Testing Framework**: Added automated testing and validation scripts
- **Documentation**: Comprehensive API documentation and guides

### v1.0.0 (2024-01-01)
- Initial API release
- RAG search functionality
- Document management
- AI chat integration
- File upload/download
- Export/import features
