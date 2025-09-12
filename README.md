# Chonost Manuscript OS v2.1.0

ระบบจัดการต้นฉบับนวนิยายอัจฉริยะ (Intelligent Manuscript Management System)

## 📚 **เอกสารทั้งหมดอยู่ใน [docs/](docs/) folder**

โปรเจ็คนี้มีการจัดระเบียบใหม่เพื่อให้โครงสร้างชัดเจนและง่ายต่อการดูแล

### 🚀 **เริ่มต้นใช้งานอย่างรวดเร็ว**

```bash
# Clone repository
git clone https://github.com/your-org/chonost-manuscript-os.git
cd chonost-manuscript-os

# Start services
docker-compose up -d
```

### 📖 **เอกสารที่สำคัญ**

- **[README หลัก](docs/README.md)** - ภาพรวมโปรเจ็คและการติดตั้ง
- **[API Documentation](docs/API_DOCUMENTATION.md)** - API endpoints ทั้งหมด
- **[Development Roadmap](docs/DEVELOPMENT_ROADMAP.md)** - แผนการพัฒนาต่อไป
- **[Security Policy](docs/SECURITY.md)** - นโยบายความปลอดภัย
- **[Project Status](docs/PROJECT_STATUS_REPORT.md)** - สถานะปัจจุบัน

### 🏗️ **โครงสร้างโปรเจ็ค**

```
chonost-manuscript-os/
├── apps/             # แอปพลิเคชันหลัก (Multi-platform Frontend)
│   └── frontend/     # Frontend หลัก (Desktop, Mobile, Web, Chat)
├── packages/         # แพ็คเกจเสริม (Backend, AI, Shared)
├── services/         # Microservices
├── FileSystemMCP/    # MCP Server Implementation
├── docs/             # เอกสารทั้งหมด ⭐
├── scripts/          # Build & Test Scripts
├── data/             # ข้อมูลและ Datasets
└── database/         # Database Configurations
```

### 🔧 **การพัฒนา**

ดูรายละเอียดการพัฒนาใน [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)

---

**📁 ดูเอกสารเพิ่มเติมใน [docs/](docs/) folder**
