# Chonost Manuscript OS

Chonost Manuscript OS is a monorepo that combines a FastAPI-based MCP orchestrator, a React/Tauri desktop client (`craft-ide`), and a reusable UI component library (`@chonost/ui`). The goal of the project is to provide a foundation for experimenting with AI-assisted manuscript tooling while keeping the codebase modular and approachable.

## Key Capabilities

- FastAPI MCP orchestrator with endpoints for basic server discovery and tool execution.
- React + Vite desktop interface packaged through Tauri for multi-platform use.
- Shared component library that powers the Craft IDE experience.
- Docker Compose stack that provisions the API server together with Postgres, Redis, and Qdrant.

## Repository Layout

```
.
|- craft-ide/              # React + Tauri desktop client
|- packages/ui/            # Shared UI component library
|- services/api-server/    # FastAPI MCP orchestrator
|- services/testing/       # Testing helpers and Docker image
|- docs/                   # Architecture, database, and roadmap documentation
|- scripts/                # Automation helpers (e.g. ai-commit)
`- docker-compose.yml      # Full-stack container orchestration
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- Docker Desktop (optional, required for the compose stack)

### Install Dependencies

```bash
# Install JS workspaces (root package.json manages workspaces)
npm install

# Install API server dependencies
cd services/api-server
pip install -r requirements.txt
```

### Run the API Server

```bash
cd services/api-server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server exposes `/health`, `/mcp/servers`, `/mcp/tools`, `/mcp/status`, and `/mcp/call`.

### Run the Craft IDE Frontend

```bash
cd craft-ide
npm run dev
```

By default the frontend expects the API server at `http://localhost:8000`.

### Run with Docker Compose

```bash
# From the repo root
docker-compose up -d
```

This brings up the API server together with Postgres, Redis, Qdrant, Grafana, and the Craft IDE container. Update the `.env` file before starting if you need custom secrets.

## Environment Configuration

Copy `.env.example` to `.env` and supply any API keys you intend to use. The FastAPI settings loader in `services/api-server/config.py` falls back to sensible defaults when variables are missing, making local development easy to start.

## Testing

```bash
cd services/api-server
python -m pytest
```

The current test suite validates the health check, MCP endpoints, and basic configuration wiring in `main.py`.

## Documentation

- `docs/ARCHITECTURE.md` explains the current orchestrator layout with Mermaid diagrams.
- `docs/DATABASE_SCHEMA.md` captures the chat memory schema.
- `docs/DEVELOPMENT_ROADMAP.md` outlines longer-term goals and technical debt.

Additional documentation is still work in progress. If you spot inaccuracies, feel free to open an issue or update the relevant file.

## Contributing

We welcome pull requests that clarify documentation, improve test coverage, or extend the orchestrator safely. Please open a draft PR early if you plan to make larger architectural changes so we can align on direction.
