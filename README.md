[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/billlzzz10-chonost-manifest-os-badge.png)](https://mseep.ai/app/billlzzz10-chonost-manifest-os)

# Chonost Manuscript OS

Chonost Manuscript OS is a comprehensive AI monorepo designed for advanced AI agent ecosystems, RAG pipelines, and desktop integrations. This project combines backend services, MCP servers, and desktop applications for seamless AI-driven manuscript management.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Rust (for Tauri desktop builds)
- Docker (for containerized services)

### Installation
```bash
# Clone the repository
git clone https://github.com/user/chonost.git
cd chonost

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt

# Start core services
docker-compose up -d
```
# Chonost Manuscript OS v2.1.0

An Intelligent Manuscript Management System.

This project has been reorganized for clarity and maintainability. For a complete overview, please see the documents in the `docs/` directory.

---

## 🚀 Getting Started

This guide will get you up and running with the Chonost Manuscript OS.

**Prerequisites:**
- Docker and Docker Compose
- Python 3.8+
- Node.js and npm (for frontend development)

**Installation:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/chonost-manuscript-os.git
    cd chonost-manuscript-os
    ```

2.  **Set up the environment:**
    -   Copy the `.env.example` file to `.env`.
    -   Run the main setup script to install dependencies and create necessary configurations:
        ```bash
        python core-services/link-ai-core/scripts/core/setup.py
        ```
    -   For detailed environment setup, see the [Environment Setup Guide](docs/ENV_SETUP_GUIDE.md).

3.  **Start all services:**
    ```bash
    docker-compose up -d
    ```

### Development
```bash
# Start MCP servers
npm run mcp:start

# Run backend services
python core-services/link-ai-core/main.py

# Start frontend development
npm run dev
```

## 🏗️ Architecture

### Core Components
- **MCP Servers**: Memory, Filesystem, Sequential Thinking, Context7
- **RAG Pipeline**: Enhanced retrieval-augmented generation with Notion integration
- **AI Agents**: Multi-agent orchestration with CrewAI and Ollama
- **Desktop Integration**: Tauri-based Nodition desktop application
- **Monitoring**: Grafana dashboards and alert systems

### Data Flow
1. **Notion Sync** → `scripts/notion.py` → Manuscript Vault
2. **RAG Processing** → Vector stores → AI responses
3. **Agent Orchestration** → MCP tools → Task execution
4. **Desktop Interface** → Nodition → User interaction

## 📱 Desktop Integration - Nodition

Nodition is the desktop companion for Chonost Manuscript OS, providing native desktop experience with Tauri.

### Features
- **Native Desktop UI**: Cross-platform (Windows/Mac/Linux) with Tauri
- **Notion Integration**: Real-time sync with manuscript vault via sidecar
- **RAG Health Checks**: Validation service for system monitoring
- **Sidecar Architecture**: Node.js backend with Python subprocess integration
- **Production Ready**: Bundled executables with system tray support

### Badges
[![Nodition Desktop](https://img.shields.io/badge/Nodition-Desktop%20Ready-brightgreen)](https://github.com/user/chonost/tree/main/nodition)
[![Tauri Build](https://img.shields.io/badge/Tauri-v1.5.0-blue)](https://tauri.app)
[![Notion Integration](https://img.shields.io/badge/Notion-API%20v1-yellow)](https://developers.notion.com)
[![Cross%20Platform](https://img.shields.io/badge/Windows-Mac-Linux-green)](https://tauri.app)

### Quick Start - Nodition
```bash
cd nodition
npm install
npx tauri dev  # Development mode
npx tauri build  # Production build
```

### Configuration
1. Set `NOTION_TOKEN` in `.env` for Notion API access
2. Configure `MANUSCRIPT_VAULT` path for data storage
3. Set `NOTION_DATABASE_ID` for target database sync

## 🔧 Core Services

### Link AI Core
- **AI Chat Interface**: Enhanced chat with memory and context
- **RAG System**: Complete retrieval-augmented generation pipeline
- **Notion AI Integration**: Seamless Notion data sync and processing

### MCP Ecosystem
- **Memory Server**: Knowledge graph and conversation memory
- **Filesystem Server**: Secure file operations and vault management
- **Sequential Thinking**: Advanced problem-solving with chain-of-thought

## 📊 Monitoring & Observability

- **Grafana Dashboards**: Real-time metrics and performance tracking
- **Alert System**: Automated notifications for system health
- **Logging**: Structured logs with correlation IDs

## 🛠️ Development Tools

### VSCode Extension
- **MCP Tools Provider**: Integrated MCP server access
- **Cursor Integration**: AI-powered code assistance
- **Tool Schema Management**: Dynamic tool discovery and usage

### Scripts
- **Vault Management**: Automated manuscript vault organization
- **Dataset Generation**: AI conversation and performance datasets
- **Quality Control**: Master quality assurance and validation

## 📈 Performance & Scale

- **Horizontal Scaling**: Kubernetes-ready with HPA configurations
- **Caching**: Redis integration for response caching
- **Load Balancing**: Multi-MCP server pooling and orchestration

## 🤝 Contributing

See our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tauri Team](https://tauri.app) - Desktop framework
- [Notion Developers](https://developers.notion.com) - API integration
- [Model Context Protocol](https://modelcontextprotocol.io) - AI agent communication
- [CrewAI](https://crewai.com) - Multi-agent orchestration

---

⭐ **Star us on GitHub** if you find this project useful!  
📢 **Join the conversation** in our [community discussions](https://github.com/user/chonost/discussions)
---

## 🧠 Core Concepts

This system is built on a set of core concepts that enable its modular and intelligent capabilities.

-   **MCP (Modular Component Protocol):** A protocol that allows different system components (servers) to communicate with each other in a standardized way. This enables loose coupling and independent development of tools. See `core-services/link-ai-core/mcp/` for the implementation.

-   **AI Orchestrator:** The central hub of the system. It receives requests, uses the MCP client to call the appropriate tools, and coordinates the flow of data between components. The orchestrator is implemented as a FastAPI server in `core-services/link-ai-core/main.py`.

-   **Agent Ecosystem:** A collection of AI agents that can perform specific tasks, such as analyzing content, reviewing code, or managing memory. These agents leverage the MCP tools to perform their functions. See `core-services/link-ai-core/agents/` for examples.

-   **RAG (Retrieval-Augmented Generation):** The system uses a RAG pipeline to provide contextually relevant information to the AI models. This involves storing documents in a vector database and retrieving them based on semantic similarity to a user's query. See `core-services/link-ai-core/core/rag_system.py`.

---

## 🏗️ Project Structure

```
chonost-manuscript-os/
├── apps/             # Main applications (Multi-platform Frontend)
│   └── frontend/     # Main frontend (Desktop, Mobile, Web, Chat)
├── packages/         # Supplementary packages (Backend, AI, Shared)
├── services/         # Microservices
├── core-services/    # Core backend services and AI logic
├── docs/             # All documentation ⭐
├── scripts/          # Build & Test Scripts
└── data/             # Data and Datasets
```

---

## 📖 Important Documentation

- **[System Architecture](docs/ARCHITECTURE.md)** - A high-level overview of the system architecture.
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - The schema for the chat memory database.
- **[API Documentation](docs/API_DOCUMENTATION.md)** - All API endpoints.
- **[Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)** - The plan for future development.
- **[Security Policy](SECURITY.md)** - The project's security policy.

---

## 🔬 Audit Summary & Recommendations (As of 2025-09-12)

This project has undergone a comprehensive documentation and architectural audit. The following is a summary of the key findings and recommendations.

### Key Findings:

1.  **Architectural Ambiguity:** The project contains multiple, overlapping backend services (`core-services` and `services/backend`) and a fragmented frontend structure (`apps/frontend` and `packages/frontend`). This indicates a need for a clear, unified architectural vision.
2.  **Duplicate Functionality:** There is significant duplication of core logic, including:
    *   **LLM Clients:** Separate clients for OpenAI and Ollama.
    *   **Database Schemas:** Two different modules implementing chat history databases.
    *   **RAG Systems:** At least two different implementations of Retrieval-Augmented Generation.
3.  **Incomplete Features:** Some components, particularly in `services/backend`, use mock data or contain placeholder logic, indicating they are not production-ready.

### High-Priority Recommendations:

1.  **Unify the Architecture:** Decide on a single architectural pattern (e.g., modular monolith or microservices) and refactor the codebase to follow it. This includes merging the duplicate backend and frontend applications.
2.  **Centralize Core Services:** Refactor duplicated logic (LLM clients, database services, RAG) into single, shared services within `core-services`.
3.  **Complete or Remove Placeholder Services:** The `services/backend/routes/manuscript.py` service should be either completed with a proper database or removed in favor of the more robust `core-services`.
