# Local Runtime Checklist

Use this checklist to confirm the unified template runs fully offline.

- [ ] Install Node.js ≥ 18.18 and Python ≥ 3.10.
- [ ] Run `corepack enable` then `pnpm install` at `unified_template/`.
- [ ] Build packages: `pnpm build`.
- [ ] Start backend: `cd unified_template/apps/backend` → `uvicorn app.main:app --reload`.
  - Confirms SQLite database is created under `.runtime/storage.db`.
  - Verify `/api/health` returns `{"status":"ok"}`.
- [ ] Warm up Ollama: ensure `ollama serve` is running with the configured model (`OLLAMA_MODEL`, default `qwen2.5-coder`).
- [ ] Start frontend: `pnpm dev:frontend` to reach `http://localhost:5173`.
  - Send a prompt; ensure the streamed response renders without cloud calls (inspect network tab – only local requests).
- [ ] Exercise Puppeteer tooling: from repo root run `pnpm --filter @unified/browser-kit test`.
  - Browser binaries download to `.runtime/browser-cache` and no remote automation endpoints are hit afterwards.
- [ ] Run agent CLI: `pnpm agent architect "Draft release notes for the latest sprint"`.
  - Verify plan emitted and no cloud providers are referenced.

All steps complete ⇒ local runtime hardened.
