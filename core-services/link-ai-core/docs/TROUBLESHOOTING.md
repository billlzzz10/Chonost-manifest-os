# 🚨 Troubleshooting Guide - MCP Orchestrator

## 📋 Overview

เอกสารนี้ครอบคลุมปัญหาที่พบบ่อยและการแก้ไขสำหรับ MCP Orchestrator v0.2.0

## 🔴 Critical Issues

### 1. Python Environment Corruption

#### **Problem Description**

Python environment มีปัญหาอย่างรุนแรง ทำให้ไม่สามารถติดตั้งหรือใช้งาน packages ได้

#### **Symptoms**

- `pip install` สำเร็จแต่ `import` ไม่ได้
- packages ที่ติดตั้งแล้วไม่สามารถ import ได้
- Python environment ไม่สามารถใช้งานได้ปกติ

#### **Root Cause**

- Python installation corruption
- Environment variables conflicts
- System-level Python configuration issues

#### **Solutions**

##### **Option 1: Reinstall Python (Recommended)**

```bash
# 1. Uninstall current Python
# 2. Download fresh Python installer
# 3. Install with "Add to PATH" option
# 4. Create new virtual environment
python -m venv venv_new
venv_new\Scripts\activate
pip install -r requirements.txt
```

##### **Option 2: Fix Current Environment**

```bash
# 1. Check Python path
python -c "import sys; print(sys.executable)"

# 2. Check site-packages
python -c "import site; print(site.getsitepackages())"

# 3. Reinstall critical packages
pip install --force-reinstall pytest pytest-asyncio uvicorn fastapi
```

##### **Option 3: Use Alternative Python**

```bash
# 1. Find working Python installation
# 2. Use full path to Python executable
F:\4_TOOLS\CLI\Python\python.exe -m pip install package_name
```

#### **Prevention**

- ใช้ virtual environments เสมอ
- ไม่ติดตั้ง packages ใน global Python
- ตรวจสอบ Python path ก่อนใช้งาน

### 2. Dependency Installation Issues

#### **Problem Description**

Packages ไม่สามารถติดตั้งใน environment ได้ หรือติดตั้งแล้วใช้งานไม่ได้

#### **Affected Packages**

- `pytest`
- `pytest-asyncio`
- `uvicorn`
- `fastapi`
- `click`
- `structlog`

#### **Solutions**

##### **Force Reinstall**

```bash
pip install --force-reinstall --no-cache-dir package_name
```

##### **Install with Dependencies**

```bash
pip install package_name[all]
```

##### **Check Package Compatibility**

```bash
pip check
pip list --outdated
```

##### **Use Alternative Package Manager**

```bash
# Try conda if available
conda install package_name

# Or use pip with specific version
pip install package_name==version
```

## 🟡 Common Issues

### 3. CLI Syntax Errors

#### **Problem Description**

`tools/mcp_cli.py` มี syntax errors ใน f-string formatting

#### **Symptoms**

```
SyntaxError: unexpected character after line continuation character
```

#### **Solution**

แก้ไข f-string formatting โดยใช้ string concatenation แทน:

```python
# Before (problematic)
click.echo(f"    -d '{{\"server\": \"{server_name}\", \"tool\": \"{tool_name}\", \"arguments\": {args or \"{}\"}}}'")

# After (fixed)
click.echo("    -d '{\"server\": \"" + server_name + "\", \"tool\": \"" + tool_name + "\", \"arguments\": " + (args or "{}") + "}'")
```

### 4. Import Errors

#### **Problem Description**

ไม่สามารถ import modules ได้

#### **Common Errors**

```
ImportError: cannot import name 'StdioJsonRpcClient' from 'services.orchestrator.mcp.client'
ModuleNotFoundError: No module named 'pytest_asyncio'
```

#### **Solutions**

##### **Check Module Structure**

```bash
# Verify file exists
ls services/orchestrator/mcp/client.py

# Check import statements
grep -n "class.*Client" services/orchestrator/mcp/client.py
```

##### **Fix Import Paths**

```python
# Add project root to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

##### **Update **init**.py**

```python
# services/orchestrator/mcp/__init__.py
from .client import MCPClient  # Updated class name
from .pool import MCPPool
from .registry import REGISTRY

__all__ = ["MCPClient", "MCPPool", "REGISTRY"]
```

### 5. FastAPI Server Not Starting

#### **Problem Description**

FastAPI server ไม่สามารถ start ได้หรือไม่ listen บน port ที่กำหนด

#### **Symptoms**

```
curl: (7) Failed to connect to localhost port 8000
netstat: no process listening on port 8000
```

#### **Solutions**

##### **Check Dependencies**

```bash
python -c "import uvicorn; print('uvicorn available')"
python -c "import fastapi; print('fastapi available')"
```

##### **Manual Server Start**

```bash
# Start server manually
python -c "from services.orchestrator.main import run_app; run_app()"

# Or use uvicorn directly
uvicorn services.orchestrator.main:app --host 0.0.0.0 --port 8000
```

##### **Check Port Availability**

```bash
# Check if port is in use
netstat -an | findstr :8000

# Kill processes using port
tasklist | findstr python
taskkill /f /im python.exe
```

## 🟢 System Validation

### 6. Testing System Components

#### **Step-by-Step Validation**

##### **1. Test Core Modules**

```bash
# Test registry
python -c "from services.orchestrator.mcp.registry import REGISTRY; print('Registry OK')"

# Test client
python -c "from services.orchestrator.mcp.client import MCPClient; print('Client OK')"

# Test pool
python -c "from services.orchestrator.mcp.pool import MCPPool; print('Pool OK')"
```

##### **2. Test FastAPI App**

```bash
# Test app loading
python -c "from services.orchestrator.main import app; print('FastAPI OK')"

# Test endpoints (if server running)
curl localhost:8000/health
curl localhost:8000/mcp/servers
```

##### **3. Test CLI**

```bash
# Test basic CLI
python tools/mcp_cli.py --help

# Test specific commands
python tools/mcp_cli.py servers
python tools/mcp_cli.py health
```

##### **4. Test pytest**

```bash
# Check pytest installation
python -c "import pytest; print('pytest OK')"

# Check pytest-asyncio
python -c "import pytest_asyncio; print('pytest-asyncio OK')"

# Run basic tests
pytest --version
pytest --collect-only
```

## 🔧 Environment Setup

### 7. Recommended Environment Setup

#### **Fresh Python Installation**

```bash
# 1. Download Python 3.12+ from python.org
# 2. Install with "Add to PATH" option
# 3. Verify installation
python --version
pip --version

# 4. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 5. Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn pydantic structlog click
pip install pytest pytest-asyncio pytest-cov httpx
```

#### **Environment Variables**

```bash
# Set environment variables
set PYTHONPATH=%PYTHONPATH%;F:\1_PROJECTS\02_DEV\REPO\FileSystemMCP
set PYTHONUNBUFFERED=1
set PYTHONDONTWRITEBYTECODE=1
```

#### **IDE Configuration**

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

## 📚 Additional Resources

### **Useful Commands**

```bash
# Check Python environment
python -c "import sys; print('Python path:'); [print(p) for p in sys.path]"

# Check installed packages
pip list
pip show package_name

# Check package compatibility
pip check

# Debug import issues
python -v -c "import package_name"
```

### **Log Files**

```bash
# Check Python logs
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"

# Check system logs
Get-EventLog -LogName Application -Source Python
```

### **Documentation**

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip Troubleshooting](https://pip.pypa.io/en/stable/user_guide/#troubleshooting)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

## 🚨 Emergency Procedures

### **When All Else Fails**

#### **1. Complete Reset**

```bash
# 1. Delete virtual environment
rm -rf venv/

# 2. Clear pip cache
pip cache purge

# 3. Reinstall Python completely
# 4. Create fresh environment
```

#### **2. Alternative Python**

```bash
# Use system Python or alternative installation
# Install packages globally (not recommended but functional)
python -m pip install --user package_name
```

#### **3. Container Approach**

```bash
# Use Docker for isolated environment
docker run -it --rm -v ${PWD}:/app -w /app python:3.12 bash
pip install -r requirements.txt
python tools/mcp_cli.py servers
```

---

**Last Updated**: 2025-09-03
**Version**: 0.2.0
**Status**: Critical Issues Identified - Environment Problems
**Next Action**: Fix Python Environment Immediately
