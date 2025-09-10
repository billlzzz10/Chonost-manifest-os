# 🔄 FileSystemMCP Project Refactor Plan

## 📋 เป้าหมาย

ปรับโครงสร้างโปรเจกต์ให้เป็นมาตรฐานและสามารถขยายขนาดได้ง่ายในอนาคต

## 🏗️ โครงสร้างเป้าหมาย

```
FileSystemMCP/
├── .github/                    # GitHub Actions และ workflows
├── .cursor/                    # Cursor Rules (มีอยู่แล้ว)
├── alembic/                    # Database migrations (มีอยู่แล้ว)
├── docs/                       # 📁 เอกสารทั้งหมด
├── scripts/                    # 📁 Scripts (.ps1, .bat)
├── src/                        # 📁 โค้ดหลัก
│   ├── main.py                 # Entry point หลัก
│   ├── core/                   # Core logic
│   ├── apps/                   # Chat Applications
│   ├── server/                 # Universal MCP Server และ AI Orchestrator
│   ├── agents/                 # AI Agent Ecosystem
│   └── utils/                  # ฟังก์ชันที่ใช้ร่วมกัน
├── tests/                      # 📁 Test files
├── datasets/                   # 📁 Dataset files (.json)
├── .gitignore
├── README.md                   # README หลัก
├── requirements.txt
└── pyproject.toml             # 📄 ใหม่ - จัดการ dependencies
```

## 📦 แผนการย้ายไฟล์

### **Phase 1: สร้างโครงสร้างพื้นฐาน** - ✅ สร้างโฟลเดอร์ใหม่ (src, scripts, tests, docs, datasets)
- ✅ สร้างโฟลเดอร์ย่อยใน src

### ** Phase 2: ย้ายไฟล์ Core Logic**

* * จาก root → src/core/**

- ` file_system_analyzer.py` → ` src/core/file_system_analyzer.py`
- ` ai_ready_analyzer.py` → ` src/core/ai_ready_analyzer.py`
- ` smart_analyzer.py` → ` src/core/smart_analyzer.py`

### ** Phase 3: ย้าย Chat Applications**

* * จาก root → src/apps/**

- ` desktop_chat_app.py` → ` src/apps/desktop_chat_app.py`
- ` advanced_chat_app.py` → ` src/apps/advanced_chat_app.py`
- ` ai_enhanced_chat_app.py` → ` src/apps/ai_enhanced_chat_app.py`
- ` unified_chat_app.py` → ` src/apps/unified_chat_app.py`

### ** Phase 4: ย้าย Server Components**

* * จาก root → src/server/**

- ` universal_fs_mcp_server.py` → ` src/server/universal_fs_mcp_server.py`
- ` ai_orchestrator_* .py` → ` src/server/ai_orchestrator/`
- ` mcp_server.py` → ` src/server/mcp_server.py`
- ` file_system_mcp_api.py` → ` src/server/file_system_mcp_api.py`

### **Phase 5: ย้าย AI Agent Ecosystem**

* * จาก root → src/agents/**

- ` agent_model_config.py` → ` src/agents/agent_model_config.py`
- ` crewai_with_ollama.py` → ` src/agents/crewai_with_ollama.py`

### ** Phase 6: ย้าย Utilities**

* * จาก root → src/utils/**

- ` ollama_client.py` → ` src/utils/ollama_client.py`
- ` dataset_generator.py` → ` src/utils/dataset_generator.py`

### ** Phase 7: ย้าย Scripts**

* * จาก root → scripts/**

- ` start-* .ps1` → ` scripts/`
- ` run.ps1` → ` scripts/`
- ` run.bat` → ` scripts/`
- ` test-* .ps1` → ` scripts/`

### **Phase 8: ย้าย Tests**

* * จาก root → tests/**

- ` test_* .py` → ` tests/`

### **Phase 9: ย้าย Datasets**

* * จาก root → datasets/**

- ` * .json` (dataset files) → ` datasets/`

### **Phase 10: ย้าย Documentation**

* * จาก root → docs/**

- ` * _README.md` → ` docs/`
- ` * _SUMMARY.md` → ` docs/`
- ` PROJECT_STATUS.md` → ` docs/`
- ` SETUP_COMPLETE.md` → ` docs/`
- ` VAULT_SCAN_REPORT.md` → ` docs/`

## 🔧 การปรับปรุงที่จำเป็น

### **1. สร้าง main.py** ```python
# src/main.py
"""
FileSystemMCP - Main Entry Point
"""
from src.apps.unified_chat_app import main as run_chat_app
from src.server.universal_fs_mcp_server import main as run_mcp_server
from src.agents.crewai_with_ollama import main as run_agent_ecosystem

def main():
    """Main entry point"""
    # TODO: Add CLI argument parsing
    pass

if __name__ == "__main__":
    main()
```

### ** 2. สร้าง pyproject.toml** ```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "filesystem-mcp"
version = "3.0.0"
description = "File System MCP Tool with AI Integration"
authors = [{name = "Orion Senior Dev", email = "orion@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "requests>=2.31.0",
    "sqlalchemy>=2.0.0",
    "fastapi>=0.104.0",
    "crewai>=0.28.0",
    "langchain>=0.1.0",
    "ollama>=0.1.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.11.0",
    "flake8>=6.1.0",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_* .py"]
```

### **3. อัปเดต imports** - แก้ไข import paths ในทุกไฟล์
- เพิ่ม ` __init__.py` ในทุกโฟลเดอร์
- อัปเดต relative imports

### ** 4. อัปเดต Scripts** - แก้ไข paths ใน PowerShell scripts
- อัปเดต launcher scripts

## 📊 สถานะการ Refactor

### ** ✅ เสร็จสิ้น:** - [x] สร้างโครงสร้างโฟลเดอร์ใหม่
- [x] วางแผนการย้ายไฟล์

### ** 🔄 กำลังดำเนินการ:** - [ ] ย้ายไฟล์ Core Logic
- [ ] ย้าย Chat Applications
- [ ] ย้าย Server Components
- [ ] ย้าย AI Agent Ecosystem
- [ ] ย้าย Utilities
- [ ] ย้าย Scripts
- [ ] ย้าย Tests
- [ ] ย้าย Datasets
- [ ] ย้าย Documentation

### ** ⏳ รอการดำเนินการ:** - [ ] สร้าง main.py
- [ ] สร้าง pyproject.toml
- [ ] อัปเดต imports
- [ ] อัปเดต scripts
- [ ] ทดสอบการทำงาน
- [ ] อัปเดต documentation

## 🎯 ประโยชน์ที่คาดหวัง

### ** การจัดการที่ดีขึ้น:** - 📁 โครงสร้างที่ชัดเจนและเป็นมาตรฐาน
- 🔍 ค้นหาไฟล์ได้ง่าย
- 🧹 แยกส่วนการทำงานชัดเจน

### ** การขยายขนาด:** - 🚀 เพิ่มฟีเจอร์ใหม่ได้ง่าย
- 🔧 แก้ไขและบำรุงรักษาง่าย
- 📦 ติดตั้งและ deploy ได้ง่าย

### ** การทำงานเป็นทีม:** - 👥 เข้าใจโครงสร้างได้ง่าย
- 📚 เอกสารที่จัดระเบียบ
- 🧪 การทดสอบที่เป็นระบบ

- --

* * สร้างโดย**: Orion Senior Dev / Pair Programmer
* * วันที่**: 21 สิงหาคม 2024
* * สถานะ**: กำลังดำเนินการ

