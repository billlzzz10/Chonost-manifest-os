# Configuration

All services read environment variables via `.env` at the repository root. The backend uses [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) while TypeScript packages rely on `dotenv-flow`.

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local model API for `packages/ai-runtime`. |
| `OLLAMA_MODEL` | `qwen2.5-coder` | Default model identifier for completions. |
| `VECTOR_CACHE_PATH` | `.runtime/vectors.db` | Location of the on-disk embedding cache. |
| `SQLITE_PATH` | `.runtime/storage.db` | Backend persistence database. |
| `BROWSER_CACHE_PATH` | `.runtime/browser-cache` | Chromium cache used by `packages/browser-kit`. |
| `AGENT_MAX_STEPS` | `8` | Safety cap for Architect/Coder/Debugger loops. |
| `AGENT_LOG_LEVEL` | `info` | Log level for agent orchestration. |
| `FRONTEND_API_URL` | `http://localhost:8000` | API endpoint consumed by the frontend and CLI. |

Create `.env.local` to override values without committing secrets.

## Secrets

Cloud providers are optional. If you opt into remote inference, add keys such as `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`. The backend auto-detects these variables and enables the corresponding provider adapters while keeping Ollama as the default.

## Config Loading Order

1. OS environment variables
2. `.env.local`
3. `.env`

Frontends with Vite use the `VITE_` prefix (`VITE_FRONTEND_API_URL`, etc.) when variables must be exposed to the browser.
