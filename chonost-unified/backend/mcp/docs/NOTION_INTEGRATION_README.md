# 📚 Notion MCP Integration - คู่มือการใช้งาน

## 🎯 ภาพรวม

Notion MCP Integration เป็นการบูรณาการระหว่าง **FileSystemMCP** และ ** Notion MCP Server** เพื่อให้สามารถจัดการและวิเคราะห์ข้อมูลไฟล์ผ่าน Notion ได้อย่างมีประสิทธิภาพ

### ✨ Features หลัก

- ** 📁 File Structure Export**: ส่งออกโครงสร้างไฟล์ไปยัง Notion
- ** 🗄️ Database Management**: สร้างและจัดการ database สำหรับการวิเคราะห์ไฟล์
- ** 🔄 Real-time Sync**: ซิงค์ข้อมูลแบบ real-time (optional)
- ** 🏷️ Tagging System**: ระบบติดแท็กไฟล์อัตโนมัติ
- ** 🔍 Search Integration**: ค้นหาข้อมูลข้ามแพลตฟอร์ม
- ** 📊 Analytics Dashboard**: แสดงสถิติและข้อมูลการวิเคราะห์

- --

## 🚀 การติดตั้ง

### 1. Prerequisites

#### ระบบที่ต้องการ
- ** Python 3.8+** - ** Docker Desktop** - ** PowerShell 7+** (Windows)
- ** Notion Account** และ ** Internal Integration Token** #### Notion Setup
1. ไปที่ [Notion Developers](https://developers.notion.com/) 2. สร้าง ** Internal Integration** 3. รับ ** Internal Integration Token** 4. แชร์หน้า Notion ที่ต้องการใช้งานกับ Integration

### 2. การติดตั้ง

#### วิธีที่ 1: ใช้ PowerShell Script (แนะนำ)
```
# รัน script พร้อม token
.\scripts\start-notion-integration.ps1 -Token "ntn_your_token_here"

# หรือตั้งค่า environment variable ก่อน
$env:NOTION_INTEGRATION_TOKEN = "ntn_your_token_here"
.\scripts\start-notion-integration.ps1
```

#### วิธีที่ 2: ติดตั้งด้วยตนเอง
```
# 1. Clone repository
git clone <repository-url>
cd FileSystemMCP

# 2. สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ
venv\Scripts\activate     # Windows

# 3. ติดตั้ง dependencies
pip install -r requirements_notion_integration.txt

# 4. ดาวน์โหลด Docker image
docker pull mcp/notion

# 5. ตั้งค่า environment variable
export NOTION_INTEGRATION_TOKEN="ntn_your_token_here"  # Linux/Mac
# หรือ
set NOTION_INTEGRATION_TOKEN=ntn_your_token_here       # Windows
```

### 3. การทดสอบ

```
# ทดสอบการเชื่อมต่อ
python -c "
import asyncio
import sys
sys.path.append('src/server')
from notion_mcp_integration import test_notion_integration

async def test():
    import os
    token = os.getenv('NOTION_INTEGRATION_TOKEN')
    success = await test_notion_integration(token)
    print('✅ Success' if success else '❌ Failed')

asyncio.run(test())
"
```

- --

## 📖 การใช้งาน

### 1. การเริ่มต้น Service

#### เริ่มต้นแบบ Standalone
```
import asyncio
from src.server.notion_mcp_integration import NotionMCPIntegration

async def main():
    notion = NotionMCPIntegration()

    # เริ่มต้น MCP Server
    if await notion.start_mcp_server():
        print("✅ Notion MCP Integration พร้อมใช้งาน")

        # ใช้งานฟีเจอร์ต่างๆ ตรงนี้

        # หยุด service
        await notion.stop_mcp_server()
    else:
        print("❌ ไม่สามารถเริ่มต้น service ได้")

asyncio.run(main())
```

#### เริ่มต้นแบบ Service
```
# รัน service แบบต่อเนื่อง
python notion_integration_service.py
```

### 2. การส่งออกโครงสร้างไฟล์

```
import asyncio
from src.server.notion_mcp_integration import NotionMCPIntegration
from src.core.file_system_analyzer import FileSystemMCPTool

async def export_file_structure():
    # วิเคราะห์โครงสร้างไฟล์
    analyzer = FileSystemMCPTool()
    file_structure = analyzer._run('{"action": "scan", "path": "./src"}')

    # ส่งออกไปยัง Notion
    notion = NotionMCPIntegration()
    await notion.start_mcp_server()

    result = await notion.export_file_structure_to_notion(
        file_structure=file_structure,
        parent_page_id="your_notion_page_id"
    )

    await notion.stop_mcp_server()
    return result

# รันการส่งออก
result = asyncio.run(export_file_structure())
print(f"ส่งออกสำเร็จ: {result}")
```

### 3. การสร้างและจัดการ Database

```
async def create_file_analysis_database():
    notion = NotionMCPIntegration()
    await notion.start_mcp_server()

    # สร้าง database สำหรับการวิเคราะห์ไฟล์
    database = await notion.create_file_analysis_database(
        parent_page_id="your_notion_page_id"
    )

    # เพิ่มไฟล์ลงใน database
    file_info = {
        "name": "main.py",
        "path": "/path/to/main.py",
        "size": 1024,
        "modified": "2024-01-01T00:00:00Z"
    }

    await notion.add_file_to_database(
        database_id=database["id"],
        file_info=file_info
    )

    await notion.stop_mcp_server()
```

### 4. การค้นหาและจัดการข้อมูล

```
async def search_and_manage_data():
    notion = NotionMCPIntegration()
    await notion.start_mcp_server()

    # ค้นหาหน้า
    search_results = await notion.search_pages(
        query="file analysis",
        filter_type="page"
    )

    # ค้นหาข้อมูลใน database
    database_results = await notion.query_database(
        database_id="your_database_id",
        filter={
            "property": "File Type",
            "select": {"equals": "Code"}
        },
        sorts=[
            {
                "property": "Last Modified",
                "direction": "descending"
            }
        ]
    )

    await notion.stop_mcp_server()
    return search_results, database_results
```

- --

## ⚙ ️ Configuration

### Configuration File Structure

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
    "supportedFileTypes": [".py", ".js", ".ts", ".md", ".txt"]
  },
  "integrationFeatures": {
    "fileStructureExport": true,
    "fileAnalysisDatabase": true,
    "realTimeSync": false,
    "batchProcessing": true,
    "searchIntegration": true,
    "taggingSystem": true
  }
}
```

### Environment Variables

 | Variable | Description | Required |
 | ---------- | ------------- | ---------- |
 | ` NOTION_INTEGRATION_TOKEN` | Notion Internal Integration Token | ✅ |
 | ` NOTION_PARENT_PAGE_ID` | Default parent page ID | ❌ |
 | ` NOTION_DATABASE_ID` | Default database ID | ❌ |
 | ` NOTION_SYNC_INTERVAL` | Sync interval in seconds | ❌ |

- --

## 🔧 API Reference

### NotionMCPIntegration Class

#### Core Methods

 | Method | Description | Parameters |
 | -------- | ------------- | ------------ |
 | ` start_mcp_server()` | เริ่มต้น MCP Server | - |
 | ` stop_mcp_server()` | หยุด MCP Server | - |
 | ` send_mcp_request()` | ส่งคำขอไปยัง MCP Server | ` method` , ` params` |

#### Notion API Methods

 | Method | Description | Parameters |
 | -------- | ------------- | ------------ |
 | ` create_page()` | สร้างหน้าใหม่ | ` parent_id` , ` properties` , ` children` |
 | ` create_database()` | สร้าง database | ` parent_id` , ` properties` , ` title` |
 | ` query_database()` | ค้นหาข้อมูลใน database | ` database_id` , ` filter` , ` sorts` |
 | ` search_pages()` | ค้นหาหน้า | ` query` , ` filter_type` |
 | ` get_page()` | ดึงข้อมูลหน้า | ` page_id` |
 | ` update_page()` | อัปเดตข้อมูลหน้า | ` page_id` , ` properties` , ` archived` |
 | ` get_block_children()` | ดึง children blocks | ` block_id` , ` page_size` |
 | ` append_block_children()` | เพิ่ม children blocks | ` block_id` , ` children` |

#### File System Integration Methods

 | Method | Description | Parameters |
 | -------- | ------------- | ------------ |
 | ` export_file_structure_to_notion()` | ส่งออกโครงสร้างไฟล์ | ` file_structure` , ` parent_page_id` |
 | ` create_file_analysis_database()` | สร้าง database สำหรับการวิเคราะห์ | ` parent_page_id` |
 | ` add_file_to_database()` | เพิ่มไฟล์ลงใน database | ` database_id` , ` file_info` |

- --

## 🧪 Testing

### Unit Tests

```
# รัน unit tests
pytest tests/test_notion_integration.py -v

# รัน tests พร้อม coverage
pytest tests/test_notion_integration.py --cov=src.server.notion_mcp_integration --cov-report=html
```

### Integration Tests

```
# ทดสอบการเชื่อมต่อจริง
python -m pytest tests/test_notion_integration_real.py -v
```

### Manual Testing

```
# ทดสอบการเชื่อมต่อ
python src/server/notion_mcp_integration.py
```

- --

## 🐛 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. Docker ไม่ทำงาน
```
# ตรวจสอบ Docker status
docker info

# เริ่มต้น Docker Desktop
# Windows: เปิด Docker Desktop
# Linux: sudo systemctl start docker
```

#### 2. Token ไม่ถูกต้อง
```
# ตรวจสอบ token
echo $NOTION_INTEGRATION_TOKEN

# ตั้งค่าใหม่
export NOTION_INTEGRATION_TOKEN="ntn_your_new_token"
```

#### 3. Permission Denied
```
# ตรวจสอบ permissions
ls -la scripts/start-notion-integration.ps1

# ให้สิทธิ์การรัน
chmod +x scripts/start-notion-integration.ps1
```

#### 4. Network Issues
```
# ตรวจสอบการเชื่อมต่อ
ping api.notion.com

# ตรวจสอบ firewall settings
```

### Error Messages

 | Error | Cause | Solution |
 | ------- | ------- | ---------- |
 | ` MCP Server ไม่ได้เชื่อมต่อ` | Docker ไม่ทำงาน | เริ่มต้น Docker Desktop |
 | ` ไม่พบ Notion Integration Token` | Token ไม่ได้ตั้งค่า | ตั้งค่า environment variable |
 | ` ไม่สามารถดาวน์โหลด Docker image` | Network issues | ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต |
 | ` Permission denied` | File permissions | ให้สิทธิ์การรันไฟล์ |

- --

## 📈 Performance

### Optimization Tips

1. ** Batch Processing**: ใช้ batch processing สำหรับไฟล์จำนวนมาก
2. ** Caching**: ใช้ caching สำหรับข้อมูลที่ใช้บ่อย
3. ** Async Operations**: ใช้ async/await สำหรับ operations ที่ใช้เวลานาน
4. ** Connection Pooling**: ใช้ connection pooling สำหรับการเชื่อมต่อ

### Monitoring

```
import time
import logging

# ตั้งค่า logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# วัดประสิทธิภาพ
start_time = time.time()
# ... operations ...
end_time = time.time()
logger.info(f"Operation took {end_time - start_time:.2f} seconds")
```

- --

## 🔒 Security

### Best Practices

1. ** Token Management**: เก็บ token ใน environment variables
2. ** Access Control**: จำกัดการเข้าถึง Notion pages
3. ** Data Validation**: ตรวจสอบข้อมูลก่อนส่งไปยัง Notion
4. ** Error Handling**: จัดการ errors อย่างเหมาะสม

### Security Checklist

- [ ] Token ถูกเก็บใน environment variables
- [ ] ไม่มี hardcoded credentials ในโค้ด
- [ ] ใช้ HTTPS สำหรับการเชื่อมต่อ
- [ ] จำกัด permissions ของ Notion integration
- [ ] ตรวจสอบ logs อย่างสม่ำเสมอ

- --

## 🤝 Contributing

### Development Setup

1. Fork repository
2. สร้าง feature branch
3. เขียน tests
4. รัน linting และ tests
5. สร้าง pull request

### Code Standards

- ใช้ TypeScript-style type hints
- เขียน docstrings สำหรับทุก function
- ใช้ async/await สำหรับ async operations
- เขียน tests สำหรับทุก feature

- --

## 📞 Support

### Resources

- [Notion API Documentation](https://developers.notion.com/) - [MCP Protocol Documentation](https://modelcontextprotocol.io/) - [FileSystemMCP Documentation](./README.md) ### Contact

- ** Issues**: สร้าง issue ใน GitHub repository
- ** Discussions**: ใช้ GitHub Discussions
- ** Email**: [your-email@example.com]

- --

## 📄 License

MIT License - ดูรายละเอียดใน [LICENSE](../LICENSE) file

- --

## 🔄 Changelog

### v1.0.0 (2024-01-01)
- ✨ Initial release
- 🚀 Basic Notion MCP integration
- 📁 File structure export
- 🗄️ Database management

### v1.1.0 (2024-01-15)
- 🔄 Real-time sync support
- 🏷️ Enhanced tagging system
- 📊 Analytics dashboard
- 🐛 Bug fixes and improvements

