# Chronost-manifest-os

Chronost-manifest-os is a project that provides a foundation for building desktop and web applications with a Rust backend and a React/TypeScript frontend.

## Project Structure

-   `crates/`: Contains the Rust workspace crates.
    -   `backend`: Core business logic.
    -   `server`: Rocket-based REST API and WebSocket server.
    -   `tauri-app`: Tauri desktop application wrapper.
-   `frontend/`: Contains the frontend application.
    -   `desktop-app`: React/TypeScript application built with Vite and styled with Tailwind CSS.
-   `docs/`: Contains project documentation.
-   `justfile`: Defines tasks for automating common development tasks.
-   `README.md`: Provides an overview of the project.

## Setup Instructions

1.  **Install Rust:** Follow the instructions on the [Rust website](https://www.rust-lang.org/tools/install) to install Rust.
2.  **Install Node.js and pnpm:** Follow the instructions on the [Node.js website](https://nodejs.org/en/download/) to install Node.js, then install pnpm with `npm install -g pnpm`.
3.  **Install just:** Follow the instructions on the [just website](https://github.com/casey/just) to install just.
4.  **Install dependencies:** Run `just deps` to install all dependencies.

## Workflow

-   **Desktop Development:** Run `just dev` to start the Tauri desktop application and frontend in development mode.
-   **Web Development:** Run `just dev-web` to start the backend server and frontend in development mode.
-   **Build:** Run `just build` to build the project for production.
-   **Test:** Run `just test` to run the project's tests.
-   **Lint:** Run `just lint` to lint the project's code.
