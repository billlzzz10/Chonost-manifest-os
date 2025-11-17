# Contributing to Chonost Manuscript OS

First off, thank you for considering contributing to this project! Your help is invaluable in making this a great tool for writers and creators.

This document provides guidelines for contributing to the project and an overview of the new, unified architecture to help you get started.

## Project Architecture Overview

This project has been refactored into a streamlined monorepo architecture. The goal was to eliminate redundancy and create a clear, maintainable structure. Here are the key components:

### 1. Core Backend Service: `core-services/link-ai-core`

This is the single source of truth for all backend logic. It is a powerful FastAPI application that serves as the central orchestrator for the entire system.

-   **Location:** `/core-services/link-ai-core/`
-   **Responsibilities:**
    -   Provides all public API endpoints for managing manuscripts, nodes, edges, and other data.
    -   Orchestrates AI tool calls via the MCP (Modular Component Protocol).
    -   Manages the database connection and data models.
-   **Contribution Note:** When adding or modifying code within this service, you **MUST** follow the import conventions documented in `/core-services/link-ai-core/AGENTS.md`. All internal imports must be absolute from the `link-ai-core` root.

### 2. Primary Frontend Application: `craft-ide`

This is the main user-facing application. It is a desktop app built with **Tauri** and **React**, providing a rich, native experience for manuscript management.

-   **Location:** `/craft-ide/`
-   **Responsibilities:**
    -   Provides the main user interface, including the editor, whiteboard, and chat panels.
    -   Communicates with the core backend service to fetch and manipulate data.

### 3. Shared Packages

The `/packages/` directory contains shared code intended to be used across different parts of the application. This is key to our code reuse strategy.

-   **`packages/ui`**: A centralized library of shared React UI components (e.g., buttons, cards, dialogs). When you need a standard UI element, check here first. If you build a new, reusable component, add it here.
-   **`packages/ai_clients`**: Contains the unified client for interacting with various Large Language Models (LLMs) and embedding providers. All AI-related communication should go through this package.
-   **`packages/rag-pipeline`**: The powerful, unified Retrieval-Augmented Generation (RAG) system. It includes an `IntelligentFileProcessor` for deep-scanning local directories and ingesting various file types into a vector database.

### 4. Containerization with Docker

The entire backend infrastructure is containerized for easy setup and deployment.

-   **Configuration:** `/docker-compose.yml`
-   This file orchestrates the core backend, AI services, and databases (PostgreSQL, Redis, Qdrant).

## Getting Started

To get the backend services up and running for development, follow these steps:

1.  **Prerequisites:** Ensure you have [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.
2.  **Environment Variables:** Create a `.env` file in the root directory by copying the `.env.example` file and fill in any necessary API keys (e.g., `OPENAI_API_KEY`).
3.  **Start Services:** Open a terminal in the root of the project and run:
    ```bash
    docker-compose up --build
    ```
    This command will build the container images and start all the necessary backend services. The main API will be available at `http://localhost:8000`.

To run the frontend desktop app:
1.  **Prerequisites:** Ensure you have [Node.js](https://nodejs.org/) and [Rust](https://www.rust-lang.org/tools/install) installed.
2.  **Navigate to the directory:** `cd craft-ide`
3.  **Install dependencies:** `npm install`
4.  **Run the app:** `npm run tauri dev`

## How to Contribute

We welcome contributions of all kinds, from bug fixes to new features!

-   **Adding an API Endpoint:**
    1.  Create or modify a route file in `/core-services/link-ai-core/api/`.
    2.  Add your new endpoint to the `APIRouter`.
    3.  Ensure your data models are defined in `/core-services/link-ai-core/db_models.py` (for the database) and your route file (for Pydantic).
    4.  The router is already included in `main.py`, so your endpoint will be available automatically.

-   **Adding a Shared UI Component:**
    1.  Create a new `.tsx` file for your component in `/packages/ui/`.
    2.  Export the component from `/packages/ui/index.ts`.
    3.  You can now import and use the component in `craft-ide` or any other future frontend application.

Thank you for helping to build the future of writing!