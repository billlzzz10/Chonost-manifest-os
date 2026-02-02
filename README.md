Chonost-manifest-os

📖 Overview
Chonost-manifest-os is a Rust + React/TypeScript project designed as a multi-crate workspace with backend, server, and desktop application support.  
The system provides a foundation for building AI-driven applications, bots, and desktop tools with a secure, modular, and extensible architecture.

---

🏗️ Project Structure
`plaintext
chonost-manifest-os/
├── crates/                # Rust workspace crates
│   ├── backend/           # Core business logic (ACP, session, events, security, filesystem, projects, search, CLI, RPC)
│   ├── server/            # Rocket-based REST API + WebSocket server
│   └── tauri-app/         # Tauri desktop application wrapper
│
├── frontend/              # React/TypeScript frontend
│   └── desktop-app/       # SPA for desktop/web (UI, i18n, hooks, utils, renderers, etc.)
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── PRIVACY.md
│   └── TERMS.md
│
├── Cargo.toml             # Rust workspace definition
├── justfile               # Task runner (Just)
├── pnpm-lock.yaml         # Frontend package lock
└── README.md
`

---

⚙️ Technology Stack

Backend
- Rust (2024 Edition)  
- Tokio – async runtime  
- Serde – serialization  
- Rocket – REST API framework  
- Tauri – desktop integration  

Frontend
- React 19 + TypeScript 5.9  
- Vite – build tool  
- Tailwind CSS – styling  
- shadcn/ui – component library  
- CodeMirror / Monaco – code editing  

Tooling
- Just – task runner  
- pnpm – package manager  
- ESLint + Prettier – linting & formatting  
- cargo-nextest + tarpaulin – testing & coverage  

---

🚀 Getting Started

Prerequisites
- Rust (latest stable)  
- Node.js 22+  
- pnpm 10+  
- Just task runner  

Setup
`bash

Install dependencies
just deps

Desktop development (Tauri + frontend)
just dev

Web development (frontend + backend server)
just dev-web
`

---

🧪 Testing
`bash

Run all tests
just test
cargo nextest run

Run with coverage
cargo tarpaulin
`

---

🔒 Security
- Whitelist of safe commands  
- Blacklist of dangerous patterns  
- API key masking in logs  
- SSRF protection  
- Environment variable cleanup with RAII  

---

📑 Documentation
- ARCHITECTURE.md – System design and structure  
- AGENTS.md – Agent roles and communication protocol  
- PRIVACY.md – Privacy policy  
- TERMS.md – Terms of service  

---

🛠️ Development Workflow
- Issues drive tasks (label jules to trigger automation)  
- Feature branches per crate/module  
- Pull Requests with automated checks  
- Documentation updates required for each change  

---

📜 License
Specify your license here (MIT, Apache 2.0, GPL, etc.)

---