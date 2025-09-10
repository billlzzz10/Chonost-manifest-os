# 🔧 Environment Recovery Guide - MCP Orchestrator

## 📋 Overview

เอกสารนี้ครอบคลุมขั้นตอนการกู้คืน Python environment สำหรับ MCP Orchestrator v0.2.0

## 🚨 Current Status: CRITICAL

### **Environment Issues Identified**

- Python environment corruption
- Packages cannot be imported after installation
- pip install succeeds but import fails
- System blocking MCP Orchestrator usage

### **Impact Assessment**

- **Severity**: Critical
- **Scope**: Complete system unusable
- **Business Impact**: Development and testing blocked
- **User Impact**: Cannot use MCP Orchestrator features

## 🎯 Recovery Objectives

### **Primary Goals**

1. **Restore Python Environment**: Fix Python environment functionality
2. **Install Dependencies**: Install all required packages
3. **Validate System**: Ensure MCP Orchestrator works
4. **Resume Development**: Continue development and testing

### **Success Criteria**

- [ ] Python environment functions normally
- [ ] All required packages can be imported
- [ ] MCP Orchestrator starts successfully
- [ ] CLI commands work properly
- [ ] FastAPI server responds to requests
- [ ] pytest runs without errors

## 🔧 Recovery Procedures

### **Phase 1: Environment Diagnosis**

#### **1.1 System Assessment**

```bash
# Check Python installation
python --version
python -c "import sys; print(sys.executable)"

# Check pip functionality
pip --version
pip list

# Check environment variables
echo $PYTHONPATH
echo $PYTHONHOME
```

#### **1.2 Problem Identification**

```bash
# Test package installation
pip install --dry-run pytest

# Test package import
python -c "import pytest; print('pytest OK')"

# Check site-packages
python -c "import site; print(site.getsitepackages())"
```

#### **1.3 Root Cause Analysis**

- **Python Installation**: Corrupted or misconfigured
- **Environment Variables**: Conflicts or missing
- **Package Manager**: pip configuration issues
- **System Dependencies**: Missing system libraries

### **Phase 2: Environment Recovery**

#### **2.1 Option A: Complete Python Reinstall (Recommended)**

##### **Step 1: Backup Current Setup**

```bash
# Backup current Python configuration
pip freeze > requirements_backup.txt
python -c "import sys; print(sys.path)" > python_path_backup.txt
```

##### **Step 2: Uninstall Current Python**

```bash
# Windows
# 1. Control Panel > Programs > Uninstall
# 2. Remove Python 3.x
# 3. Delete remaining Python directories
# 4. Clean PATH environment variable
```

##### **Step 3: Download Fresh Python**

```bash
# Download Python 3.12+ from python.org
# Ensure "Add to PATH" option is selected
# Install for all users (recommended)
```

##### **Step 4: Verify Installation**

```bash
# Test Python
python --version
python -c "print('Hello, World!')"

# Test pip
pip --version
pip list
```

#### **2.2 Option B: Environment Repair (Alternative)**

##### **Step 1: Fix Environment Variables**

```bash
# Set correct Python path
set PYTHONPATH=C:\Python312\Lib\site-packages
set PYTHONHOME=C:\Python312

# Add Python to PATH
set PATH=%PATH%;C:\Python312;C:\Python312\Scripts
```

##### **Step 2: Reinstall Critical Packages**

```bash
# Force reinstall core packages
pip install --force-reinstall --no-cache-dir pip setuptools wheel

# Install required packages
pip install --force-reinstall --no-cache-dir pytest pytest-asyncio uvicorn fastapi
```

##### **Step 3: Verify Package Installation**

```bash
# Test each package
python -c "import pytest; print('pytest OK')"
python -c "import pytest_asyncio; print('pytest-asyncio OK')"
python -c "import uvicorn; print('uvicorn OK')"
python -c "import fastapi; print('fastapi OK')"
```

#### **2.3 Option C: Virtual Environment Approach**

##### **Step 1: Create Fresh Virtual Environment**

```bash
# Remove old environment
rm -rf venv/

# Create new environment
python -m venv venv_new

# Activate environment
venv_new\Scripts\activate
```

##### **Step 2: Install Dependencies**

```bash
# Upgrade pip
pip install --upgrade pip

# Install core packages
pip install fastapi uvicorn pydantic structlog click

# Install testing packages
pip install pytest pytest-asyncio pytest-cov httpx

# Install development packages
pip install black ruff mypy
```

##### **Step 3: Verify Environment**

```bash
# Check installed packages
pip list

# Test imports
python -c "import fastapi, uvicorn, pytest; print('All packages OK')"
```

### **Phase 3: System Validation**

#### **3.1 Core Component Testing**

##### **Test MCP Orchestrator Components**

```bash
# Test registry
python -c "from services.orchestrator.mcp.registry import REGISTRY; print('Registry OK')"

# Test client
python -c "from services.orchestrator.mcp.client import MCPClient; print('Client OK')"

# Test pool
python -c "from services.orchestrator.mcp.pool import MCPPool; print('Pool OK')"

# Test main app
python -c "from services.orchestrator.main import app; print('FastAPI OK')"
```

##### **Test CLI Functionality**

```bash
# Test CLI help
python tools/mcp_cli.py --help

# Test specific commands
python tools/mcp_cli.py servers
python tools/mcp_cli.py health
python tools/mcp_cli.py config
```

#### **3.2 FastAPI Server Testing**

##### **Start Server**

```bash
# Start server in background
start /B python -c "from services.orchestrator.main import run_app; run_app()"

# Wait for server to start
timeout 5

# Test server response
curl localhost:8000/health
curl localhost:8000/mcp/servers
```

##### **Verify Endpoints**

```bash
# Test health endpoint
curl -s localhost:8000/health | jq .

# Test servers endpoint
curl -s localhost:8000/mcp/servers | jq .

# Test specific server
curl -s localhost:8000/mcp/servers/filesystem | jq .
```

#### **3.3 Testing Framework Validation**

##### **Test pytest Installation**

```bash
# Check pytest
pytest --version

# Check pytest-asyncio
python -c "import pytest_asyncio; print('pytest-asyncio OK')"

# Run basic collection
pytest --collect-only
```

##### **Run Test Suite**

```bash
# Run basic tests
pytest tests/ -v

# Run specific test file
pytest tests/test_mcp_hard.py -v

# Run with coverage
pytest tests/ --cov=services.orchestrator --cov-report=html
```

### **Phase 4: Post-Recovery Actions**

#### **4.1 Environment Documentation**

```bash
# Document working environment
python --version > environment_info.txt
pip freeze > requirements_working.txt
python -c "import sys; print(sys.path)" >> environment_info.txt
```

#### **4.2 Prevention Measures**

```bash
# Create environment backup script
echo "pip freeze > requirements_backup.txt" > backup_env.bat
echo "python -c \"import sys; print(sys.path)\" > python_path_backup.txt" >> backup_env.bat

# Set up regular backups
# Add to crontab or Windows Task Scheduler
```

#### **4.3 Monitoring Setup**

```bash
# Create health check script
echo "python -c \"import fastapi, uvicorn, pytest; print('Environment OK')\"" > health_check.bat

# Set up automated health checks
# Run every hour during development
```

## 🚨 Emergency Procedures

### **When Recovery Fails**

#### **1. Alternative Python Installation**

```bash
# Use system Python or alternative installation
# Install packages globally (not recommended but functional)
python -m pip install --user package_name
```

#### **2. Container Approach**

```bash
# Use Docker for isolated environment
docker run -it --rm -v ${PWD}:/app -w /app python:3.12 bash
pip install -r requirements.txt
python tools/mcp_cli.py servers
```

#### **3. Cloud Development Environment**

```bash
# Use GitHub Codespaces or similar
# Provides clean Python environment
# No local environment issues
```

## 📊 Recovery Timeline

### **Estimated Recovery Time**

- **Environment Diagnosis**: 1-2 hours
- **Environment Recovery**: 2-4 hours
- **System Validation**: 1-2 hours
- **Post-Recovery Setup**: 1 hour

### **Total Estimated Time**: 5-9 hours

### **Critical Path Items**

1. **Python Reinstallation**: 2-3 hours
2. **Dependency Installation**: 1-2 hours
3. **System Testing**: 1-2 hours

## 🔍 Troubleshooting Tips

### **Common Recovery Issues**

#### **1. Permission Denied**

```bash
# Run as Administrator (Windows)
# Use sudo (Linux/macOS)
# Check file permissions
```

#### **2. Port Already in Use**

```bash
# Check port usage
netstat -an | findstr :8000

# Kill processes
taskkill /f /im python.exe
```

#### **3. Import Path Issues**

```bash
# Add project root to Python path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### **4. Package Conflicts**

```bash
# Check package compatibility
pip check

# Resolve conflicts
pip install --upgrade package_name
```

## 📚 Additional Resources

### **Documentation**

- [Python Installation Guide](https://docs.python.org/3/using/index.html)
- [pip User Guide](https://pip.pypa.io/en/stable/user_guide/)
- [Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### **Community Support**

- [Python Discord](https://discord.gg/python)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/python)
- [Python Reddit](https://www.reddit.com/r/Python/)

### **Professional Support**

- [Python Software Foundation](https://www.python.org/psf/)
- [Local Python User Groups](https://wiki.python.org/moin/LocalUserGroups)

---

**Last Updated**: 2025-09-03
**Version**: 0.2.0
**Status**: Environment Recovery Required
**Priority**: Critical
**Next Action**: Execute Environment Recovery Procedure
