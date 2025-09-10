# 🎯 Auto Vault Watcher

## 📋 ภาพรวม
เครื่องมือเฝ้ามองและจัดระเบียบไฟล์อัตโนมัติสำหรับ Obsidian Vault ที่ทำงานเงียบๆ ในพื้นหลัง

## ✨ คุณสมบัติหลัก

### 🔍 **File Watching** - เฝ้ามองการเปลี่ยนแปลงไฟล์แบบ Real-time
- รองรับการสร้าง, แก้ไข, ย้ายไฟล์
- ทำงานแบบ Background Service

### 🤖 ** Auto Organization** - จัดระเบียบไฟล์อัตโนมัติเมื่อเซฟ
- วิเคราะห์เนื้อหาไฟล์เพื่อจัดหมวดหมู่
- ย้ายไฟล์ไปยังโฟลเดอร์ที่เหมาะสม

### 📝 ** Smart Categorization** - ** Prompts**: ไฟล์ที่มีคำว่า "prompt", "copilot", "template"
- ** Templates**: ไฟล์ที่มีคำว่า "template", "form", "format"
- ** Tools**: ไฟล์ที่มีคำว่า "tool", "utility", "script"
- ** Notes**: ไฟล์ที่มีคำว่า "note", "memo", "idea"
- ** Data**: ไฟล์ที่มีคำว่า "data", "database", "config"

### 📊 ** Logging & Statistics** - บันทึกการทำงานในไฟล์ log
- สถิติการประมวลผลไฟล์
- รายงานการทำงาน

## 🚀 การใช้งาน

### การติดตั้ง
```
pip install -r requirements_watcher.txt
```

### การรัน
```
python auto_vault_watcher.py
```

### การหยุด
กด ` Ctrl+C` เพื่อหยุดการทำงาน

## ⚙ ️ การตั้งค่า

ไฟล์ ` vault_watcher_config.json` ใน Vault:

```
{
  "watch_extensions": [".txt", ".md", ".json"],
  "auto_organize": true,
  "move_duplicates": true,
  "create_readme": true,
  "organize_rules": {
    "prompts": ["prompt", "copilot", "template"],
    "templates": ["template", "form", "format"],
    "tools": ["tool", "utility", "script"],
    "notes": ["note", "memo", "idea"],
    "data": ["data", "database", "config"]
  },
  "target_folders": {
    "prompts": "08_Templates-Tools/Prompts/General",
    "templates": "08_Templates-Tools/Document_Templates",
    "tools": "08_Templates-Tools/Tools_and_Utilities",
    "notes": "06_NOTE",
    "data": "08_Templates-Tools/Databases"
  },
  "exclude_patterns": ["temp", "tmp", "backup", "old"],
  "min_file_size": 10
}
```

## 📁 โครงสร้างไฟล์

```
Vault/
├── logs/                          # ไฟล์ log
│   └── vault_watcher_YYYYMMDD.log
├── vault_watcher_config.json      # การตั้งค่า
├── vault_watcher_stats.json       # สถิติการทำงาน
└── [organized files...]
```

## 🔧 การทำงาน

### 1. ** File Detection** - เฝ้ามองการเปลี่ยนแปลงใน Vault
- ตรวจจับไฟล์ .txt, .md, .json

### 2. ** Content Analysis** - อ่านเนื้อหาไฟล์ (1000 ตัวอักษรแรก)
- วิเคราะห์ชื่อไฟล์และเนื้อหา

### 3. ** Smart Organization** - กำหนดโฟลเดอร์ปลายทาง
- ย้ายไฟล์อัตโนมัติ
- จัดการไฟล์ซ้ำ

### 4. ** Documentation** - สร้าง README อัตโนมัติ
- อัปเดตรายการไฟล์

## 📊 สถิติการทำงาน

- ** files_processed**: จำนวนไฟล์ที่ประมวลผล
- ** files_moved**: จำนวนไฟล์ที่ย้าย
- ** files_organized**: จำนวนไฟล์ที่จัดระเบียบ
- ** errors**: จำนวนข้อผิดพลาด

## 🎯 ข้อดี

### ✅ ** อัตโนมัติ** - ไม่ต้องจัดการไฟล์ด้วยตนเอง
- ทำงานเงียบๆ ในพื้นหลัง

### ✅ ** ชาญฉลาด** - วิเคราะห์เนื้อหาไฟล์
- จัดหมวดหมู่อัตโนมัติ

### ✅ ** ปลอดภัย** - ตรวจสอบไฟล์ซ้ำ
- บันทึก log การทำงาน

### ✅ ** ปรับแต่งได้** - ตั้งค่ากฎการจัดระเบียบ
- ปรับแต่งโฟลเดอร์ปลายทาง

## 🔄 การทำงานแบบ Background

เครื่องมือทำงานแบบ Background Service:
- เริ่มต้นเมื่อรันโปรแกรม
- เฝ้ามองการเปลี่ยนแปลงตลอดเวลา
- จัดระเบียบไฟล์ทันทีเมื่อเซฟ
- หยุดเมื่อกด Ctrl+C

## 📝 ตัวอย่างการทำงาน

1. ** สร้างไฟล์ใหม่**: ` my_prompt.md`
2. ** Auto Watcher ตรวจจับ**: ไฟล์ถูกสร้าง
3. ** วิเคราะห์เนื้อหา**: พบคำว่า "prompt"
4. ** จัดระเบียบ**: ย้ายไป ` 08_Templates-Tools/Prompts/General/`
5. ** สร้าง README**: อัปเดตรายการไฟล์

## 🎉 ผลลัพธ์

- ** Vault ที่เป็นระเบียบ**: ไฟล์อยู่ในตำแหน่งที่ถูกต้อง
- ** การทำงานอัตโนมัติ**: ไม่ต้องจัดการไฟล์ด้วยตนเอง
- ** เอกสารครบถ้วน**: README ในทุกโฟลเดอร์
- ** ติดตามการทำงาน**: Log และสถิติการทำงาน

