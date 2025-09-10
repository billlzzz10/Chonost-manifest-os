# 🌐 Universal File System MCP Server

## 📋 ภาพรวม

Universal File System MCP Server เป็นเครื่องมือวิเคราะห์และจัดการไฟล์ระบบที่ครอบคลุมทุกรูปแบบการจัดเก็บข้อมูล:

- **🖥️ Desktop Storage** (Windows, macOS, Linux)
- ** ☁️ Cloud Storage** (Google Drive, Dropbox, OneDrive, AWS S3)
- ** 📱 Mobile Storage** (Android, iOS)
- ** 🌐 Network Storage** (NAS, FTP, SFTP, SMB)

## 🎯 คุณสมบัติหลัก

### 🔧 Core Operations
- ** Universal Directory Scanner**: สแกนโฟลเดอร์บนแพลตฟอร์มใดก็ได้
- ** Universal Directory Summary**: สรุปข้อมูลจากแพลตฟอร์มใดก็ได้
- ** Universal File Search**: ค้นหาไฟล์ข้ามแพลตฟอร์ม

### ☁️ Cloud Integration
- ** Cloud Sync Status**: ตรวจสอบสถานะการซิงค์
- ** Multi-Cloud Analysis**: วิเคราะห์ข้อมูลจากหลาย cloud providers
- ** Cloud Migration**: แผนการย้ายข้อมูลระหว่าง cloud

### 📱 Mobile Support
- ** Mobile Storage Analysis**: วิเคราะห์พื้นที่จัดเก็บมือถือ
- ** Cross-Device Sync**: ตรวจสอบการซิงค์ระหว่างอุปกรณ์
- ** App Data Analysis**: วิเคราะห์ข้อมูลแอปพลิเคชัน

### 🌐 Network Storage
- ** Network Storage Connection**: เชื่อมต่อกับ NAS, FTP, SFTP
- ** Permission Analysis**: วิเคราะห์สิทธิ์การเข้าถึง
- ** Transfer Analysis**: วิเคราะห์การถ่ายโอนข้อมูล

### 🔄 Cross-Platform Features
- ** Cross-Platform Comparison**: เปรียบเทียบโครงสร้างไฟล์ข้ามแพลตฟอร์ม
- ** Storage Migration Plan**: แผนการย้ายข้อมูลระหว่างแพลตฟอร์ม
- ** Universal Backup Analysis**: วิเคราะห์การสำรองข้อมูล

### 🦄 UnicornX OS Integration
- ** UnicornX Universal Export**: ส่งออกข้อมูลไปยัง UnicornX OS
- ** Biome Data Generation**: สร้างข้อมูลสำหรับ Mind-Biome Visualization
- ** Catalyst Fragment Creation**: สร้าง Catalyst Fragments จากข้อมูลไฟล์

## 🚀 การติดตั้ง

### Prerequisites
```
# Python 3.9+
python --version

# Required packages
pip install asyncio requests pathlib
```

### Quick Start
```
# Clone repository
git clone [repository-url]
cd FileSystemMCP

# Install dependencies
pip install -r requirements.txt

# Run Universal MCP Server
python universal_fs_mcp_server.py
```

## 📊 Tool Reference

### Universal Core Operations

#### ` universal_scan_directory`
สแกนโฟลเดอร์บนแพลตฟอร์มใดก็ได้

```
{
  "name": "universal_scan_directory",
  "arguments": {
    "path": "/path/to/directory",
 "storage_type": "local | cloud | mobile | network",
 "provider": "google_drive | dropbox | android | ios | ftp | sftp",
    "credentials": {},
    "config": {
      "max_depth": 10,
      "include_hidden": false
    }
  }
}
```

#### ` universal_get_summary`
รับสรุปข้อมูลจากแพลตฟอร์มใดก็ได้

```
{
  "name": "universal_get_summary",
  "arguments": {
    "session_id": "session_123",
    "storage_type": "local"
  }
}
```

#### ` universal_search`
ค้นหาไฟล์ข้ามแพลตฟอร์ม

```
{
  "name": "universal_search",
  "arguments": {
    "query": "document.pdf",
    "platforms": ["local", "google_drive"],
    "filters": {
      "file_type": "pdf",
      "size_min": 1000000
    }
  }
}
```

### Platform-Specific Operations

#### ` cloud_sync_status`
ตรวจสอบสถานะการซิงค์ cloud

```
{
  "name": "cloud_sync_status",
  "arguments": {
    "provider": "google_drive",
    "path": "/Documents"
  }
}
```

#### ` mobile_storage_analysis`
วิเคราะห์พื้นที่จัดเก็บมือถือ

```
{
  "name": "mobile_storage_analysis",
  "arguments": {
    "platform": "android",
    "storage_type": "internal",
    "path": "/storage/emulated/0"
  }
}
```

#### ` network_storage_connect`
เชื่อมต่อกับ network storage

```
{
  "name": "network_storage_connect",
  "arguments": {
    "protocol": "sftp",
    "host": "192.168.1.100",
    "port": 22,
    "username": "user",
    "password": "password",
    "path": "/home/user"
  }
}
```

### Cross-Platform Operations

#### ` cross_platform_compare`
เปรียบเทียบข้ามแพลตฟอร์ม

```
{
  "name": "cross_platform_compare",
  "arguments": {
    "sources": [
      {"path": "/local/path", "type": "local"},
      {"path": "/cloud/path", "type": "cloud", "provider": "google_drive"}
    ],
    "comparison_type": "structure"
  }
}
```

#### ` storage_migration_plan`
สร้างแผนการย้ายข้อมูล

```
{
  "name": "storage_migration_plan",
  "arguments": {
    "source": {
      "type": "local",
      "path": "/source/path"
    },
    "destination": {
      "type": "cloud",
      "provider": "google_drive",
      "path": "/destination/path"
    },
    "migration_type": "incremental"
  }
}
```

### UnicornX OS Integration

#### ` unicornx_universal_export`
ส่งออกข้อมูลไปยัง UnicornX OS

```
{
  "name": "unicornx_universal_export",
  "arguments": {
    "session_id": "session_123",
    "platforms": ["local", "google_drive"],
    "project_type": "DEV",
    "include_biome_data": true
  }
}
```

## 🔧 Configuration

### Platform Configuration

#### Local Storage
```
{
  "local": {
    "windows": {
      "paths": ["C:\\", "D:\\"],
      "file_systems": ["NTFS", "FAT32"]
    },
    "macos": {
      "paths": ["/Users/", "/Applications/"],
      "file_systems": ["APFS", "HFS+"]
    },
    "linux": {
      "paths": ["/home/", "/var/"],
      "file_systems": ["ext4", "btrfs"]
    }
  }
}
```

#### Cloud Storage
```
{
  "cloud": {
    "google_drive": {
      "api_endpoint": "https://www.googleapis.com/drive/v3",
      "scopes": ["https://www.googleapis.com/auth/drive.readonly"]
    },
    "dropbox": {
      "api_endpoint": "https://api.dropboxapi.com/2",
      "scopes": ["files.metadata.read"]
    }
  }
}
```

#### Mobile Storage
```
{
  "mobile": {
    "android": {
      "storage_types": ["internal", "external"],
      "permissions": ["READ_EXTERNAL_STORAGE"]
    },
    "ios": {
      "storage_types": ["local", "icloud"],
      "permissions": ["NSDocumentsFolderUsageDescription"]
    }
  }
}
```

#### Network Storage
```
{
  "network": {
    "ftp": {
      "ports": [21, 2121],
      "protocols": ["FTP", "FTPS"]
    },
    "sftp": {
      "ports": [22],
      "protocols": ["SSH", "SFTP"]
    }
  }
}
```

## 📈 Use Cases

### 1. Enterprise File Management
- วิเคราะห์ไฟล์ข้าม multiple storage platforms
- ตรวจสอบการซิงค์ระหว่าง cloud providers
- สร้างแผนการย้ายข้อมูลระหว่าง storage systems

### 2. Mobile Device Management
- วิเคราะห์พื้นที่จัดเก็บมือถือ
- ตรวจสอบการซิงค์กับ cloud storage
- จัดการไฟล์แอปพลิเคชัน

### 3. Network Storage Administration
- เชื่อมต่อและวิเคราะห์ NAS, FTP servers
- ตรวจสอบสิทธิ์การเข้าถึง
- วิเคราะห์การใช้งาน storage

### 4. UnicornX OS Integration
- ส่งออกข้อมูลไฟล์ไปยัง UnicornX OS
- สร้าง Catalyst Fragments จากโครงสร้างไฟล์
- สร้าง Mind-Biome visualization data

## 🔒 Security

### Credential Management
- เข้ารหัส credentials ในไฟล์ configuration
- ใช้ secure connections สำหรับ network storage
- ตรวจสอบ SSL certificates

### Access Control
- จำกัดการเข้าถึงตาม platform permissions
- ตรวจสอบสิทธิ์การเข้าถึงไฟล์
- Log การเข้าถึงทั้งหมด

## 📊 Performance

### Optimization
- Multi-threading สำหรับ concurrent scans
- Caching สำหรับ metadata
- Streaming สำหรับไฟล์ขนาดใหญ่

### Resource Management
- จำกัด memory usage
- Timeout สำหรับ long-running operations
- Cleanup resources หลังใช้งาน

## 🧪 Testing

### Unit Tests
```
python -m pytest tests/test_universal_mcp.py
```

### Integration Tests
```
python -m pytest tests/test_integration.py
```

### Platform-Specific Tests
```
# Test local storage
python -m pytest tests/test_local_storage.py

# Test cloud storage (requires credentials)
python -m pytest tests/test_cloud_storage.py

# Test mobile storage
python -m pytest tests/test_mobile_storage.py

# Test network storage
python -m pytest tests/test_network_storage.py
```

## 📝 Examples

### Example 1: Scan Local Directory
```
import asyncio
from universal_fs_mcp_server import UniversalFileSystemMCPServer

async def scan_local():
    server = UniversalFileSystemMCPServer()

    result = await server._universal_scan_directory({
        "path": "/home/user/documents",
        "storage_type": "local",
        "config": {
            "max_depth": 5,
            "include_hidden": False
        }
    })

    print(result)

asyncio.run(scan_local())
```

### Example 2: Compare Cloud vs Local
```
async def compare_storage():
    server = UniversalFileSystemMCPServer()

    result = await server._cross_platform_compare({
        "sources": [
            {"path": "/local/documents", "type": "local"},
            {"path": "/cloud/documents", "type": "cloud", "provider": "google_drive"}
        ],
        "comparison_type": "structure"
    })

    print(result)

asyncio.run(compare_storage())
```

### Example 3: Export to UnicornX OS
```
async def export_to_unicornx():
    server = UniversalFileSystemMCPServer()

    result = await server._unicornx_universal_export({
        "session_id": "session_123",
        "platforms": ["local", "google_drive"],
        "project_type": "DEV",
        "include_biome_data": True
    })

    print(result)

asyncio.run(export_to_unicornx())
```

## 🤝 Contributing

### Development Guidelines
1. ใช้ TypeScript สำหรับ type definitions
2. เขียน unit tests สำหรับทุกฟีเจอร์ใหม่
3. ใช้ async/await สำหรับ I/O operations
4. ตรวจสอบ security สำหรับทุก platform integration

### Code Style
- ** Python:** Black, isort, flake8
- ** Documentation:** Google Style Docstrings
- ** Testing:** pytest with async support

## 📄 License

MIT License - ดูรายละเอียดใน [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- ** UnicornX OS Team** - สำหรับแนวคิดและสถาปัตยกรรม
- ** Open Source Community** - สำหรับ libraries และ tools ที่ใช้
- ** Platform Providers** - สำหรับ APIs และ documentation

- --

* "Universal Storage, Universal Analysis, Universal Growth"* 🌐 ✨

