# 🚀 Chonost Desktop App - Startup Guide

## **ปัญหาที่พบ:**
- Terminal อยู่ใน directory ผิด (F:\ แทนที่จะเป็น project directory)
- API Server ไม่สามารถเริ่มต้นได้ - มีปัญหาเรื่อง module imports
- Frontend Server ไม่สามารถเริ่มต้นได้ - ไม่พบ package.json

## **วิธีแก้ไข:**

### **1. แก้ไข Terminal Directory:**
```bash
# ไปที่ project root
cd F:\repos\chonost-manuscript-os

# ตรวจสอบ current directory
pwd
```

### **2. เริ่มต้น Frontend Development Server:**
```bash
# ไปที่ frontend directory
cd packages/frontend

# ตรวจสอบ package.json
ls package.json

# เริ่มต้น development server
npm run dev
```

### **3. เริ่มต้น Backend API Server:**
```bash
# เปิด terminal ใหม่ (หรือ tab ใหม่)
# ไปที่ project root
cd F:\repos\chonost-manuscript-os

# ไปที่ backend directory
cd services/local-rag

# ตรวจสอบ dependencies
pip install fastapi uvicorn requests

# เริ่มต้น simple server
python simple_server.py
```

### **4. ทดสอบ Servers:**
```bash
# เปิด terminal ใหม่
# ไปที่ project root
cd F:\repos\chonost-manuscript-os

# รัน test script
python test_servers.py
```

## **URLs สำหรับทดสอบ:**

### **Frontend:**
- **Development Server:** http://localhost:3000
- **The Trinity Layout:** ตรวจสอบ Editor/Whiteboard switching
- **KnowledgeExplorer:** ตรวจสอบ sidebar ซ้าย
- **AssistantPanel:** ตรวจสอบ sidebar ขวา

### **Backend API:**
- **Health Check:** http://localhost:8000/health
- **API Docs:** http://localhost:8000/docs
- **RAG Info:** http://localhost:8000/api/rag/info
- **RAG Search:** http://localhost:8000/api/rag/search?query=Trinity Layout

## **Troubleshooting:**

### **Frontend Issues:**
1. **npm error ENOENT:** ตรวจสอบว่า package.json มีอยู่
2. **Port 3000 in use:** เปลี่ยน port ใน vite.config.js
3. **Module not found:** รัน `npm install`

### **Backend Issues:**
1. **ModuleNotFoundError:** ติดตั้ง dependencies ด้วย `pip install`
2. **Port 8000 in use:** เปลี่ยน port ใน simple_server.py
3. **Import error:** ตรวจสอบ Python path

### **General Issues:**
1. **Directory wrong:** ใช้ `cd F:\repos\chonost-manuscript-os` เสมอ
2. **Permission denied:** รัน terminal as Administrator
3. **Firewall:** อนุญาต ports 3000 และ 8000

## **Next Steps:**
1. ✅ แก้ไข Terminal Directory
2. ✅ เริ่มต้น Frontend Server
3. ✅ เริ่มต้น Backend Server
4. ✅ ทดสอบ The Trinity Layout
5. ✅ ทดสอบ RAG Functionality
6. 🔄 พัฒนา Features เพิ่มเติม
