# 🚀 File System MCP Project Launcher

คำสั่ง PowerShell และ Batch สำหรับเปิดโปรแกรมต่างๆ ในโปรเจค File System MCP ผ่าน Command Line

## 📁 ไฟล์ที่ใช้งาน

### **ไฟล์หลัก:** - `run.ps1` - PowerShell script หลักที่รองรับทุกฟีเจอร์
- ` run.bat` - Windows Batch file สำหรับระบบที่ไม่รองรับ PowerShell

### ** ไฟล์แยกตามฟังก์ชัน:** - ` start-chat.ps1` - เปิดแอปแชตพื้นฐาน
- ` start-ai.ps1` - เปิดแอปแชตที่รวม AI
- ` start-dataset.ps1` - สร้างชุดข้อมูลฝึก AI
- ` test-ollama.ps1` - ทดสอบการเชื่อมต่อ Ollama

## 🚀 วิธีการใช้งาน

### ** 1. PowerShell (แนะนำ)** #### ** คำสั่งหลัก:** ```powershell
# เปิดแอปแชตพื้นฐาน
.\run.ps1 chat

# เปิดแอปแชตขั้นสูง
.\run.ps1 advanced

# เปิดแอปแชตที่รวม AI
.\run.ps1 ai

# สร้างชุดข้อมูลฝึก AI
.\run.ps1 dataset

# ทดสอบการเชื่อมต่อ Ollama
.\run.ps1 test
.\run.ps1 ollama  # alias

# แสดงความช่วยเหลือ
.\run.ps1 help
.\run.ps1 -Help

# เปิดแอปทั้งหมดพร้อมกัน
.\run.ps1 -All
```

#### ** คำสั่งแยกตามฟังก์ชัน:** ```powershell
# เปิดแอปแต่ละตัว
.\start-chat.ps1      # แอปแชตพื้นฐาน
.\start-ai.ps1        # แอปแชตที่รวม AI
.\start-dataset.ps1   # สร้างชุดข้อมูล
.\test-ollama.ps1     # ทดสอบ Ollama
```

### ** 2. Windows Batch** ```batch
# เปิดแอปแชตพื้นฐาน
run.bat chat

# เปิดแอปแชตขั้นสูง
run.bat advanced

# เปิดแอปแชตที่รวม AI
run.bat ai

# สร้างชุดข้อมูลฝึก AI
run.bat dataset

# ทดสอบการเชื่อมต่อ Ollama
run.bat test
run.bat ollama

# แสดงความช่วยเหลือ
run.bat help
```

## 🔧 ฟีเจอร์พิเศษ

### ** การตรวจสอบอัตโนมัติ:** - ✅ ตรวจสอบการติดตั้ง Python
- ✅ ตรวจสอบ Virtual Environment
- ✅ ตรวจสอบไฟล์ที่จำเป็น
- ✅ แสดงสถานะการเชื่อมต่อ

### ** การจัดการ Virtual Environment:** - 🔄 เปิดใช้ Virtual Environment อัตโนมัติ (ถ้ามี)
- 🌐 ใช้ Python global (ถ้าไม่มี venv)
- 📦 แสดงสถานะการใช้งาน

### ** การแสดงผลสี:** - 🟢 สีเขียว - สำเร็จ
- 🟡 สีเหลือง - คำเตือน
- 🔴 สีแดง - ข้อผิดพลาด
- 🔵 สีฟ้า - ข้อมูล

## 📊 ตัวอย่างการใช้งาน

### ** เปิดแอปแชตที่รวม AI:** ```powershell
PS> .\run.ps1 ai

🚀 File System MCP Project Launcher
==================================================

🔍 ตรวจสอบการติดตั้ง...
✅ Python: Python 3.12.0
✅ Virtual Environment พบ
✅ file_system_analyzer.py
✅ desktop_chat_app.py
✅ advanced_chat_app.py
✅ dataset_generator.py
✅ ollama_client.py

🚀 เปิด แอปแชตที่รวม AI...
📦 ใช้ Virtual Environment
✅ เปิด แอปแชตที่รวม AI สำเร็จ
```

### ** สร้างชุดข้อมูล:** ```powershell
PS> .\run.ps1 dataset

📊 สร้างชุดข้อมูลฝึก AI...
📦 ใช้ Virtual Environment

🚀 File System MCP Dataset Generator
==================================================
🚀 เริ่มสร้างชุดข้อมูลสำหรับฝึก AI Agent...
✅ สร้างชุดข้อมูลสำเร็จ: 30 รายการ
📁 บันทึกไปยัง: file_system_training_dataset.json
```

### ** เปิดแอปทั้งหมด:** ```powershell
PS> .\run.ps1 -All

🚀 เปิดแอปทั้งหมด...

🚀 เปิด แอปแชตพื้นฐาน...
📦 ใช้ Virtual Environment
✅ เปิด แอปแชตพื้นฐาน สำเร็จ

🚀 เปิด แอปแชตขั้นสูง...
📦 ใช้ Virtual Environment
✅ เปิด แอปแชตขั้นสูง สำเร็จ

🚀 เปิด แอปแชตที่รวม AI...
📦 ใช้ Virtual Environment
✅ เปิด แอปแชตที่รวม AI สำเร็จ

🎉 เปิดแอปทั้งหมดเสร็จสิ้น!
```

## 🛠 ️ การแก้ไขปัญหา

### ** ปัญหาที่พบบ่อย:** #### ** 1. PowerShell Execution Policy** ```powershell
# ถ้าไม่สามารถรัน .ps1 ได้
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# หรือรันครั้งเดียว
powershell -ExecutionPolicy Bypass -File .\run.ps1 chat
```

#### ** 2. Python ไม่พบ** ```
❌ Python ไม่พบ
💡 ติดตั้ง Python จาก https://python.org
💡 ตรวจสอบว่า Python อยู่ใน PATH
```

#### ** 3. Virtual Environment ไม่พบ** ```
⚠️ Virtual Environment ไม่พบ
💡 สร้าง venv ด้วยคำสั่ง: python -m venv venv
```

#### ** 4. ไฟล์หายไป** ```
❌ file_system_analyzer.py ไม่พบ
💡 ตรวจสอบว่าอยู่ในโฟลเดอร์ที่ถูกต้อง
💡 ดาวน์โหลดไฟล์จากโปรเจค
```

### ** การตรวจสอบระบบ:** ```powershell
# ตรวจสอบ Python
python --version

# ตรวจสอบ pip
pip --version

# ตรวจสอบ packages ที่ติดตั้ง
pip list

# ตรวจสอบ Virtual Environment
if (Test-Path "venv\Scripts\Activate.ps1") { "venv OK" } else { "venv NG" }
```

## 🎯 การปรับแต่ง

### ** เพิ่มแอปใหม่ใน run.ps1:** ```powershell
# เพิ่มใน switch statement
"newapp" {
    Start-Application "newapp" "new_app.py" "แอปใหม่"
}
```

### ** เปลี่ยนสีที่แสดงผล:** ```powershell
$Colors = @{
    Success = "Green"      # เปลี่ยนเป็นสีอื่น
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Title = "Magenta"
}
```

### ** เพิ่มการตรวจสอบ:** ```powershell
# เพิ่มไฟล์ที่ต้องตรวจสอบ
$requiredFiles = @(
    "file_system_analyzer.py",
    "new_file.py"  # เพิ่มไฟล์ใหม่
)
```

## 🔗 คำสั่งที่เกี่ยวข้อง

### ** Virtual Environment:** ```powershell
# สร้าง Virtual Environment
python -m venv venv

# เปิดใช้งาน (PowerShell)
.\venv\Scripts\Activate.ps1

# เปิดใช้งาน (Command Prompt)
venv\Scripts\activate.bat

# ปิดการใช้งาน
deactivate
```

### ** การติดตั้ง Dependencies:** ```powershell
# ติดตั้งจาก requirements.txt
pip install -r requirements.txt

# ติดตั้งแยก
pip install requests rich python-magic-bin Pillow
```

### ** การทดสอบ:** ```powershell
# ทดสอบ Python script
python -c "import sys; print(sys.version)"

# ทดสอบ import modules
python -c "import tkinter; print('tkinter OK')"
```

## 📝 หมายเหตุ

- ✅ ใช้งานได้ทั้ง PowerShell และ Command Prompt
- ✅ รองรับ Virtual Environment อัตโนมัติ
- ✅ ตรวจสอบและแจ้งเตือนข้อผิดพลาด
- ✅ แสดงผลสีสวยงาม
- ✅ เปิดแอปในหน้าต่างใหม่
- ✅ รองรับการเปิดหลายแอปพร้อมกัน

- --

* * สร้างโดย**: Orion Senior Dev / Pair Programmer
* * เวอร์ชัน**: 1.0.0
* * วันที่**: 21 สิงหาคม 2024

