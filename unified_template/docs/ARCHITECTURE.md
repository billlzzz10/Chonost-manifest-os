# Unified Template Architecture

The unified template folds the strongest patterns from the existing Chonost Manuscript OS codebase together with lessons from the Vercel AI SDK, Kilo Code agents, Puppeteer automation, and Hero UI – while removing overlaps and enforcing a **local-first**, low-dependency runtime.

## High-Level Layout

```
unified_template/
├── apps/
│   ├── backend/        # FastAPI service with local SQLite + embedding cache, SSE streaming, MCP-lite endpoints
│   ├── frontend/       # Vite + React client using @unified/ui primitives and local data cache
│   └── agent-cli/      # Node CLI that orchestrates Architect → Coder → Debugger loops
├── packages/
│   ├── ai-runtime/     # Lightweight text generation + tools pipeline (Ollama-first, Vercel SDK semantics)
│   ├── agent-core/     # Deterministic planner/executor derived from Kilo Code, decoupled from VS Code
│   ├── browser-kit/    # Puppeteer-core wrapper with cached Chromium management for offline automation
│   └── ui/             # Hero UI-inspired design system (Button, Card, Command Palette, Editor shells)
└── docs/               # Architecture, configuration, migration guidance
```

### Why This Structure

- **Clear responsibility boundaries.** Packages expose reusable building blocks; apps compose them without redundant logic.
- **Local-first defaults.** No cloud API keys required. Ollama, SQLite, and cached Chromium cover inference, storage, and automation.
- **Reusable modules.** Each package can be published or swapped independently (`workspace:*` coordination via pnpm).
- **Testability.** Vitest targets in TypeScript packages, pytest for FastAPI, and smoke scripts for the CLI ensure quick feedback.

## Backend Overview (`apps/backend`)

- FastAPI app with:
  - `/api/chat` – streams completions using `packages/ai-runtime`.
  - `/api/memory` – CRUD endpoints backed by SQLite + persistent embeddings cache.
  - `/api/tools/browser` – exposes selected `browser-kit` automation primitives.
- Embeddings are generated through a local sentence-transformers model (via `ctransformers`) or a deterministic stub if unavailable.
- Server-Sent Events (SSE) push streaming responses to the frontend without extra dependencies.

## Frontend Overview (`apps/frontend`)

- Vite + React + TypeScript.
- Uses `@unified/ui` for layout, typography, tokens, and command palette.
- Bundles a small IndexedDB layer for offline sync with the backend memory APIs.
- Tailwind removed; styling handled via vanilla-extract tokens to keep dependency footprint small.

## Agent CLI (`apps/agent-cli`)

- `pnpm agent <mode>` entry-point built with `commander`.
- Modes:
  - `architect` – plan tasks.
  - `coder` – execute plans.
  - `debugger` – verify outputs and emit fixes.
- Uses `packages/agent-core` for orchestration and shares the same `ai-runtime` client as backend/frontend for consistency.

## Packages Snapshot

- **`ai-runtime`** – Refactors the useful streaming bits from Vercel AI SDK into a provider-agnostic layer biased toward Ollama. Supports tool calls & usage accounting, no remote vendor SDKs.
- **`agent-core`** – Condenses Kilo Code’s multi-step agent into a deterministic state machine. Events emitted via Node `EventEmitter` so backend/CLI can subscribe.
- **`browser-kit`** – Wraps `puppeteer-core` + `@puppeteer/browsers` to guarantee local binaries. Includes queue + timeout guards inspired by Puppeteer’s best practices.
- **`ui`** – Hero UI atoms (Button, Card, Stack, SidePanel) plus Monaco shell and Markdown preview. Ships CSS variables + tokens for consistent dark/light theming.

## Data & Runtime Flow

1. Frontend issues chat or task requests to the backend.
2. Backend stores conversation state, calls `agent-core` if orchestration is needed, and streams model deltas using `ai-runtime`.
3. `agent-core` can invoke `browser-kit` actions or local scripts; results are persisted via the backend’s memory service.
4. Agent CLI shares the same flow but communicates through the backend REST API to stay composable.

## Testing Strategy

- `pnpm test` at root runs:
  - Vitest suites in `packages/*`.
  - Pytest suite in `apps/backend`.
  - CLI smoke tests in `apps/agent-cli`.
- Git hooks (via `corepack`) run lint + type-check to keep modules consistent.

Refer to `docs/MIGRATION.md` and `../../DECISIONS.md` for details on what was removed, replaced, or simplified.
