# Environment Setup Guide

This guide walks through preparing a local development environment for Chonost Manuscript OS. It assumes you are working on macOS, Linux, or Windows with PowerShell.

## 1. Install Prerequisites

- Node.js 18 or newer (use `nvm` or the official installer).
- Python 3.10 or newer.
- Git.
- Docker Desktop (optional, required for the full compose stack).

## 2. Clone the Repository

```bash
git clone https://github.com/billlzzz10/Chonost-manifest-os.git
cd Chonost-manifest-os
```

## 3. Python Environment

```bash
python -m venv .venv
# Activate the virtualenv (PowerShell example)
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r services/api-server/requirements.txt
```

### Environment Variables

Copy `.env.example` to `.env` in the repo root and populate any required secrets.

```bash
Copy-Item .env.example .env
```

The FastAPI service reads configuration from environment variables with fallbacks, so leaving values blank is acceptable for most local runs. Set at least `JWT_SECRET` before exercising `/api/rag`.

## 4. JavaScript Workspaces

```bash
npm install
```

This installs dependencies for the root workspace, the Craft IDE, and the shared UI library.

## 5. Run Services Locally

### API server

```bash
cd services/api-server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Craft IDE frontend

```bash
cd craft-ide
npm run dev
```

## 6. Docker Compose (Optional)

The repository ships with a compose file that launches Postgres, Redis, Qdrant, Grafana, the API server, and the Craft IDE.

```bash
docker-compose up -d
```

To stop the stack:

```bash
docker-compose down
```

## 7. Running Tests

```bash
cd services/api-server
python -m pytest
```

The suite focuses on sanity checks for `main.py` and MCP wiring.

## 8. Troubleshooting Tips

- **Missing Python packages**: verify the virtualenv is activated and re-run `pip install -r services/api-server/requirements.txt`.
- **Webpack/Vite port conflicts**: change the `VITE_PORT` value in `craft-ide/.env` or run `npm run dev -- --port 3001`.
- **Docker volume permission issues**: remove the `postgres_data`, `redis_data`, and `qdrant_data` volumes and retry (`docker volume rm ...`).

Keeping environments isolated (virtualenvs, Node versions via `nvm`) helps avoid cross-project conflicts as the monorepo evolves.

