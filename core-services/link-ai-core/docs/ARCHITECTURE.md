# 🏗️ Chonost Ecosystem - System Architecture v2.1

## 🎯 Architecture Overview

Chonost Ecosystem ใช้สถาปัตยกรรมแบบ **Modular Microservices** ที่ประกอบด้วย 2 Repository หลักตาม **Master Blueprint v2.1**:

- **`chonost-app`**: Desktop Application (Tauri + Sidecar)
- **`chonost-mcp`**: Extensible Tool Platform

## 🔑 Core Concepts Architecture

### The All-Seeing Eye Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    The All-Seeing Eye                       │
├─────────────────────────────────────────────────────────────┤
│  File System Watcher (watchdog)                             │
│  ├── Real-time file monitoring                              │
│  ├── Change detection and notification                      │
│  └── Event-driven architecture                              │
├─────────────────────────────────────────────────────────────┤
│  Metadata Indexing System                                   │
│  ├── File metadata extraction                               │
│  ├── Content analysis and categorization                    │
│  └── Search index generation                                │
├─────────────────────────────────────────────────────────────┤
│  Project Manifest                                           │
│  ├── Project structure analysis                             │
│  ├── Dependency mapping                                     │
│  └── Configuration management                               │
└─────────────────────────────────────────────────────────────┘
```

### The Forge Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        The Forge                            │
├─────────────────────────────────────────────────────────────┤
│  Jupyter Kernel Manager                                     │
│  ├── Kernel lifecycle management                            │
│  ├── Code execution pipeline                                │
│  └── Result caching and optimization                        │
├─────────────────────────────────────────────────────────────┤
│  Docker Container Manager                                   │
│  ├── Container orchestration                                │
│  ├── Resource management                                    │
│  └── Security isolation                                     │
├─────────────────────────────────────────────────────────────┤
│  Code Interpreter                                           │
│  ├── Multi-language support                                 │
│  ├── Interactive execution                                  │
│  └── Error handling and recovery                            │
└─────────────────────────────────────────────────────────────┘
```

### The Trinity Layout Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    The Trinity Layout                       │
├─────────────────┬───────────────────────────┬───────────────┤
│   Left Panel    │      Center Panel         │  Right Panel  │
│   (Explorer)    │   (Editor/Whiteboard)     │ (Chat/Tools)  │
├─────────────────┼───────────────────────────┼───────────────┤
│ • File Browser  │ • Code Editor             │ • AI Chat     │
│ • Project Tree  │ • Excalidraw Canvas       │ • Tool Panel  │
│ • Search        │ • Split View Manager      │ • Context     │
│ • Categories    │ • Real-time Collaboration │ • Execution   │
└─────────────────┴───────────────────────────┴───────────────┘
```

### The Living Dictionary Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                  The Living Dictionary                      │
├─────────────────────────────────────────────────────────────┤
│  Document Processing Pipeline                               │
│  ├── Document ingestion and parsing                        │
│  ├── Content extraction and cleaning                       │
│  └── Metadata enrichment                                    │
├─────────────────────────────────────────────────────────────┤
│  Vector Database (Qdrant)                                   │
│  ├── Embedding storage and indexing                         │
│  ├── Semantic search capabilities                           │
│  └── Similarity matching                                    │
├─────────────────────────────────────────────────────────────┤
│  RAG (Retrieval-Augmented Generation)                       │
│  ├── Context retrieval                                      │
│  ├── Knowledge synthesis                                    │
│  └── Response generation                                    │
└─────────────────────────────────────────────────────────────┘
```

### MCP (Master Control Program) Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                Master Control Program                       │
├─────────────────────────────────────────────────────────────┤
│  Tool Registry & Manager                                    │
│  ├── Dynamic tool registration                              │
│  ├── Tool discovery and loading                             │
│  └── Version compatibility management                       │
├─────────────────────────────────────────────────────────────┤
│  Communication Hub                                          │
│  ├── WebSocket server                                       │
│  ├── Message routing                                         │
│  └── Protocol translation                                    │
├─────────────────────────────────────────────────────────────┤
│  Service Orchestration                                      │
│  ├── Service discovery                                       │
│  ├── Load balancing                                          │
│  └── Fault tolerance                                         │
└─────────────────────────────────────────────────────────────┘
```

### AI Agents Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      AI Agents                              │
├─────────────────────────────────────────────────────────────┤
│  Agent Orchestrator                                         │
│  ├── Task distribution                                       │
│  ├── Agent coordination                                      │
│  └── Workflow management                                     │
├─────────────────────────────────────────────────────────────┤
│  Specialized Agents                                         │
│  ├── Code Analysis Agent                                    │
│  ├── Documentation Agent                                    │
│  ├── Project Management Agent                               │
│  └── Learning Agent                                         │
├─────────────────────────────────────────────────────────────┤
│  Safety & Control                                           │
│  ├── Autonomy limits                                         │
│  ├── Safety protocols                                        │
│  └── Human oversight                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Chonost Ecosystem                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   chonost-app   │    │         chonost-mcp             │ │
│  │  (Desktop App)  │◄──►│     (Tool Platform)             │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              External Services                          │ │
│  │  • AI Models (LiteLLM)                                  │ │
│  │  • Vector DB (Qdrant)                                   │ │
│  │  • Task Queue (Dramatiq + Redis)                        │ │
│  │  • Jupyter Kernels                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### chonost-app Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    chonost-app                              │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React + Vite + TypeScript)                      │
│  ├── Trinity Layout Components                              │
│  ├── State Management (Zustand/Redux)                      │
│  ├── UI Components (TailwindCSS)                           │
│  └── Excalidraw Integration                                 │
├─────────────────────────────────────────────────────────────┤
│  Tauri Backend (Rust)                                       │
│  ├── File System Access                                     │
│  ├── Native OS Integration                                  │
│  ├── Security & Permissions                                 │
│  └── Performance Optimization                               │
├─────────────────────────────────────────────────────────────┤
│  Sidecar (FastAPI + Python)                                 │
│  ├── AI Model Management (LiteLLM)                          │
│  ├── Vector Operations (Qdrant)                             │
│  ├── Task Queue (Dramatiq + Redis)                          │
│  └── Jupyter Integration                                    │
└─────────────────────────────────────────────────────────────┘
```

### chonost-mcp Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    chonost-mcp                              │
├─────────────────────────────────────────────────────────────┤
│  MCP Server (FastAPI + WebSockets)                          │
│  ├── Tool Registration & Discovery                          │
│  ├── Message Routing & Protocol Translation                 │
│  ├── Authentication & Authorization                         │
│  └── Error Handling & Recovery                              │
├─────────────────────────────────────────────────────────────┤
│  Tool Management                                            │
│  ├── Dynamic Tool Loading                                   │
│  ├── Tool Validation & Testing                              │
│  ├── Version Compatibility                                  │
│  └── Tool Marketplace                                       │
├─────────────────────────────────────────────────────────────┤
│  Service Integration                                        │
│  ├── External API Connectors                                │
│  ├── Third-party Service Integration                        │
│  ├── Custom Tool Development Kit                            │
│  └── Plugin System                                          │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Architecture

### File System Data Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ File System │───►│ All-Seeing  │───►│ Metadata    │
│   Changes   │    │    Eye      │    │  Index      │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ Trinity     │
                   │  Layout     │
                   └─────────────┘
```

### AI Processing Data Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ User Input  │───►│ Living      │───►│ Vector DB   │
│             │    │ Dictionary  │    │ (Qdrant)    │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ AI Agents   │
                   │             │
                   └─────────────┘
```

### Tool Execution Data Flow
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Tool        │───►│ MCP Server  │───►│ Tool        │
│ Request     │    │             │    │ Execution   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │ Results     │
                   │ Processing  │
                   └─────────────┘
```

## 🗄️ Database Architecture

### SQLite Schema (chonost-app)
```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Files table
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT,
    size INTEGER,
    last_modified TIMESTAMP,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    title TEXT,
    messages JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tools table
CREATE TABLE tools (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    uri TEXT UNIQUE NOT NULL,
    version TEXT,
    description TEXT,
    schema JSON,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Vector Database Schema (Qdrant)
```python
# Collections for The Living Dictionary
collections = {
    "documents": {
        "id": "uuid",
        "content": "text",
        "embedding": "vector(1536)",  # OpenAI embedding dimension
        "metadata": "json",
        "created_at": "timestamp"
    },
    "code_snippets": {
        "id": "uuid", 
        "content": "text",
        "embedding": "vector(1536)",
        "language": "string",
        "project_id": "uuid",
        "metadata": "json"
    },
    "conversations": {
        "id": "uuid",
        "content": "text", 
        "embedding": "vector(1536)",
        "context": "json",
        "created_at": "timestamp"
    }
}
```

## 🔐 Security Architecture

### Authentication & Authorization
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Authentication                                             │
│  ├── OAuth 2.0 + JWT                                        │
│  ├── Multi-factor authentication                            │
│  └── Session management                                      │
├─────────────────────────────────────────────────────────────┤
│  Authorization                                               │
│  ├── Role-based access control (RBAC)                       │
│  ├── Permission-based access control (PBAC)                 │
│  └── Resource-level permissions                             │
├─────────────────────────────────────────────────────────────┤
│  Data Protection                                            │
│  ├── End-to-end encryption                                  │
│  ├── Data at rest encryption                                │
│  └── Secure communication (HTTPS/WSS)                       │
└─────────────────────────────────────────────────────────────┘
```

### Security Considerations
- **Input Validation**: Strict validation for all user inputs
- **SQL Injection Prevention**: Parameterized queries
- **XSS Prevention**: Content Security Policy (CSP)
- **CSRF Protection**: Token-based CSRF protection
- **Rate Limiting**: API rate limiting and throttling
- **Audit Logging**: Comprehensive security event logging

## 🚀 Performance Architecture

### Caching Strategy
```
┌─────────────────────────────────────────────────────────────┐
│                    Caching Layer                            │
├─────────────────────────────────────────────────────────────┤
│  Application Cache (Redis)                                  │
│  ├── Session storage                                        │
│  ├── API response caching                                   │
│  └── Tool execution results                                 │
├─────────────────────────────────────────────────────────────┤
│  Browser Cache                                              │
│  ├── Static assets                                          │
│  ├── API responses                                          │
│  └── User preferences                                       │
├─────────────────────────────────────────────────────────────┤
│  CDN Cache                                                  │
│  ├── Global content distribution                             │
│  ├── Static file optimization                               │
│  └── Geographic optimization                                │
└─────────────────────────────────────────────────────────────┘
```

### Performance Optimization
- **Lazy Loading**: Components and modules loaded on demand
- **Code Splitting**: Bundle optimization for faster loading
- **Database Indexing**: Optimized queries and indexing
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Non-blocking operations
- **Resource Compression**: Gzip/Brotli compression

## 🔧 Deployment Architecture

### Development Environment
```
┌─────────────────────────────────────────────────────────────┐
│                Development Environment                      │
├─────────────────────────────────────────────────────────────┤
│  Local Development                                          │
│  ├── Docker Compose                                         │
│  ├── Hot reloading                                          │
│  ├── Debug tools                                            │
│  └── Local databases                                        │
├─────────────────────────────────────────────────────────────┤
│  CI/CD Pipeline                                             │
│  ├── Automated testing                                       │
│  ├── Code quality checks                                     │
│  ├── Security scanning                                       │
│  └── Automated deployment                                    │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment
```
┌─────────────────────────────────────────────────────────────┐
│                Production Environment                       │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer (Nginx)                                      │
│  ├── SSL termination                                        │
│  ├── Request routing                                         │
│  ├── Rate limiting                                           │
│  └── Health checks                                           │
├─────────────────────────────────────────────────────────────┤
│  Application Servers                                        │
│  ├── Multiple instances                                      │
│  ├── Auto-scaling                                            │
│  ├── Health monitoring                                       │
│  └── Failover support                                        │
├─────────────────────────────────────────────────────────────┤
│  Database Layer                                              │
│  ├── Primary database                                        │
│  ├── Read replicas                                           │
│  ├── Backup systems                                          │
│  └── Disaster recovery                                       │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Monitoring & Observability

### Monitoring Stack
```
┌─────────────────────────────────────────────────────────────┐
│                Monitoring & Observability                   │
├─────────────────────────────────────────────────────────────┤
│  Application Monitoring                                     │
│  ├── Prometheus metrics                                      │
│  ├── Grafana dashboards                                      │
│  ├── Performance tracking                                    │
│  └── Error tracking                                          │
├─────────────────────────────────────────────────────────────┤
│  Logging                                                     │
│  ├── Structured logging                                      │
│  ├── Log aggregation (ELK)                                   │
│  ├── Log analysis                                            │
│  └── Alerting                                                │
├─────────────────────────────────────────────────────────────┤
│  Tracing                                                     │
│  ├── Distributed tracing                                     │
│  ├── Request flow tracking                                   │
│  ├── Performance profiling                                   │
│  └── Bottleneck identification                               │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Integration Architecture

### External Service Integration
```
┌─────────────────────────────────────────────────────────────┐
│                External Integrations                        │
├─────────────────────────────────────────────────────────────┤
│  AI Services                                                 │
│  ├── OpenAI API                                              │
│  ├── Anthropic Claude                                        │
│  ├── Local AI models                                         │
│  └── Custom model endpoints                                  │
├─────────────────────────────────────────────────────────────┤
│  Development Tools                                           │
│  ├── Git providers (GitHub, GitLab)                         │
│  ├── CI/CD platforms                                         │
│  ├── Code quality tools                                      │
│  └── Testing frameworks                                      │
├─────────────────────────────────────────────────────────────┤
│  Productivity Tools                                          │
│  ├── Notion API                                              │
│  ├── Slack integration                                       │
│  ├── Email services                                          │
│  └── Calendar integration                                    │
└─────────────────────────────────────────────────────────────┘
```

---

**หมายเหตุ**: สถาปัตยกรรมนี้ได้รับการออกแบบให้มีความยืดหยุ่นและขยายได้ตามความต้องการของโปรเจกต์ และสามารถปรับเปลี่ยนได้ตามการพัฒนาของเทคโนโลยีและความต้องการของผู้ใช้
