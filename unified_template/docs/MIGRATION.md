# Migration Guide

Use this guide to transition from the existing multi-template repository to the unified local-first template.

## Mapping Legacy → Unified

| Legacy Component | Unified Location | Key Changes |
|------------------|------------------|-------------|
| `services/api-server` FastAPI app | `apps/backend` | Collapsed to a single FastAPI project with SQLite persistence, SSE streaming, and optional embeddings cache. Removes Postgres/Redis/Qdrant dependencies. |
| `craft-ide` React/Tauri client | `apps/frontend` | Rebuilt as a pure Vite + React SPA that consumes backend APIs and `@unified/ui` primitives. Tauri packaging is optional. |
| `packages/ui` component library | `packages/ui` | Deduplicated to TypeScript-only components and design tokens; removes duplicated JSX/TSX files and Tailwind requirement. |
| `services/mcp-toolbox` | `packages/agent-core` + `packages/browser-kit` | Splits tool orchestration from browser automation. HTTP-only mocks retained; Codacy/cloud-specific helpers removed. |
| `agents/*` scripts | `apps/agent-cli` + `packages/agent-core` | Replaces bespoke scripts with structured Architect/Coder/Debugger modes using local runtime + event hooks. |
| `services/code-interpreter/forge.py` | `apps/backend/worker` + CLI tools | Brought in as part of the agent CLI tooling; exposed as a task runner triggered via API. |

## Migration Steps

1. **Prepare data** – Export conversation history and embeddings from the old backend (if any). The new backend includes scripts under `apps/backend/scripts/` for importing JSON/CSV dumps.
2. **Adopt workspace tooling** – Switch to `pnpm` (root `package.json`) and align Python tooling with the unified `pyproject.toml`.
3. **Update frontend** – Swap imports from `@chonost/ui` to `@unified/ui`. Replace Tauri-specific shell components with the provided `DesktopShell` if native packaging is required.
4. **Replace agents** – Retire direct uses of `services/mcp-toolbox`. Instead, register tools with `packages/agent-core` and call them through the CLI or backend.
5. **Drop external databases** – Remove Postgres/Redis/Qdrant from deployment manifests. SQLite + optional DuckDB handle persistence for the unified stack.
6. **Verify runtime** – Run `pnpm test` and `pnpm agent verify` to validate that backend APIs, UI flows, and agent orchestration work as expected.

## Removed / Replaced Features

- Codacy-specific MCP tooling and cloud scanners (kept as extension hooks via `packages/agent-core` events).
- Direct Anthropic/OpenAI SDK usage; replaced with the local-first `ai-runtime` provider wrappers.
- Tailwind/PostCSS pipeline; replaced with vanilla-extract tokens and CSS modules.
- Docker Compose stack that provisioned heavy external services.

Refer to `../DECISIONS.md` for the full rationale behind each removal or change.
