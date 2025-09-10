# 🚀 Chonost MCP Tools System

## 📋 Overview

ระบบ MCP Tools ที่รองรับ 16 ค่ายพร้อม JSON Schema และ VS Code Extension แบบครบวงจร

## 🏗️ Architecture

```
chonost-mcp/
├── tools.schema.json              # JSON Schema กลาง
├── tools.instance.json            # ไฟล์ตัวอย่าง tools
├── packages/vscode-ext/           # VS Code Extension
│   ├── package.json
│   ├── src/extension.ts
│   └── tsconfig.json
├── scripts/
│   └── generate_chatgpt_functions.py
└── docs/
    └── MCP_TOOLS_README.md
```

## 🎯 Features

### ✅ **16 Tool Categories**

1. **filesystem** - ค้นหาและจัดการไฟล์
2. **github** - จัดการ GitHub repositories
3. **notion** - จัดการ Notion databases
4. **slack** - จัดการ Slack channels
5. **google-drive** - จัดการ Google Drive
6. **google-calendar** - จัดการ Google Calendar
7. **gmail** - จัดการ Gmail
8. **jira** - จัดการ Jira projects
9. **confluence** - จัดการ Confluence spaces
10. **linear** - จัดการ Linear issues
11. **airtable** - จัดการ Airtable bases
12. **trello** - จัดการ Trello boards
13. **pdf-tools** - จัดการ PDF files
14. **web-browsing** - จัดการ web content
15. **vector-db** - จัดการ vector databases
16. **llm-router** - จัดการ LLM routing

### ✅ **Common Options**

ทุกทูลรองรับพารามิเตอร์ร่วม:

- `dry_run`: รันแบบทดสอบ
- `timeout_s`: เวลาหมดอายุ
- `job_mode`: โหมดงาน (sync/async)
- `idempotency_key`: คีย์ป้องกันการทำงานซ้ำ
- `cursor`: สำหรับ pagination

## 🛠️ Usage

### 1. **VS Code Extension**

#### **Installation**

1. Clone repository
2. Navigate to `packages/vscode-ext/`
3. Run `npm install`
4. Run `npm run compile`
5. Press F5 to launch extension development host

#### **Commands**

- `Chonost: Run Tool` - รันทูลตาม ID
- `Chonost: Pick & Run Tool` - เลือกทูลจากรายการ
- `Chonost: List Available Tools` - แสดงรายการทูล

#### **Configuration**

```json
{
  "chonost.orchestratorUrl": "http://localhost:8000",
  "chonost.toolsSchemaPath": "${workspaceFolder}/tools.schema.json"
}
```

### 2. **Direct API Calls**

#### **List Tools**

```bash
curl -X POST http://localhost:8000/mcp/tools \
  -H "Content-Type: application/json" \
  -d '{"server": "filesystem"}'
```

#### **Execute Tool**

```bash
curl -X POST http://localhost:8000/mcp/call \
  -H "Content-Type: application/json" \
  -d '{
    "server": "filesystem",
    "tool": "fs.semantic_search",
    "arguments": {
      "query": "authentication",
      "top_k": 10,
      "dry_run": false
    }
  }'
```

### 3. **VS Code Tasks**

สร้าง tasks ใน `.vscode/tasks.json`:

```json
{
  "label": "MCP: fs.semantic_search",
  "type": "shell",
  "command": "curl",
  "args": [
    "-sS",
    "-X",
    "POST",
    "${config:chonost.orchestratorUrl}/mcp/call",
    "-H",
    "content-type: application/json",
    "-d",
    "{\"server\":\"filesystem\",\"tool\":\"fs.semantic_search\",\"arguments\":{\"query\":\"${input:searchQuery}\"}}"
  ]
}
```

## 🔧 Development

### **Adding New Tools**

1. **Update Schema** - เพิ่มใน `tools.schema.json`
2. **Update Instance** - เพิ่มใน `tools.instance.json`
3. **Update Registry** - เพิ่มใน `services/orchestrator/mcp/registry.py`

#### **Example: New Tool**

```json
{
  "$defs": {
    "fs.new_tool": {
      "allOf": [
        { "$ref": "#/$defs/CommonOptions" },
        {
          "type": "object",
          "required": ["param1"],
          "properties": {
            "param1": { "type": "string", "description": "Description" }
          }
        }
      ]
    }
  }
}
```

### **Schema Validation**

VS Code จะ validate `tools.schema.json` อัตโนมัติผ่าน JSON validation

### **TypeScript Types**

Extension ใช้ TypeScript interfaces สำหรับ type safety

## 🤖 ChatGPT Integration

### **Generate Function Definitions**

```bash
python scripts/generate_chatgpt_functions.py
```

### **Output Files**

- `chatgpt_functions.json` - JSON format
- `chatgpt_functions.py` - Python format

### **Usage in ChatGPT**

```python
from chatgpt_functions import CHATGPT_FUNCTIONS

# Send to ChatGPT
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Search for authentication code"}],
    functions=CHATGPT_FUNCTIONS,
    function_call="auto"
)
```

## 📊 Tool Examples

### **1. Filesystem Tools**

#### **Semantic Search**

```json
{
  "tool_id": "fs.semantic_search",
  "arguments": {
    "query": "authentication middleware",
    "top_k": 20,
    "include_globs": ["src/**/*.ts", "src/**/*.js"],
    "exclude_globs": ["node_modules/**", "dist/**"]
  }
}
```

#### **Pattern Extract**

```json
{
  "tool_id": "fs.pattern_extract",
  "arguments": {
    "pattern": "function\\s+\\w+\\s*\\([^)]*\\)\\s*\\{",
    "lang": "typescript",
    "paths": ["src/core/**/*.ts"]
  }
}
```

### **2. GitHub Tools**

#### **Create Smart PR**

```json
{
  "tool_id": "gh.pr_create_smart",
  "arguments": {
    "repo": "chonost/chonost-mcp",
    "base": "main",
    "head": "feature/new-tools",
    "title": "feat: Add new MCP tools",
    "auto_labels": true
  }
}
```

### **3. Web Tools**

#### **Fetch Readable Content**

```json
{
  "tool_id": "web.fetch_readable",
  "arguments": {
    "url": "https://example.com/article",
    "strip_selectors": [".ads", ".sidebar"]
  }
}
```

## 🚀 Advanced Features

### **Async Job Mode**

```json
{
  "tool_id": "fs.semantic_search",
  "arguments": {
    "query": "large search query",
    "job_mode": "async",
    "timeout_s": 300
  }
}
```

### **Dry Run Mode**

```json
{
  "tool_id": "gh.pr_create_smart",
  "arguments": {
    "repo": "owner/repo",
    "base": "main",
    "head": "feature",
    "dry_run": true
  }
}
```

### **Idempotency**

```json
{
  "tool_id": "fs.refactor_batch",
  "arguments": {
    "rules": [...],
    "idempotency_key": "refactor-2024-01-01"
  }
}
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Schema Validation Errors**

   - ตรวจสอบ JSON syntax
   - ตรวจสอบ $ref paths
   - ใช้ VS Code JSON validation

2. **Extension Not Working**

   - ตรวจสอบ configuration
   - ตรวจสอบ orchestrator URL
   - ตรวจสอบ tools.schema.json path

3. **Tool Execution Failed**
   - ตรวจสอบ server availability
   - ตรวจสอบ tool parameters
   - ตรวจสอบ orchestrator logs

### **Debug Mode**

เปิด Developer Tools ใน VS Code เพื่อดู console logs

## 📚 Resources

### **Documentation**

- [JSON Schema Specification](https://json-schema.org/)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [MCP Protocol](https://modelcontextprotocol.io/)

### **Examples**

- `tools.instance.json` - ตัวอย่างการใช้งาน
- `packages/vscode-ext/` - Extension source code
- `scripts/` - Utility scripts

## 🎉 Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

---

**Status**: Ready for Development
**Version**: 0.1.0
**Last Updated**: 2025-09-03

