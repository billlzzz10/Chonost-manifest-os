# 🎯 Chonost Unified Ecosystem - Project Structure

## 📋 Overview

การรวม Chonost Ecosystem ที่ประกอบด้วย:
- **chonost-app** (Frontend Desktop App)
- **chonost-mcp** (MCP Platform & AI Tools)

## 🗂️ Unified Project Structure

```
chonost-unified/
├── 📁 frontend/                 # Main Frontend App (chonost-app)
│   ├── 📁 src/
│   │   ├── 📁 components/
│   │   │   ├── 📁 Layout/       # Trinity Layout Components
│   │   │   ├── 📁 KnowledgeExplorer/
│   │   │   ├── 📁 AssistantPanel/
│   │   │   └── 📁 Editor/
│   │   ├── 📁 services/         # Frontend Services
│   │   │   ├── 📄 aiService.ts
│   │   │   ├── 📄 mcpService.ts # MCP Integration
│   │   │   └── 📄 ragService.ts
│   │   ├── 📁 types/
│   │   └── 📄 App.tsx
│   ├── 📄 package.json
│   ├── 📄 vite.config.ts
│   └── 📄 tauri.conf.json       # Desktop App Config
│
├── 📁 backend/                  # Backend Services
│   ├── 📁 mcp/                  # MCP Platform (chonost-mcp)
│   │   ├── 📁 services/
│   │   │   ├── 📁 orchestrator/
│   │   │   ├── 📁 embedding/
│   │   │   └── 📁 rag/
│   │   ├── 📁 tools/
│   │   ├── 📁 agents/
│   │   └── 📁 config/
│   ├── 📁 app/                  # Main App Backend
│   │   ├── 📁 routes/
│   │   │   ├── 📄 api.py        # REST API
│   │   │   ├── 📄 websocket.py  # Real-time
│   │   │   └── 📄 mcp.py        # MCP Integration
│   │   ├── 📁 models/
│   │   └── 📁 services/
│   ├── 📄 main.py               # FastAPI App
│   ├── 📄 requirements.txt
│   └── 📄 pyproject.toml
│
├── 📁 shared/                   # Shared Code & Types
│   ├── 📁 types/
│   │   ├── 📄 mcp.ts
│   │   ├── 📄 mcp.py
│   │   └── 📄 common.ts
│   ├── 📁 utils/
│   └── 📁 config/
│
├── 📁 docs/                     # Documentation
│   ├── 📄 README.md
│   ├── 📄 API_DOCS.md
│   ├── 📄 MCP_GUIDE.md
│   └── 📄 DEPLOYMENT.md
│
├── 📁 scripts/                  # Build & Deploy Scripts
│   ├── 📄 build_desktop.py
│   ├── 📄 setup_environment.py
│   ├── 📄 deploy.py
│   └── 📄 test_integration.py
│
├── 📁 docker/                   # Docker Configuration
│   ├── 📄 docker-compose.yml
│   ├── 📄 Dockerfile.frontend
│   └── 📄 Dockerfile.backend
│
├── 📁 .github/                  # CI/CD
│   └── 📁 workflows/
│
├── 📄 package.json              # Root package.json (monorepo)
├── 📄 pyproject.toml            # Root Python config
├── 📄 docker-compose.yml        # Full system orchestration
└── 📄 README.md
```

## 🔗 Integration Points

### 1. **MCP ↔ Frontend Communication**

```typescript
// frontend/src/services/mcpService.ts
export class MCPService {
  private wsConnection: WebSocket;

  async connectToMCPServer() {
    // Connect to MCP WebSocket server
  }

  async callTool(toolName: string, params: any) {
    // Call MCP tools from frontend
  }

  async getAvailableTools() {
    // Get list of available MCP tools
  }
}
```

```python
# backend/app/routes/mcp.py
@app.websocket("/ws/mcp")
async def mcp_websocket(websocket: WebSocket):
    await websocket.accept()

    # Handle MCP tool calls from frontend
    while True:
        data = await websocket.receive_json()
        result = await mcp_orchestrator.call_tool(data)
        await websocket.send_json(result)
```

### 2. **Backend ↔ MCP Integration**

```python
# backend/mcp/services/orchestrator/main.py
from mcp_ai_orchestrator import MCPServer

class MCPIntegration:
    def __init__(self):
        self.mcp_server = MCPServer()

    async def call_tool(self, tool_name: str, params: dict):
        return await self.mcp_server.call_tool(tool_name, params)

    async def get_available_tools(self):
        return await self.mcp_server.list_tools()
```

### 3. **Frontend State Management**

```typescript
// frontend/src/store/appStore.ts
interface AppState {
  currentView: 'editor' | 'whiteboard';
  mcpTools: MCPTool[];
  knowledgeNodes: KnowledgeNode[];
  aiMessages: AIMessage[];
}

export const useAppStore = create<AppState>((set, get) => ({
  // App state
  currentView: 'editor',

  // MCP integration
  mcpTools: [],
  async loadMCPTools() {
    const tools = await mcpService.getAvailableTools();
    set({ mcpTools: tools });
  },

  // Knowledge management
  knowledgeNodes: [],
  async loadKnowledgeGraph() {
    const nodes = await knowledgeService.getGraph();
    set({ knowledgeNodes: nodes });
  },

  // AI chat
  aiMessages: [],
  async sendMessage(message: string) {
    const response = await aiService.sendMessage(message);
    set(state => ({
      aiMessages: [...state.aiMessages, response]
    }));
  }
}));
```

## 🚀 Build & Deployment Strategy

### 1. **Development Setup**

```bash
# Install all dependencies
npm install                    # Root dependencies
cd frontend && npm install     # Frontend
cd ../backend && pip install -e .  # Backend

# Start development servers
npm run dev:all               # Start all services
```

### 2. **Desktop App Build**

```bash
# Build desktop application
cd frontend
npm run build
npm run tauri build

# Output: dist/ and src-tauri/target/release/
```

### 3. **Docker Deployment**

```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - mcp-server

  mcp-server:
    build: ./backend/mcp
    ports:
      - "8080:8080"
```

## 🔧 Configuration Management

### 1. **Environment Variables**

```bash
# .env
# Frontend
VITE_API_URL=http://localhost:8000
VITE_MCP_WS_URL=ws://localhost:8080

# Backend
DATABASE_URL=postgresql://localhost/chonost
REDIS_URL=redis://localhost:6379
OLLAMA_URL=http://localhost:11434

# MCP
MCP_SERVER_PORT=8080
MCP_TOOLS_PATH=./tools
```

### 2. **Shared Configuration**

```typescript
// shared/config/common.ts
export const CONFIG = {
  API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  MCP_WS_URL: import.meta.env.VITE_MCP_WS_URL || 'ws://localhost:8080',
  OLLAMA_URL: import.meta.env.VITE_OLLAMA_URL || 'http://localhost:11434'
};
```

```python
# shared/config/common.py
import os

CONFIG = {
    'API_BASE_URL': os.getenv('API_BASE_URL', 'http://localhost:8000'),
    'MCP_WS_URL': os.getenv('MCP_WS_URL', 'ws://localhost:8080'),
    'OLLAMA_URL': os.getenv('OLLAMA_URL', 'http://localhost:11434')
}
```

## 📊 Development Workflow

### 1. **Local Development**

```bash
# Start all services
npm run dev:all

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# MCP Server: http://localhost:8080
# Ollama: http://localhost:11434
```

### 2. **Testing**

```bash
# Test all components
npm run test:all

# Test MCP integration
npm run test:mcp

# Test end-to-end
npm run test:e2e
```

### 3. **Building**

```bash
# Build all components
npm run build:all

# Build desktop app
npm run build:desktop

# Build Docker images
npm run build:docker
```

## 🎯 Key Integration Features

### 1. **Real-time MCP Tool Execution**

- Frontend can call MCP tools directly
- Real-time progress updates
- Error handling and retry logic

### 2. **Unified Knowledge Graph**

- Shared knowledge between MCP and frontend
- Real-time synchronization
- Cross-platform knowledge management

### 3. **AI Agent Integration**

- MCP agents accessible from frontend
- Custom agent creation and management
- Agent conversation history

### 4. **Plugin Architecture**

- MCP tools as plugins
- Frontend extensions
- Custom integrations

## 🔄 Migration Strategy

### Phase 1: Project Setup
- [ ] Create unified project structure
- [ ] Merge package.json files
- [ ] Merge Python dependencies
- [ ] Setup monorepo configuration

### Phase 2: Code Integration
- [ ] Move FileSystemMCP to backend/mcp/
- [ ] Move chonost-app to frontend/
- [ ] Create shared types and utilities
- [ ] Setup communication protocols

### Phase 3: Service Integration
- [ ] Integrate MCP orchestrator
- [ ] Connect frontend to MCP services
- [ ] Setup WebSocket communication
- [ ] Implement tool calling from frontend

### Phase 4: Testing & Deployment
- [ ] Test integrated system
- [ ] Setup CI/CD pipeline
- [ ] Create deployment scripts
- [ ] Document integration points

## 🎉 Benefits of Unified Architecture

1. **Simplified Development**: Single repository, unified tooling
2. **Better Integration**: Direct communication between components
3. **Consistent Architecture**: Shared patterns and conventions
4. **Easier Deployment**: Unified build and deployment process
5. **Enhanced Collaboration**: Clear component boundaries and responsibilities

---

**Status**: 🏗️ **Planning Phase** - Ready for implementation
**Next Step**: Create unified project structure and begin migration
