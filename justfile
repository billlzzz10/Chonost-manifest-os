# Task Automation with just

# Install all dependencies
deps:
    cargo build
    cd frontend/desktop-app && pnpm install

# Start desktop development (Tauri + frontend)
dev:
    cd crates/tauri-app && cargo tauri dev

# Start web development (frontend + backend)
dev-web:
    cd crates/server && cargo run &
    cd frontend/desktop-app && pnpm dev

# Build the project
build:
    cargo build --release
    cd frontend/desktop-app && pnpm build

# Run tests
test:
    cargo test
    cd frontend/desktop-app && pnpm test

# Lint the project
lint:
    cargo clippy
    cd frontend/desktop-app && pnpm lint
