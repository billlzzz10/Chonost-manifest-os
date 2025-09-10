# 🔧 คู่มือการตั้งค่า .env File

## 📋 ภาพรวม

ระบบ Notion AI Server ใช้ไฟล์ `.env` เพื่อจัดการ environment variables ทำให้การตั้งค่าทำได้ง่ายและปลอดภัย

## 🚀 ขั้นตอนการตั้งค่า

### 1. **สร้างไฟล์ .env** ```powershell
# รัน script เพื่อสร้างไฟล์ .env จาก env.example
.\create_env_file.ps1
```

### 2. ** แก้ไขไฟล์ .env** เปิดไฟล์ ` .env` และแก้ไขค่าต่างๆ:

```
# Notion Integration Token (สำคัญที่สุด!)
NOTION_INTEGRATION_TOKEN=ntn_your_actual_token_here

# Server Configuration
NOTION_SERVER_PORT=8000
NOTION_SERVER_HOST=0.0.0.0

# Docker Configuration
DOCKER_IMAGE=mcp/notion
DOCKER_CONTAINER_NAME=notion-mcp-server

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/notion_mcp_server.log

# API Configuration
API_VERSION=v1
API_PREFIX=/api/v1

# Development Configuration
DEBUG=false
RELOAD=false
```

## 🔑 การได้มาซึ่ง Notion Integration Token

### 1. ** ไปที่ Notion Integrations** - เปิด [Notion Integrations](https://www.notion.so/my-integrations) - เข้าสู่ระบบด้วยบัญชี Notion ของคุณ

### 2. ** สร้าง Integration ใหม่** - คลิก "New integration"
- ตั้งชื่อ: ` Notion AI Server`
- เลือก workspace ที่ต้องการใช้

### 3. ** คัดลอก Token** - หลังจากสร้างแล้ว จะเห็น Token ที่เริ่มต้นด้วย ` ntn_`
- คัดลอก Token และใส่ในไฟล์ ` .env`

### 4. ** ตั้งค่าสิทธิ์** - ในหน้า Integration Settings
- เปิดใช้งาน "Read content" และ "Update content"
- เพิ่ม pages ที่ต้องการใช้งาน

## 📁 โครงสร้างไฟล์

```
FileSystemMCP/
├── .env                    # ไฟล์การตั้งค่า (สร้างจาก create_env_file.ps1)
├── env.example            # ตัวอย่างการตั้งค่า
├── create_env_file.ps1    # Script สร้างไฟล์ .env
├── scripts/
│   └── start-notion-mcp-server.ps1  # Script เริ่มต้น server
└── test_real_notion_integration.py  # ไฟล์ทดสอบ
```

## 🔧 การใช้งาน

### ** เริ่มต้น Server** ```powershell
# ระบบจะอ่านค่าจาก .env file อัตโนมัติ
.\scripts\start-notion-mcp-server.ps1
```

### ** ทดสอบการเชื่อมต่อ** ```powershell
# รันการทดสอบ
python test_real_notion_integration.py
```

## 🛡 ️ ความปลอดภัย

### ** สิ่งที่ไม่ควรทำ:** - ❌ อย่า commit ไฟล์ ` .env` ไปยัง Git repository
- ❌ อย่าแชร์ Token กับผู้อื่น
- ❌ อย่าใช้ Token เดียวกันในหลายโปรเจ็ค

### ** สิ่งที่ควรทำ:** - ✅ เก็บไฟล์ ` .env` ไว้ใน ` .gitignore`
- ✅ ใช้ Token แยกสำหรับแต่ละโปรเจ็ค
- ✅ หมุนเวียน Token เป็นประจำ

## 🔍 การตรวจสอบ

### ** ตรวจสอบการตั้งค่า** ```powershell
# ตรวจสอบว่า .env ถูกโหลดหรือไม่
 Get-Content .env | Select-String "NOTION_INTEGRATION_TOKEN"
```

### ** ตรวจสอบ Server** ```powershell
# ตรวจสอบว่า server กำลังรันอยู่
curl http://localhost:8000/health
```

## 🚨 การแก้ไขปัญหา

### ** ปัญหา: "Token ไม่ถูกต้อง"** ```powershell
# ตรวจสอบ Token ใน .env
 Get-Content .env | Select-String "NOTION_INTEGRATION_TOKEN"

# ตรวจสอบ Token ใน environment
echo $env:NOTION_INTEGRATION_TOKEN
```

### ** ปัญหา: "Server ไม่เริ่มต้น"** ```powershell
# ตรวจสอบการตั้งค่าใน .env
Get-Content .env

# ตรวจสอบ logs
Get-Content logs/notion_mcp_server.log -Tail 20
```

### ** ปัญหา: "ไม่พบไฟล์ .env"** ```powershell
# สร้างไฟล์ .env ใหม่
.\create_env_file.ps1
```

## 📚 ข้อมูลเพิ่มเติม

- [Notion API Documentation](https://developers.notion.com/) - [Notion Integrations](https://www.notion.so/my-integrations) - [Environment Variables Best Practices](https://12factor.net/config) - --

* * หมายเหตุ:** ไฟล์ ` .env` จะถูกโหลดอัตโนมัติเมื่อรัน PowerShell script หรือ Python script ที่เกี่ยวข้อง

