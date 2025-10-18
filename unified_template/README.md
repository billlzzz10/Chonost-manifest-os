# Unified Local-First Template

This template merges the highest-signal components from the Chonost Manuscript OS repo into a single, conflict-free stack. It keeps the proven ideas—FastAPI orchestrator, rich UI primitives, agentic workflows—but strips away cloud dependencies, duplicate responsibilities, and heavyweight packaging.

## Highlights

- **Apps**
  - `apps/backend`: FastAPI service with SQLite persistence, vector cache, and streaming chat endpoints.
  - `apps/frontend`: Vite + React dashboard with Hero UI-inspired components.
  - `apps/agent-cli`: Node CLI exposing Architect → Coder → Debugger pipelines.
- **Packages**
  - `packages/ai-runtime`: Local-first text generation helpers (Ollama compatible) with tool-call streaming.
  - `packages/agent-core`: Deterministic orchestration engine derived from Kilo Code behaviour.
  - `packages/browser-kit`: Puppeteer-core wrapper that reuses cached Chromium binaries for offline automation.
  - `packages/ui`: Hero UI primitives (Button, Card, Command Menu, Markdown viewer) plus design tokens.
- **Docs** cover architecture, migration from the old templates, and configuration.

Everything defaults to local runtimes—Ollama for LLMs, SQLite for storage, cached Chromium for automation—minimising cost and external quotas.

## Getting Started

```bash
corepack enable
pnpm install

# Build shared packages
pnpm build

# Run backend + frontend in parallel
pnpm dev:backend
pnpm dev:frontend

# Launch the agent CLI
pnpm agent plan --task "summarise manuscript chapter 1"
```

The backend listens on `http://localhost:8000`, the frontend on `http://localhost:5173`, and the agent CLI communicates with the backend APIs by default.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/MIGRATION.md`](docs/MIGRATION.md)
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)
- [`../DECISIONS.md`](../DECISIONS.md)
- [`../ARTIFACTS/INVENTORY.md`](../ARTIFACTS/INVENTORY.md)

## License

This template inherits the upstream licenses for reused components. Validate compliance before redistribution.
