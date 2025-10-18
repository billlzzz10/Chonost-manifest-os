# Template Inventory

This inventory captures the major building blocks in the current repository and highlights the responsibilities we will merge into the unified template.

| Path | Stack | Responsibility | Notes / Issues |
|------|-------|----------------|----------------|
| `craft-ide/` | React + Vite + Tauri | Desktop UI with Monaco editor, multi-mode panels, heavy tailwind theme | Pulls cloud SDKs (OpenAI, Anthropic); large dependency footprint; focused on desktop packaging. |
| `packages/ui/` | React component lib | Hero UI-inspired component primitives, dashboards, editors | Reusable but tightly coupled to Tailwind/PostCSS utilities; includes redundant JSX/TSX variants. |
| `services/api-server/` | FastAPI | MCP orchestrator, JWT-protected `/api/rag`, registry/client abstractions | Mixes experimental code paths with unused datasets; expects external services (Postgres, Redis, Qdrant). |
| `services/mcp-toolbox/` | Node MCP helper | Config loader + HTTP tool invoker + large mock suite | Provides valuable local mocks but file is monolithic (700+ LOC) and references Codacy/cloud defaults. |
| `services/code-interpreter/` | Python | Thin wrapper exposing a `forge.py` automation script | Local execution friendly but unintegrated with the main orchestrator. |
| `agents/` | Node scripts | Code review & memory agents that call MCP toolbox | Depend on Codacy server and auto-fix commands; contain Thai/English logging. |
| `services/testing/` | Docker + pytest helpers | Containerised test harness for MCP flows | Useful for local validation; overlaps with orchestrator smoke tests. |
| `Docs/` | Markdown | Architecture, DB schema, roadmap | Provide context but some docs out of sync with code. |

Additional notes:

- `docker-compose.yml` provisions multiple external databases, conflicting with the “local-first” goal.
- Multiple `.env.*` examples emphasise cloud API keys; few fallbacks for offline use.
- Frontend and backend each declare their own dependency managers (npm/pip) without a unified workflow.
