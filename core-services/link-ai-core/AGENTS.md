# Agent Coding Conventions for link-ai-core

This document outlines the essential coding conventions that all agents must follow when working within the `core-services/link-ai-core` service.

## 1. Import Statements

**All Python import statements MUST be absolute.**

To ensure consistency and prevent import errors, especially during testing, all imports must be absolute relative to the `core-services/link-ai-core` directory.

### Rationale

The project structure uses directories with hyphens (e.g., `core-services`), which are not standard Python package names. To make the code testable and runnable, the testing environment adds `core-services/link-ai-core` to the `sys.path`. Therefore, all internal imports must be written as if this directory is the root.

### Correct ✅

```python
# Assuming the file is located anywhere inside core-services/link-ai-core/
from database import get_db
from mcp.client import MCPClient
from api import manuscript_routes
```

### Incorrect ❌

```python
# Do NOT use relative imports like these.
from .database import get_db
from ..models import MCPServer
from ..api import manuscript_routes
```

Adherence to this rule is critical for maintaining the stability and testability of the service. Any new or modified code must be checked to ensure it follows this convention.