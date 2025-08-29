# Chat Integration App

เว็บแอปพลิเคชันแชตที่รวมบริการต่างๆ เข้าด้วยกัน พร้อมระบบ Chat Agent และ Automation

## คุณสมบัติหลัก

### 🤖 Chat Agent
- ระบบแชตอัจฉริยะที่สามารถเข้าใจและตอบสนองต่อคำถามของผู้ใช้
- รองรับการสนทนาแบบ real-time
- ระบบจัดการประวัติการสนทนา

### ⚡ Automation & Workflow
- สร้างและจัดการ workflow อัตโนมัติ
- รองรับการเชื่อมต่อกับบริการต่างๆ เช่น Notion, Google Drive, Dropbox
- ระบบ trigger และ action ที่ยืดหยุ่น

### 🔗 Service Integration
- เชื่อมต่อกับบริการยอดนิยม:
  - Notion
  - Google Drive
  - Dropbox
  - Google Sheets
  - Google Docs
  - Airtable
  - Obsidian
  - Miro
  - Milanote
  - n8n
  - Make.com

### 🎨 User Interface
- ออกแบบด้วย React และ Tailwind CSS
- รองรับการใช้งานบนอุปกรณ์มือถือ (Responsive Design)
- ธีมสีที่สวยงามและใช้งานง่าย

## เทคโนโลยีที่ใช้

### Frontend
- **React** - JavaScript library สำหรับสร้าง user interface
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Build tool และ development server

### Backend
- **Flask** - Python web framework
- **SQLite** - Database สำหรับการพัฒนา
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Flask-SQLAlchemy** - ORM สำหรับ database

### Deployment
- **Manus Cloud Platform** - สำหรับ deploy แอปพลิเคชัน

## โครงสร้างโปรเจกต์

```
project/
├── chat-app/                 # Frontend React application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── App.jsx          # Main application component
│   │   └── main.jsx         # Entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── chat-backend/            # Backend Flask application
│   ├── src/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic services
│   │   ├── static/          # Static files (built frontend)
│   │   └── main.py          # Flask application entry point
│   ├── requirements.txt
│   └── venv/               # Python virtual environment
│
└── README.md               # Project documentation
```

## การติดตั้งและใช้งาน

### ข้อกำหนดระบบ
- Node.js 20.x หรือใหม่กว่า
- Python 3.11 หรือใหม่กว่า
- pnpm (สำหรับจัดการ package ใน frontend)

### การติดตั้ง

#### 1. Clone โปรเจกต์
```bash
git clone <repository-url>
cd project
```

#### 2. ติดตั้ง Frontend Dependencies
```bash
cd chat-app
pnpm install
```

#### 3. ติดตั้ง Backend Dependencies
```bash
cd ../chat-backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### การรันแอปพลิเคชัน

#### Development Mode

1. **รัน Backend**
```bash
cd chat-backend
source venv/bin/activate
python src/main.py
```
Backend จะรันที่ `http://localhost:5000`

2. **รัน Frontend** (ใน terminal ใหม่)
```bash
cd chat-app
pnpm run dev
```
Frontend จะรันที่ `http://localhost:5173`

#### Production Mode

1. **Build Frontend**
```bash
cd chat-app
pnpm run build
```

2. **คัดลอก Built Files ไปยัง Backend**
```bash
cp -r dist/* ../chat-backend/src/static/
```

3. **รัน Backend**
```bash
cd ../chat-backend
source venv/bin/activate
python src/main.py
```

แอปพลิเคชันจะรันที่ `http://localhost:5000`

## API Documentation

### Chat API

#### GET /api/chat/sessions
ดึงรายการ chat sessions ทั้งหมด

#### POST /api/chat/sessions
สร้าง chat session ใหม่

#### POST /api/chat/sessions/{session_id}/messages
เพิ่มข้อความใหม่ใน chat session

#### GET /api/chat/sessions/{session_id}/messages
ดึงข้อความทั้งหมดใน chat session

### Automation API

#### GET /api/workflows
ดึงรายการ workflows ทั้งหมด

#### POST /api/workflows
สร้าง workflow ใหม่

#### POST /api/workflows/{workflow_id}/execute
รัน workflow

#### PUT /api/workflows/{workflow_id}
อัปเดต workflow

#### DELETE /api/workflows/{workflow_id}
ลบ workflow

## การใช้งาน

### 1. การแชต
- คลิกแท็บ "แชต" เพื่อเริ่มการสนทนา
- คลิก "แชตใหม่" เพื่อสร้างการสนทนาใหม่
- พิมพ์ข้อความและกด Enter หรือคลิกปุ่มส่ง

### 2. การสร้าง Workflow
- คลิกแท็บ "อัตโนมัติ"
- คลิก "สร้าง Workflow"
- กรอกชื่อ, คำอธิบาย และเลือกประเภทการเรียกใช้
- คลิก "สร้าง" เพื่อบันทึก

### 3. การรัน Workflow
- ในหน้า "อัตโนมัติ" คลิกปุ่ม "รัน" ใน workflow ที่ต้องการ
- ระบบจะแสดงผลการทำงาน

## การ Deploy

แอปพลิเคชันได้ถูก deploy แล้วที่: **https://8xhpiqcqg5lm.manus.space**

### ข้อมูลการเข้าถึง
- **URL**: https://8xhpiqcqg5lm.manus.space
- **Username**: admin (สำหรับการจัดการระบบ)
- **Password**: admin123 (สำหรับการจัดการระบบ)

*หมายเหตุ: ในการใช้งานจริง ควรเปลี่ยนรหัสผ่านเริ่มต้น*

## การพัฒนาต่อ

### ฟีเจอร์ที่สามารถเพิ่มเติมได้
1. **Authentication System** - ระบบล็อกอินและจัดการผู้ใช้
2. **Real-time Notifications** - การแจ้งเตือนแบบ real-time
3. **File Upload/Download** - การอัปโหลดและดาวน์โหลดไฟล์
4. **Advanced Workflow Builder** - เครื่องมือสร้าง workflow แบบ visual
5. **API Integration Templates** - เทมเพลตสำหรับเชื่อมต่อ API ต่างๆ

### การเชื่อมต่อบริการเพิ่มเติม
- **Slack** - สำหรับการแจ้งเตือนและการสื่อสار
- **Discord** - สำหรับการแจ้งเตือนและการสื่อสาร
- **Trello** - สำหรับการจัดการงาน
- **Asana** - สำหรับการจัดการโปรเจกต์
- **Zapier** - สำหรับการเชื่อมต่อบริการต่างๆ

## การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. **Frontend ไม่สามารถเชื่อมต่อ Backend**
   - ตรวจสอบว่า Backend รันอยู่ที่ port 5000
   - ตรวจสอบ CORS settings

2. **Database Error**
   - ตรวจสอบว่าไฟล์ database ถูกสร้างแล้ว
   - รัน `flask db init` และ `flask db migrate` หากจำเป็น

3. **Build Error**
   - ลบ `node_modules` และรัน `pnpm install` ใหม่
   - ตรวจสอบ Node.js version

## การสนับสนุน

หากพบปัญหาหรือต้องการความช่วยเหลือ กรุณาติดต่อทีมพัฒนา

## License

MIT License - ดูรายละเอียดในไฟล์ LICENSE

