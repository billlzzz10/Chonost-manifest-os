# 🚀 Notion AI Server - AI-Accessible Notion MCP Integration

## 📋 Overview

Notion AI Server เป็นระบบเซิร์ฟเวอร์ที่ AI สามารถเรียกใช้งาน Notion MCP Integration ได้โดยตรงผ่าน HTTP API แทนที่จะต้องรันผ่าน command line

## 🏗️ Architecture

```
┌─────────────────┐    HTTP API    ┌──────────────────┐    MCP Protocol    ┌─────────────┐
│   AI Client     │ ──────────────► │  Notion AI       │ ──────────────────► │  Notion     │
│                 │                 │  Server          │                    │  MCP Server │
│ • HTTP Client   │                 │ • FastAPI        │                    │ • Docker    │
│ • AI Helper     │                 │ • REST API       │                    │ • Container │
└─────────────────┘                 └──────────────────┘                    └─────────────┘
```

## 🚀 Quick Start

### 1. Start Notion AI Server

```
# ใช้ PowerShell script
.\scripts\start-notion-mcp-server.ps1

# หรือระบุพอร์ตและโทเค็น
.\scripts\start-notion-mcp-server.ps1 -Port 8080 -Token "ntn_your_token"
```

### 2. AI สามารถเรียกใช้งานได้ทันที

```
import asyncio
from src.ai.notion_ai_integration import NotionAIIntegration

async def main():
    # Initialize AI integration
    integration = NotionAIIntegration()
    await integration.initialize("ntn_your_token")

    # Analyze and export file
    result = await integration.analyze_and_export_file(
        file_path="src/server/notion_mcp_integration.py",
        parent_page_id="your_page_id",
        analysis_type="detailed"
    )

    print(result)

asyncio.run(main())
```

## 📚 API Endpoints

### Health Check
```
GET /health
```

### Initialize Notion
```
POST /api/v1/notion/init
Content-Type: application/json

{
  "token": "ntn_your_notion_token"
}
```

### Create Page
```
POST /api/v1/notion/pages
Content-Type: application/json

{
  "parent_id": "page_id",
  "properties": {
    "title": {
      "title": [
        {
          "text": {
            "content": "Page Title"
          }
        }
      ]
    }
  }
}
```

### Create Database
```
POST /api/v1/notion/databases
Content-Type: application/json

{
  "parent_id": "page_id",
  "title": "Database Title",
  "properties": {
    "Name": {
      "title": {}
    }
  }
}
```

### Export File Structure
```
POST /api/v1/notion/export/file-structure
Content-Type: application/json

{
  "file_structure": {
    "name": "file.py",
    "type": "file",
    "path": "/path/to/file.py",
    "size": 1024,
    "modified": 1234567890,
    "children": []
  },
  "parent_page_id": "page_id"
}
```

### Query Database
```
POST /api/v1/notion/databases/{database_id}/query
Content-Type: application/json

{
  "filter": {
    "property": "Name",
    "title": {
      "contains": "search_term"
    }
  }
}
```

### Search Pages
```
POST /api/v1/notion/search
Content-Type: application/json

{
  "query": "search query",
  "filter": {
    "property": "object",
    "value": "page"
  }
}
```

## 🤖 AI Integration Features

### 1. File Analysis
```
# Basic analysis
result = await integration.analyze_and_export_file(
    file_path="file.py",
    parent_page_id="page_id",
    analysis_type="basic"
)

# Detailed analysis
result = await integration.analyze_and_export_file(
    file_path="file.py",
    parent_page_id="page_id",
    analysis_type="detailed"
)

# Code analysis
result = await integration.analyze_and_export_file(
    file_path="file.py",
    parent_page_id="page_id",
    analysis_type="code"
)
```

### 2. Batch Directory Analysis
```
# Analyze entire directory
result = await integration.batch_analyze_directory(
    directory_path="src",
    parent_page_id="page_id",
    file_patterns=["*.py", "* .md"],
    analysis_type="detailed"
)
```

### 3. Project Documentation
```
# Create comprehensive project documentation
result = await integration.create_project_documentation(
    project_path=".",
    parent_page_id="page_id",
    include_analysis=True
)
```

## 🔧 Configuration

### Environment Variables
```
# Required
NOTION_INTEGRATION_TOKEN=ntn_your_token

# Optional
NOTION_PARENT_PAGE_ID=your_page_id
NOTION_DATABASE_ID=your_database_id
```

### Server Configuration
```
{
  "mcpServers": {
    "notion": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "-e", "INTERNAL_INTEGRATION_TOKEN", "mcp/notion"],
      "env": {
        "INTERNAL_INTEGRATION_TOKEN": "ntn_****"
      }
    }
  },
  "notionSettings": {
    "defaultParentPageId": "",
    "fileAnalysisDatabaseId": "",
    "autoExportEnabled": true,
    "exportFormat": "structured",
    "syncInterval": 300,
    "maxFileSize": 10485760,
    "supportedFileTypes": [".py", ".js", ".ts", ".md", ".json"]
  }
}
```

## 📊 File Analysis Types

### Basic Analysis
- File name, path, type
- File size and modification date
- Basic metadata

### Detailed Analysis
- Line count, word count, character count
- File type specific analysis
- Content statistics

### Code Analysis
- Import statements
- Function and class counts
- Language-specific metrics
- Code structure analysis

## 🛠 ️ Desktop Commander Integration

### Using Desktop Commander Tools

```
# Start Notion AI Server
start_process -command "powershell" -arguments "-ExecutionPolicy Bypass -File scripts/start-notion-mcp-server.ps1"

# Run AI integration
start_process -command "python" -arguments "src/ai/notion_ai_integration.py"

# Monitor processes
 list_processes | where-object { $_.ProcessName -like "* python* " }

# Read logs
read_file -path "logs/notion_mcp_server.log"
```

### AI Helper Functions
```
# Initialize with Desktop Commander
integration = NotionAIIntegration("http://localhost:8000")
await integration.initialize(token)

# Export file analysis
result = await integration.analyze_and_export_file(
    file_path="path/to/file.py",
    parent_page_id="page_id"
)

# Batch process directory
result = await integration.batch_analyze_directory(
    directory_path="src",
    parent_page_id="page_id"
)
```

## 🔍 Monitoring and Logging

### Log Files
- ` logs/notion_mcp_server.log` - Server logs
- ` logs/notion_ai_integration.log` - AI integration logs

### Health Check
```
GET http://localhost:8000/health
```

Response:
```
{
  "status": "running",
  "notion_connected": true,
  "docker_running": true,
  "uptime": 3600.5
}
```

## 🚨 Error Handling

### Common Errors

1. **Token Not Found** ```json
   {
     "success": false,
     "message": "❌ NOTION_INTEGRATION_TOKEN not found",
     "error": "Token not provided"
   }
   ```

2. ** Docker Not Running** ```json
   {
     "success": false,
     "message": "❌ Docker is not running",
     "error": "Docker container failed to start"
   }
   ```

3. ** File Not Found** ```json
   {
     "success": false,
     "message": "❌ File not found: /path/to/file",
     "error": "File does not exist"
   }
   ```

### Troubleshooting

1. ** Server Won't Start** - Check Python installation
   - Verify Docker is running
   - Check port availability

2. ** Connection Failed** - Verify server URL
   - Check firewall settings
   - Ensure server is running

3. ** Notion API Errors** - Verify integration token
   - Check page/database permissions
   - Ensure proper Notion setup

## 📈 Performance

### Optimization Tips

1. ** Batch Operations** - Use batch_analyze_directory for multiple files
   - Group related operations

2. ** Caching** - Server caches Docker container status
   - Reuse client sessions when possible

3. ** Resource Management** - Clean up resources after use
   - Monitor memory usage for large files

### Benchmarks
- Single file analysis: ~1-2 seconds
- Directory analysis (100 files): ~30-60 seconds
- Project documentation: ~2-5 minutes

## 🔐 Security

### Best Practices

1. ** Token Management** - Use environment variables
   - Never commit tokens to version control
   - Rotate tokens regularly

2. ** Access Control** - Limit server access to trusted networks
   - Use HTTPS in production
   - Implement authentication if needed

3. ** File Access** - Validate file paths
   - Limit file size uploads
   - Sanitize file content

## 🚀 Deployment

### Production Setup

1. ** Environment** ```bash
   # Set production environment
   export NODE_ENV=production
   export NOTION_INTEGRATION_TOKEN=ntn_production_token
   ```

2. ** Server Configuration** ```python
   # Use production settings
   uvicorn.run(
       "notion_mcp_server:app",
       host="0.0.0.0",
       port=8000,
       reload=False,  # Disable reload in production
       log_level="info"
   )
   ```

3. ** Process Management** ```bash
   # Use process manager
   pm2 start src/server/notion_mcp_server.py --name "notion-mcp-server"
   ```

## 📚 Examples

### Complete AI Workflow
```
import asyncio
from src.ai.notion_ai_integration import NotionAIIntegration

async def ai_workflow():
    # Initialize
    integration = NotionAIIntegration()
    await integration.initialize("ntn_your_token")

    try:
        # 1. Create project documentation
        doc_result = await integration.create_project_documentation(
            project_path=".",
            parent_page_id="your_page_id"
        )

        # 2. Analyze specific files
        for file_path in ["main.py", "config.json", "README.md"]:
            result = await integration.analyze_and_export_file(
                file_path=file_path,
                parent_page_id="your_page_id",
                analysis_type="detailed"
            )
            print(f"Analyzed {file_path}: {result['success']}")

        # 3. Batch analyze source code
        batch_result = await integration.batch_analyze_directory(
            directory_path="src",
            parent_page_id="your_page_id",
            file_patterns=["* .py"],
            analysis_type="code"
        )

        print(f"Batch analysis: {batch_result['data']['successful']} successful")

    finally:
        await integration.cleanup()

# Run workflow
asyncio.run(ai_workflow())
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check this README and API docs
- ** Issues**: Create GitHub issue
- ** Discussions**: Use GitHub Discussions
- ** Email**: Contact maintainers

- --

* * 🎉 Notion AI Server is ready for AI integration!**

