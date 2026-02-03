AGENTS.md

Table of Contents
1. Agent Overview  
2. Agent Roles  
3. Communication Protocol  
4. Agent Lifecycle  
5. Technology Stack  
6. Security Model  
7. Agent Orchestration  
8. Testing Framework  
9. Deployment  
10. Configuration  
11. Development Workflow

---

1. Agent Overview
The system is designed around multi-agent collaboration, where each agent encapsulates a specific responsibility. Agents communicate through the Agent Communication Protocol (ACP), ensuring structured, auditable, and secure interactions.

Key Features
- Role-based specialization (backend, orchestration, UI integration)  
- Event-driven communication with WebSocket backbone  
- Tool call confirmation requiring explicit approval  
- Cross-agent interoperability via JSON-RPC 2.0  
- Security-first design with command filtering and permission enforcement  

---

2. Agent Roles

Core Agents
- Backend Agent  
  - Implements ACP protocol  
  - Handles session lifecycle, tool calls, and backend orchestration  
  - Provides APIs for other agents  

- Server Agent  
  - Exposes REST + WebSocket endpoints  
  - Manages client connections and broadcasts events  
  - Serves frontend assets  

- Desktop Agent (Tauri)  
  - Wraps frontend React app  
  - Provides native integration (menus, dialogs, notifications)  
  - Bridges system events to frontend  

Supporting Agents
- Security Agent  
  - Validates commands against whitelist/blacklist  
  - Enforces SSRF protection and API key masking  
- Search Agent  
  - Indexes and retrieves chat/project data  
  - Provides full-text search with ranking algorithms  
- Project Agent  
  - Manages workspace metadata and session history  

---

3. Communication Protocol
- ACP (Agent Communication Protocol)  
  - Based on JSON-RPC 2.0  
  - Supports text, image, audio, and resource blocks  
  - Tool call workflow with user confirmation  
  - Error propagation with structured codes  

---

4. Agent Lifecycle
1. Initialization – Agent registers capabilities  
2. Authentication – API keys or OAuth validated  
3. Session Start – New workspace/session created  
4. Event Handling – Real-time updates broadcast  
5. Termination – Cleanup environment variables, close connections  

---

5. Technology Stack
- Rust (Tokio, Serde, Rocket, Tauri)  
- TypeScript/React frontend  
- WebSocket for event streaming  
- JSON-RPC for structured agent communication  
- SHA2/Regex/Chrono for security and data handling  

---

6. Security Model
- Whitelist of safe commands (100+)  
- Blacklist of dangerous patterns  
- API key masking in logs  
- SSRF protection with URL validation  
- RAII cleanup for environment variables  

---

7. Agent Orchestration
- Workspace-based orchestration with Cargo  
- Event bus for inter-agent communication  
- Tool call confirmation requiring explicit user approval  
- Cross-platform execution (Windows, macOS, Linux)  

---

8. Testing Framework
- cargo-nextest for Rust agents  
- mockall for agent mocks  
- proptest for property-based testing  
- criterion for benchmarking agent performance  
- tarpaulin for coverage (95% threshold)  

---

9. Deployment
- Server Agent → Rocket-based REST/WebSocket server  
- Desktop Agent → Tauri binary embedding frontend  
- Backend Agent → Core library crate  
- CI/CD → GitHub Actions with lint, test, build pipelines  

---

10. Configuration
- Environment variables for API keys and endpoints  
- Config files for backend provider selection  
- i18n configuration for multilingual support  
- Cargo workspace for crate management  

---

11. Development Workflow
- Issue-driven tasks (label jules)  
- Branching model: feature branches per agent  
- Code review via PRs with automated checks  
- Documentation updates required for each agent change  

---