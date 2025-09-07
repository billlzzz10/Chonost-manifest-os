# 🚀 Chonost Unified Ecosystem v2.2

**The Ultimate Creative Workspace with AI Integration**

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/chonost/chonost-unified)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

Chonost Unified Ecosystem เป็นระบบสร้างสรรค์ที่มี UX ไร้รอยต่อ ประกอบด้วย:

- **🎨 Frontend Desktop App**: React + TypeScript + Tauri
- **🤖 MCP Platform**: Advanced AI Tools & Agents
- **🔄 Real-time Integration**: WebSocket communication
- **📚 Knowledge Management**: RAG-powered search

## 🗂️ Project Structure

```
chonost-unified/
├── frontend/                 # Desktop App (React + Tauri)
│   ├── src/
│   │   ├── components/       # Trinity Layout Components
│   │   ├── services/         # API & MCP Services
│   │   └── types/           # TypeScript Types
│   └── tauri.conf.json      # Desktop App Config
│
├── backend/                  # FastAPI Backend
│   ├── main.py              # Unified API Server
│   ├── mcp/                 # MCP Platform Integration
│   └── requirements.txt     # Python Dependencies
│
├── shared/                   # Shared Code & Types
│   ├── types/               # TypeScript & Python Types
│   ├── utils/               # Common Utilities
│   └── config/              # Shared Configuration
│
└── scripts/                  # Build & Deploy Scripts
    ├── build_desktop.py     # Desktop App Builder
    └── test_integration.py  # Integration Tests
```

## 🚀 Quick Start

### Prerequisites

```bash
# Node.js 18+ & npm
node --version  # v18.0.0 or higher
npm --version   # 8.0.0 or higher

# Python 3.8+
python --version  # 3.8.0 or higher

# Rust (for Tauri)
cargo --version  # 1.70.0 or higher
```

### Installation

```bash
# Clone repository
git clone https://github.com/chonost/chonost-unified.git
cd chonost-unified

# Install all dependencies
npm install                    # Root dependencies
npm run install:frontend       # Frontend dependencies
npm run install:backend        # Backend dependencies

# Or install everything at once
npm run install:all
```

### Development

```bash
# Start all services
npm run dev:all

# Services will be available at:
# - Frontend: http://localhost:1420
# - Backend API: http://localhost:8000
# - MCP WebSocket: ws://localhost:8000/ws
```

## 🎯 Key Features

### 1. **Trinity Layout UI**
- **ซ้าย**: Knowledge Explorer (File/Project Browser)
- **กลาง**: Editor/Whiteboard (Code Editor + Excalidraw)
- **ขวา**: AI Assistant Panel (Chat + Tool Panel)

### 2. **Advanced MCP Integration**
- **16 Tool Categories**: Filesystem, GitHub, Notion, Slack, etc.
- **Real-time Communication**: WebSocket-based tool execution
- **AI Enhancement**: Semantic search, pattern recognition
- **Parallel Processing**: Multi-worker execution

### 3. **AI-Powered Features**
- **RAG Search**: Retrieval-Augmented Generation
- **Knowledge Graph**: Visual knowledge connections
- **Smart Code Analysis**: AI-powered code review
- **Intelligent Routing**: Optimal LLM model selection

### 4. **Desktop Application**
- **Native Performance**: Built with Tauri + Rust
- **Cross-platform**: Windows, macOS, Linux
- **Offline Support**: Local AI models via Ollama
- **System Integration**: File system access, notifications

## 🛠️ Development Commands

```bash
# Development
npm run dev                 # Start frontend dev server
npm run dev:backend         # Start backend server
npm run dev:all            # Start all services

# Building
npm run build              # Build all components
npm run build:desktop      # Build desktop app
npm run build:docker       # Build Docker images

# Testing
npm run test               # Run all tests
npm run test:integration   # Run integration tests
npm run lint               # Code linting

# Deployment
npm run docker:up          # Start with Docker
npm run clean              # Clean build artifacts
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Frontend
VITE_API_URL=http://localhost:8000
VITE_MCP_WS_URL=ws://localhost:8000

# Backend
DATABASE_URL=postgresql://localhost/chonost
REDIS_URL=redis://localhost:6379
OLLAMA_URL=http://localhost:11434

# MCP
MCP_SERVER_PORT=8000
MCP_TOOLS_PATH=./tools
```

### Shared Configuration

```typescript
// shared/config/common.ts
export const CONFIG = {
  API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  MCP_WS_URL: import.meta.env.VITE_MCP_WS_URL || 'ws://localhost:8000',
  OLLAMA_URL: import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434'
};
```

## 📡 API Endpoints

### Health & Info
```http
GET /health              # Health check
GET /api/info           # API information
```

### MCP Integration
```http
GET  /api/mcp/tools     # Get available tools
POST /api/mcp/call      # Execute tool
GET  /api/mcp/servers   # Server status
```

### Knowledge & RAG
```http
GET /api/rag/search     # RAG search
GET /api/knowledge/graph # Knowledge graph
```

### Real-time Communication
```websocket
/ws                     # WebSocket endpoint
```

## 🧪 Testing

### Unit Tests
```bash
# Frontend tests
npm run test:frontend

# Backend tests
npm run test:backend
```

### Integration Tests
```bash
# Test MCP integration
python scripts/test_integration.py

# Test end-to-end
npm run test:integration
```

### Manual Testing Checklist
- [ ] Frontend loads at http://localhost:1420
- [ ] Backend responds at http://localhost:8000/health
- [ ] MCP tools are available via /api/mcp/tools
- [ ] RAG search works via /api/rag/search
- [ ] WebSocket connection established
- [ ] Desktop app builds successfully

## 🚀 Deployment

### Desktop Application
```bash
# Build for current platform
npm run build:desktop

# Build for all platforms
npm run build:desktop -- --bundles all
```

### Docker Deployment
```bash
# Build images
npm run docker:build

# Start services
npm run docker:up

# Or use docker-compose directly
docker-compose up -d
```

### Production Environment
```bash
# Set production environment
export NODE_ENV=production

# Build optimized version
npm run build

# Start production server
npm run start:prod
```

## 🔧 Architecture

### Frontend Architecture
```
frontend/
├── Trinity Layout (3-panel system)
├── State Management (Zustand)
├── API Integration (Axios/Fetch)
├── MCP Service Layer
├── Component Library
└── Desktop Integration (Tauri)
```

### Backend Architecture
```
backend/
├── FastAPI Application
├── MCP Orchestrator
├── RAG Engine
├── Database Layer
├── WebSocket Server
└── AI Integration
```

### MCP Platform
```
mcp/
├── Tool Registry
├── Transport Layer
├── Connection Pool
├── AI Enhancement
└── Quality Control
```

## 🎨 UI/UX Guidelines

### Trinity Layout
- **Responsive Design**: Adaptive to screen sizes
- **Keyboard Shortcuts**: Vim-style navigation
- **Dark/Light Theme**: System preference detection
- **Accessibility**: WCAG 2.1 compliance

### Component Design
- **Atomic Design**: Molecules → Organisms → Templates
- **Consistent Spacing**: 8px grid system
- **Typography Scale**: 1.2 ratio progression
- **Color Palette**: Semantic color system

## 🔐 Security

### API Security
- **CORS Configuration**: Origin validation
- **Rate Limiting**: Request throttling
- **Authentication**: JWT tokens
- **Input Validation**: Pydantic schemas

### MCP Security
- **Tool Validation**: Safe tool execution
- **Sandboxing**: Isolated execution environment
- **Audit Logging**: Comprehensive logging
- **Permission System**: Granular access control

## 📚 Documentation

### Developer Documentation
- [API Documentation](./docs/API_DOCS.md)
- [MCP Guide](./docs/MCP_GUIDE.md)
- [Architecture](./docs/ARCHITECTURE.md)
- [Deployment](./docs/DEPLOYMENT.md)

### User Documentation
- [Getting Started](./docs/GETTING_STARTED.md)
- [User Guide](./docs/USER_GUIDE.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)

## 🤝 Contributing

### Development Setup
```bash
# Fork and clone
git clone https://github.com/your-username/chonost-unified.git
cd chonost-unified

# Setup development environment
npm run setup:dev

# Start development
npm run dev:all
```

### Code Standards
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Testing
npm run test

# Pre-commit hooks
npm run pre-commit
```

### Pull Request Process
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Tauri Team** for the amazing desktop app framework
- **FastAPI Team** for the excellent web framework
- **LangChain** for the powerful AI integration
- **Ollama** for local AI model support

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/chonost/chonost-unified/issues)
- **Discussions**: [GitHub Discussions](https://github.com/chonost/chonost-unified/discussions)
- **Email**: team@chonost.ai
- **Documentation**: https://docs.chonost.ai

---

**Made with ❤️ by the Chonost Team**

*Transforming ideas into reality with AI-powered creativity tools.*
