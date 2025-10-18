# Unified Backend

FastAPI service that exposes chat completions, conversation memory, and lightweight browser automation hooks. Defaults to SQLite + Ollama so it runs fully offline.

## Quickstart

```bash
python -m venv .venv
source .venv/Scripts/activate  # or `. .venv/bin/activate` on Unix
pip install -e .
uvicorn app.main:app --reload
```

The service listens on `http://localhost:8000`.

