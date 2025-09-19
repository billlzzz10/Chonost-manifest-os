# Contributing to Chonost Manuscript OS

ขอบคุณสำหรับความสนใจในการมีส่วนร่วมกับ Chonost Manuscript OS! โครงการนี้มุ่งเน้นที่การพัฒนา AI orchestration system ด้วย RAG features และ MCP extensions. เราให้การต้อนรับ contributions ที่ช่วยปรับปรุง maintainability, features, และ documentation.

## Overview

- **Fork the repo**: สร้าง fork จาก https://github.com/user/chonost
- **Create branch**: ใช้ branch name ที่ชัดเจน เช่น `feature/add-rag-handler` หรือ `fix/lint-errors`
- **Test locally**: ตรวจสอบ code ทำงานได้ก่อน push
- **Submit PR**: อธิบาย changes ใน PR description รวมถึง test results และ motivation

Contributions ควร align กับ roadmap ใน [DEVELOPMENT_ROADMAP.md](chonost-unified/backend/mcp/docs/DEVELOPMENT_ROADMAP.md).

## Setup Development Environment

1. **Clone and setup**:
   ```
   git clone https://github.com/user/chonost.git
   cd chonost
   # Backend (Python)
   pip install -r packages/backend/requirements_roadmap.txt
   # Frontend (TypeScript)
   npm install
   # Copy env
   cp .env.example .env
   # Configure API keys (OpenAI, Notion, etc.)
   ```

2. **Run services**:
   ```
   # Docker compose for full stack
   docker-compose up -d
   # Or individual services
   python scripts/start_backend.py
   npm run dev  # สำหรับ frontend
   ```

3. **Verify setup**:
   - Run `pytest tests/` เพื่อตรวจ unit tests
   - Access `http://localhost:3000` เพื่อ test frontend
   - Check CI badges ใน [README.md](README.md) สำหรับ status

ดูรายละเอียดเพิ่มใน [ENV_SETUP_GUIDE.md](chonost-unified/backend/mcp/docs/ENV_SETUP_GUIDE.md).

## Adding Features

Contributions สำหรับ new features ควร focus ที่ RAG enhancements, MCP tools, หรือ integrations. ตัวอย่าง: Adding RAG feature

1. **Update core files**: Modify `handlers.py` (หรือ relevant Python files ใน core-services/link-ai-core/) เพื่อ add new RAG logic เช่น vector search integration.
2. **Add tests**: สร้าง test cases ใน `tests/e2e/test_rag_flow.py` หรือ `tests/integration/`
   - Example: `def test_new_rag_handler(): assert response.contains("relevant docs")`
3. **Update docs**: Add usage examples ใน `examples/` และ update [MCP_TOOLS_README.md](chonost-unified/backend/mcp/docs/MCP_TOOLS_README.md)
4. **For MCP extensions**: Update `mcp.json` schema และ add handlers ใน `core-services/link-ai-core/scripts/`

ใช้ [DEVELOPMENT_STANDARDS_SUMMARY.md](chonost-unified/backend/mcp/docs/DEVELOPMENT_STANDARDS_SUMMARY.md) สำหรับ architecture guidelines.

## Code Style

- **Python**: Use [Black](https://black.readthedocs.io/) สำหรับ formatting: `black .`
  - Type checking ด้วย [mypy](https://mypy-lang.org/): `mypy .`
  - Linting ด้วย flake8 หรือ ruff
- **TypeScript**: Use ESLint: `npm run lint`
  - Prettier สำหรับ formatting: `npm run format`
  - TypeScript strict mode ใน `tsconfig.json`
- **General**: Follow PEP8 สำหรับ Python, Airbnb style สำหรับ JS/TS. Run `pre-commit install` ถ้ามี hooks.

ตรวจสอบก่อน commit: `black . && mypy . && npm run lint && npm run format`

## Testing and PR Process

1. **Run tests**:
   - Unit/Integration: `pytest tests/ -v`
   - Load testing: `locust -f tests/load/locustfile.py`
   - E2E: `python scripts/comprehensive_testing.py`
   - Coverage: `pytest --cov` (target >90%)

2. **Lint and format**: ตรวจสอบ code style ตามด้านบน

3. **Before push**:
   - Ensure no breaking changes (test locally)
   - Update CHANGELOG.md ถ้ามี significant changes
   - Run CI locally ถ้า possible (ดู [.github/workflows/roadmap.yml](.github/workflows/roadmap.yml))

4. **Submit PR**:
   - Target `main` branch
   - Include: Description ของ changes, test results, screenshots ถ้ามี UI changes
   - Reference issues: `Fixes #123`
   - Wait สำหรับ CI pass (badges ใน PR)

PR จะ reviewed โดย maintainers. เราจะ merge หลังจาก approve และ rebase ถ้าจำเป็น.

## Questions?

เปิด issue ใน repo หรือ comment ใน PR. สำหรับ urgent, ping ใน GitHub discussions.

ขอบคุณสำหรับ contributions ของคุณ!