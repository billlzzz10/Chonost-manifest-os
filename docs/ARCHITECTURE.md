# Architecture

This document outlines the architecture of the Chronost-manifest-os project.

## Overview

The project is a monorepo containing a Rust-based backend, a REST and WebSocket server, and a Tauri-based desktop application with a React/TypeScript frontend.

## Components

- **Rust Workspace:** The core of the project, containing the backend logic, server, and Tauri application.
  - `crates/backend`: Core business logic, including ACP, session management, events, security, filesystem operations, project management, search, CLI, and RPC.
  - `crates/server`: A Rocket-based REST API and WebSocket server.
  - `crates/tauri-app`: The Tauri desktop application wrapper.
- **Frontend:** A React/TypeScript application built with Vite and styled with Tailwind CSS.
  - `frontend/desktop-app`: The source code for the frontend application.
- **Documentation:** Project documentation.
  - `docs/`: Contains architecture, agent instructions, privacy policy, and terms of service.
- **Task Automation:** A `justfile` for automating common tasks.
  - `justfile`: Defines tasks for building, testing, and linting the project.
