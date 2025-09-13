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
