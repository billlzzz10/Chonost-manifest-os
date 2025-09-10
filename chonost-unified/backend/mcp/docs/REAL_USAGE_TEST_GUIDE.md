# 🚀 คู่มือการทดสอบใช้งานจริงกับ Notion

## 📋 สิ่งที่ต้องเตรียม

### 1. **Notion Integration Token** คุณต้องมี Notion Integration Token เพื่อทดสอบ:

1. ไปที่ [Notion Integrations](https://www.notion.so/my-integrations) 2. สร้าง Integration ใหม่
3. คัดลอก Token (เริ่มต้นด้วย `ntn_` )

### 2. ** Notion Page ID** คุณต้องมี Page ID ใน Notion ที่จะใช้เป็น parent page:

1. เปิดหน้าใน Notion ที่ต้องการใช้
2. คัดลอก URL: ` https://www.notion.so/your-workspace/Page-Title-1234567890abcdef` 3. Page ID คือส่วนสุดท้าย: ` 1234567890abcdef` ## 🔧 ขั้นตอนการทดสอบ

### ขั้นตอนที่ 1: สร้างไฟล์ .env

```
# สร้างไฟล์ .env จาก env.example
.\create_env_file.ps1
```

### ขั้นตอนที่ 2: แก้ไขไฟล์ .env
แก้ไขไฟล์ ` .env` ที่สร้างขึ้น:

```
# เปลี่ยนบรรทัดนี้
NOTION_INTEGRATION_TOKEN=ntn_your_token_here

# เป็น
NOTION_INTEGRATION_TOKEN=ntn_your_actual_token_here
```

### ขั้นตอนที่ 3: เริ่มต้น Notion AI Server

```
# เริ่มต้น server (จะอ่านค่าจาก .env file อัตโนมัติ)
.\scripts\start-notion-mcp-server.ps1
```

### ขั้นตอนที่ 4: แก้ไขไฟล์ทดสอบ
แก้ไข ` test_real_notion_integration.py` :

```
# เปลี่ยนบรรทัดนี้
parent_page_id="",  # ใส่ ID ของหน้าใน Notion ของคุณ

# เป็น
parent_page_id="1234567890abcdef",  # ใส่ Page ID ของคุณ
```

### ขั้นตอนที่ 5: รันการทดสอบ

```
# รันการทดสอบ
python test_real_notion_integration.py
```

## 🎯 สิ่งที่จะเกิดขึ้น

### 1. ** การวิเคราะห์ไฟล์** ระบบจะวิเคราะห์ไฟล์ต่อไปนี้:

- ` src/server/notion_mcp_server.py`
- ` src/ai/notion_ai_integration.py`
- ` README.md`

### 2. ** การสร้างหน้าใน Notion** สำหรับแต่ละไฟล์ ระบบจะ:

- วิเคราะห์เนื้อหา (basic, detailed, code analysis)
- สร้างหน้าใหม่ใน Notion
- เพิ่มข้อมูลการวิเคราะห์
- แสดงลิงก์ไปยังหน้า Notion

### 3. ** การสร้าง Project Documentation** ระบบจะสร้าง:

- หน้า overview ของโปรเจ็ค
- Database สำหรับเก็บข้อมูลไฟล์
- ลิงก์ไปยังไฟล์ทั้งหมด

## 🔍 การตรวจสอบผลลัพธ์

### 1. ** ตรวจสอบใน Terminal** ```
✅ เริ่มต้นสำเร็จ
📄 วิเคราะห์ไฟล์: src/server/notion_mcp_server.py
✅ สำเร็จ: File analyzed and exported to Notion
🔗 หน้า Notion: https://www.notion.so/your-page-id
```

### 2. ** ตรวจสอบใน Notion** 1. เปิด Notion workspace ของคุณ
2. ดูหน้าใหม่ที่ถูกสร้างขึ้น
3. ตรวจสอบเนื้อหาการวิเคราะห์

## 🛠 ️ การแก้ไขปัญหา

### ปัญหา: "Python ไม่พบ"

```
# ตรวจสอบ Python
python --version

# ถ้าไม่พบ ให้ติดตั้ง Python 3.8+
# ดาวน์โหลดจาก: https://www.python.org/downloads/
```

### ปัญหา: "Docker ไม่พบ"

```
# ตรวจสอบ Docker
docker --version

# ถ้าไม่พบ ให้ติดตั้ง Docker Desktop
# ดาวน์โหลดจาก: https://www.docker.com/products/docker-desktop/
```

### ปัญหา: "Server ไม่ตอบสนอง"

```
# ตรวจสอบว่า server กำลังรันอยู่
curl http://localhost:8000/health

# หรือเปิดใน browser
start http://localhost:8000/health
```

### ปัญหา: "Token ไม่ถูกต้อง"

```
# ตรวจสอบ Token
echo $env:NOTION_INTEGRATION_TOKEN

# ตั้งค่าใหม่
$env:NOTION_INTEGRATION_TOKEN = "ntn_your_new_token"
```

## 📊 ผลลัพธ์ที่คาดหวัง

### 1. ** ใน Notion จะเห็น:** - หน้าใหม่สำหรับแต่ละไฟล์
- การวิเคราะห์เนื้อหา
- โครงสร้างโค้ด
- Metadata ของไฟล์

### 2. ** ใน Terminal จะเห็น:** - สถานะการทำงาน
- ลิงก์ไปยังหน้า Notion
- ข้อผิดพลาด (ถ้ามี)

## 🎉 การยืนยันความสำเร็จ

การทดสอบสำเร็จเมื่อ:

1. ✅ Server เริ่มต้นได้
2. ✅ เชื่อมต่อกับ Notion ได้
3. ✅ สร้างหน้าใน Notion ได้
4. ✅ วิเคราะห์ไฟล์ได้
5. ✅ แสดงลิงก์ไปยังหน้า Notion

## 🔗 ลิงก์ที่เป็นประโยชน์

- [Notion API Documentation](https://developers.notion.com/) - [Notion Integrations](https://www.notion.so/my-integrations) - [FastAPI Documentation](https://fastapi.tiangolo.com/) - [Docker Documentation](https://docs.docker.com/) - --

* * หมายเหตุ:** การทดสอบนี้จะสร้างข้อมูลจริงใน Notion workspace ของคุณ โปรดตรวจสอบให้แน่ใจว่าคุณมีสิทธิ์ในการสร้างหน้าและฐานข้อมูลใน workspace นั้น

