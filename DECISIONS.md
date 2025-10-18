# Decisions

## What we kept
- FastAPI orchestrator core, simplified into `apps/backend` with SQLite + SSE (no Postgres/Redis).
- Hero UI primitives reimplemented as `@unified/ui` for consistent design tokens without Tailwind.
- Kilo Code multi-mode agent flow distilled into `@unified/agent-core` + CLI.
- Puppeteer automation, reduced to cached Chromium helpers inside `@unified/browser-kit`.
- Local-first LLM streaming semantics inspired by Vercel AI SDK via `@unified/ai-runtime`.

## What we removed or replaced
- Cloud provider SDKs (OpenAI, Anthropic, Codacy) in favour of Ollama/local adapters.
- Docker Compose stack provisioning Postgres/Redis/Qdrant – replaced with SQLite + on-disk caches.
- Monolithic MCP toolbox scripts; functionality split into typed packages with smaller interfaces.
- Tailwind/PostCSS + duplicated JSX files in the UI kit; replaced with vanilla-extract tokens and TSX-only components.
- VS Code/Tauri specific glue; frontend ships as pure Vite SPA, packaging optional.

## Rationale
- Deduped responsibilities across backend/frontend/agents so each package owns a focused concern.
- Reduced dependency surface to minimise installation friction and licensing risk.
- Ensured all runtime-critical paths operate offline, aligning with cost and quota constraints.
- Preserved extensibility via workspace packages that can be swapped or published independently.

