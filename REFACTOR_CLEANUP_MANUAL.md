# Manual Cleanup Required for Project Refactoring

**To:** Project Maintainer

**From:** Jules, AI Software Engineer

**Reason for this file:**

I was tasked with reorganizing and cleaning up the project structure. However, I encountered a technical limitation with my tools. The system prevents me from moving or deleting directories that contain a very large number of files, even with explicit permission. This is a safety feature to prevent accidental repository-wide changes.

As a workaround, I am leaving this note for you to perform the deletion steps manually. Once these directories are deleted, the project structure will be much cleaner and more maintainable.

---

## Directories to Delete

Please delete the following directories from the project root. I have identified them as either complete duplicates of other services or as legacy code that is no longer part of the primary development path.

### 1. Backend Duplicates & Legacy

*   **Directory:** `chonost-unified`
    *   **Reason:** This is a nearly identical duplicate of the `core-services/link-ai-core` directory. To eliminate massive code duplication, this entire folder can be removed. `core-services` should be considered the source of truth for Python-based services.

*   **Directory:** `services/backend`
    *   **Reason:** This is a legacy Python Flask backend. The primary backend services are being consolidated in `core-services` (Python) and the new `server` (Node.js). This directory can be safely removed to avoid confusion.

### 2. Frontend Duplicates & Legacy

*   **Directory:** `apps/frontend`
    *   **Reason:** Legacy or duplicated frontend application. The primary, active frontend is `craft-ide`.

*   **Directory:** `services/frontend`
    *   **Reason:** Legacy or duplicated frontend application. The primary, active frontend is `craft-ide`.

*   **Directory:** `packages/frontend`
    *   **Reason:** Legacy or duplicated frontend application. The primary, active frontend is `craft-ide`.

---

After deleting these directories, the project will be significantly cleaner. Thank you for your understanding and assistance in this matter.

Best regards,
Jules
