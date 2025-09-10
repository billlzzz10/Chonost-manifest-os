# 🤖 AI Orchestrator

* * PostgreSQL Database และ FastAPI Application สำหรับ AI Tool Management System**

## 📋 ภาพรวม

AI Orchestrator เป็นระบบจัดการเครื่องมือ AI ที่ครบครัน ประกอบด้วย:

- ** PostgreSQL Database Schema** - ออกแบบสำหรับจัดการ AI tools, nodes, และ artifacts
- ** SQLAlchemy Models** - ORM models พร้อม Pydantic schemas
- ** FastAPI REST API** - API endpoints ครบครันสำหรับจัดการระบบ
- ** Alembic Migrations** - Database versioning และ schema management
- ** Advanced Queries** - ฟังก์ชัน query ที่ซับซ้อนสำหรับ monitoring และ analytics

## 🏗️ โครงสร้างโปรเจกต์

```
ai_orchestrator/
├── alembic/                          # Database migrations
│   ├── versions/
│   │   └── cbc076c931f8_initial_ai_orchestrator_schema.py
│   ├── env.py
│   └── alembic.ini
├── ai_orchestrator_models.py         # SQLAlchemy models + Pydantic schemas
├── ai_orchestrator_crud.py           # CRUD operations
├── ai_orchestrator_api.py            # FastAPI application
├── ai_orchestrator_schema.sql        # Raw SQL schema
├── ai_orchestrator_queries.sql       # Advanced SQL queries
├── ai_orchestrator_requirements.txt  # Python dependencies
├── AI_ORCHESTRATOR_README.md         # This file
└── AI_ORCHESTRATOR_DB_README.md      # Database documentation
```

## 🚀 การติดตั้งและใช้งาน

### 1. ติดตั้ง Dependencies

```
# ติดตั้ง Python dependencies
pip install -r ai_orchestrator_requirements.txt

# หรือใช้ virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# หรือ
venv\Scripts\activate     # Windows
pip install -r ai_orchestrator_requirements.txt
```

### 2. ตั้งค่า Database

#### 2.1 สร้าง PostgreSQL Database

```
- - สร้าง database
CREATE DATABASE ai_orchestrator;

- - สร้าง user (optional)
CREATE USER ai_orchestrator_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_orchestrator TO ai_orchestrator_user;
```

#### 2.2 ตั้งค่า Database URL

แก้ไขไฟล์ ` ai_orchestrator_api.py` :

```
# เปลี่ยนจาก
DATABASE_URL = "postgresql://username:password@localhost/ai_orchestrator"

# เป็น
DATABASE_URL = "postgresql://your_username:your_password@localhost/ai_orchestrator"
```

หรือใช้ environment variable:

```
export DATABASE_URL="postgresql://your_username:your_password@localhost/ai_orchestrator"
```

### 3. รัน Database Migrations

```
# สร้าง database tables
python -m alembic upgrade head

# ตรวจสอบ migration status
python -m alembic current

# rollback ถ้าต้องการ
python -m alembic downgrade -1
```

### 4. รัน FastAPI Application

```
# รัน development server
python ai_orchestrator_api.py

# หรือใช้ uvicorn โดยตรง
uvicorn ai_orchestrator_api:app --host 0.0.0.0 --port 8000 --reload
```

### 5. เข้าถึง API Documentation

- ** Swagger UI**: http://localhost:8000/docs
- ** ReDoc**: http://localhost:8000/redoc
- ** Health Check**: http://localhost:8000/health

## 📊 Database Schema

### Tables

1. ** ` nodes` ** - Worker nodes สำหรับ AI tool execution
2. ** ` tools` ** - AI tools ที่มีอยู่ในระบบ
3. ** ` tool_tags` ** - Many-to-many relationship ระหว่าง tools และ tags
4. ** ` artifacts` ** - Metadata ของ output files ที่สร้างโดย tools

### Key Features

- ** UUID Primary Keys** - สำหรับ scalability และ security
- ** JSONB Columns** - สำหรับ flexible schema storage
- ** Foreign Key Constraints** - ด้วย ` ON DELETE SET NULL` และ ` ON DELETE CASCADE`
- ** Indexes** - รวมถึง GIN indexes สำหรับ JSONB queries
- ** Triggers** - อัปเดต ` updated_at` timestamps อัตโนมัติ
- ** Views** - สำหรับ common queries

## 🔧 API Endpoints

### Health Check
- ` GET /` - Root endpoint
- ` GET /health` - Health check

### Nodes Management
- ` POST /nodes/` - สร้าง node ใหม่
- ` GET /nodes/` - ดู nodes ทั้งหมด (with pagination)
- ` GET /nodes/{node_id}` - ดู node เฉพาะ
- ` GET /nodes/type/{node_type}` - ดู nodes ตาม type
- ` GET /nodes/active/` - ดู active nodes
- ` PUT /nodes/{node_id}` - อัปเดต node
- ` DELETE /nodes/{node_id}` - ลบ node

### Tools Management
- ` POST /tools/` - สร้าง tool ใหม่
- ` GET /tools/` - ดู tools ทั้งหมด (with pagination)
- ` GET /tools/{tool_id}` - ดู tool เฉพาะ
- ` GET /tools/name/{tool_name}` - ดู tool ตามชื่อ
- ` GET /tools/category/{category}` - ดู tools ตาม category
- ` GET /tools/active/` - ดู active tools
- ` PUT /tools/{tool_id}` - อัปเดต tool
- ` DELETE /tools/{tool_id}` - ลบ tool

### Tool Tags
- ` POST /tools/{tool_id}/tags/{tag_name}` - เพิ่ม tag ให้ tool
- ` DELETE /tools/{tool_id}/tags/{tag_name}` - ลบ tag จาก tool
- ` GET /tools/tags/{tag_search}` - ค้นหา tools ตาม tag

### Artifacts Management
- ` POST /artifacts/` - สร้าง artifact ใหม่
- ` GET /artifacts/` - ดู artifacts ทั้งหมด (with pagination)
- ` GET /artifacts/{artifact_id}` - ดู artifact เฉพาะ
- ` GET /artifacts/tool/{tool_id}` - ดู artifacts ของ tool เฉพาะ
- ` GET /artifacts/large/` - ดู large artifacts
- ` DELETE /artifacts/{artifact_id}` - ลบ artifact

### Advanced Queries
- ` GET /queries/active-tools-with-nodes` - ดู active tools พร้อม node info
- ` GET /queries/tools-by-category-with-tags` - ดู tools ตาม category พร้อม tags
- ` GET /queries/node-health-status` - ดู node health status
- ` GET /queries/large-artifacts-by-tool` - ดู large artifacts ตาม tool
- ` GET /queries/search-tools-by-schema` - ค้นหา tools ตาม JSON schema

### Maintenance
- ` POST /maintenance/cleanup-orphaned-artifacts` - ลบ orphaned artifacts
- ` POST /maintenance/update-tool-status` - อัปเดต tool status ตาม node status
- ` GET /maintenance/tools-without-nodes` - ดู tools ที่ไม่มี node

### Monitoring
- ` GET /monitoring/storage-usage-by-category` - ดู storage usage ตาม category
- ` GET /monitoring/tool-usage-statistics` - ดู tool usage statistics
- ` GET /monitoring/data-integrity` - ตรวจสอบ data integrity

### Statistics
- ` GET /stats/summary` - ดู system summary

## 💡 ตัวอย่างการใช้งาน

### 1. สร้าง Node และ Tool

```
import requests
import json

# สร้าง node
node_data = {
    "node_type": "TOOL_EXECUTOR",
    "address": "http://worker-1:8000",
    "status": "ACTIVE"
}
response = requests.post("http://localhost:8000/nodes/", json=node_data)
node = response.json()

# สร้าง tool
tool_data = {
    "name": "file_analyzer",
    "description": "Analyze file content and extract metadata",
    "category": "ANALYSIS",
    "version": "1.0.0",
    "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}}},
    "output_schema": {"type": "object", "properties": {"metadata": {"type": "object"}}},
    "target_node_id": str(node["node_id"])
}
response = requests.post("http://localhost:8000/tools/", json=tool_data)
tool = response.json()
```

### 2. เพิ่ม Tag และ Artifact

```
# เพิ่ม tag
requests.post(f"http://localhost:8000/tools/{tool['tool_id']}/tags/analysis")

# สร้าง artifact
artifact_data = {
    "file_name": "analysis_report.json",
    "mime_type": "application/json",
    "storage_pointer": "s3://artifacts-bucket/reports/analysis_report.json",
    "size_bytes": 2048,
    "created_by_tool_id": str(tool["tool_id"])
}
response = requests.post("http://localhost:8000/artifacts/", json=artifact_data)
```

### 3. ดู Advanced Queries

```
# ดู active tools with nodes
response = requests.get("http://localhost:8000/queries/active-tools-with-nodes")
active_tools = response.json()

# ดู node health status
response = requests.get("http://localhost:8000/queries/node-health-status")
node_health = response.json()

# ดู system summary
response = requests.get("http://localhost:8000/stats/summary")
summary = response.json()
```

## 🔍 การพัฒนา

### Code Quality

```
# Format code
black ai_orchestrator_* .py

# Sort imports
isort ai_orchestrator_* .py

# Type checking
mypy ai_orchestrator_* .py

# Linting
flake8 ai_orchestrator_* .py
```

### Testing

```
# รัน tests
pytest

# รัน tests with coverage
pytest --cov=ai_orchestrator

# รัน specific test
pytest test_ai_orchestrator.py::test_create_node
```

### Database Development

```
# สร้าง migration ใหม่
python -m alembic revision -m "Add new feature"

# แก้ไข migration file แล้วรัน
python -m alembic upgrade head

# ดู migration history
python -m alembic history
```

## 📈 Performance และ Monitoring

### Database Performance

- **Indexes**: มี indexes สำหรับ columns ที่ใช้ query บ่อย
- ** JSONB Indexes**: GIN indexes สำหรับ JSON schema queries
- ** Connection Pooling**: SQLAlchemy connection pooling
- ** Query Optimization**: ใช้ SQLAlchemy query optimization

### API Performance

- ** Pagination**: ทุก list endpoints มี pagination
- ** Response Caching**: สามารถเพิ่ม Redis caching ได้
- ** Async Support**: FastAPI async endpoints
- ** Background Tasks**: สามารถเพิ่ม Celery ได้

### Monitoring

- ** Health Checks**: ` /health` endpoint
- ** Data Integrity**: ` /monitoring/data-integrity` endpoint
- ** Usage Statistics**: ` /monitoring/tool-usage-statistics` endpoint
- ** Storage Monitoring**: ` /monitoring/storage-usage-by-category` endpoint

## 🔒 Security

### Database Security

- ** UUID Primary Keys**: ป้องกัน enumeration attacks
- ** Input Validation**: Pydantic validation
- ** SQL Injection Protection**: SQLAlchemy ORM
- ** Connection Security**: SSL/TLS สำหรับ database connections

### API Security

- ** Input Validation**: Pydantic models
- ** Rate Limiting**: สามารถเพิ่มได้
- ** Authentication**: สามารถเพิ่ม JWT authentication ได้
- ** CORS**: Configurable CORS settings

## 🚀 Production Deployment

### Docker

```
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "ai_orchestrator_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
```

### Health Checks

```
# Database health
python -c "from ai_orchestrator_api import get_db; next(get_db())"

# API health
curl http://localhost:8000/health
```

## 📚 Documentation

- ** API Documentation**: http://localhost:8000/docs
- ** Database Schema**: ดู ` AI_ORCHESTRATOR_DB_README.md`
- ** SQL Queries**: ดู ` ai_orchestrator_queries.sql`
- ** Alembic Migrations**: ดู ` alembic/versions/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## 📄 License

MIT License - ดู LICENSE file สำหรับรายละเอียด

## 🆘 Support

หากมีปัญหาหรือคำถาม:

1. ตรวจสอบ documentation
2. ดู API docs ที่ ` /docs`
3. ตรวจสอบ logs
4. สร้าง issue ใน repository

- --

* * สร้างโดย: Orion Senior Dev**
* * วันที่: 2025-08-21**

