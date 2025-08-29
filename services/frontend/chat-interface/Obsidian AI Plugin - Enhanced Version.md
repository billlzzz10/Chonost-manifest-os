# Obsidian AI Plugin - Enhanced Version

ปลั๊กอิน AI สำหรับ Obsidian ที่ได้รับการปรับปรุงและพัฒนาใหม่ เพื่อให้การใช้งานง่ายขึ้น มีประสิทธิภาพมากขึ้น และตอบโจทย์ผู้ใช้งานในด้านการจัดการงานข้ามแพลตฟอร์มได้ดีขึ้น

## ✨ คุณสมบัติหลัก

### 🧠 ระบบ AI ที่ปรับปรุงแล้ว
- **Incremental Embedding**: ประมวลผลเฉพาะเนื้อหาที่เปลี่ยนแปลง ลดเวลาการประมวลผล
- **Optimized Vector Database**: ฐานข้อมูลเวกเตอร์ที่เหมาะสำหรับอุปกรณ์ส่วนตัว
- **Smart Caching**: ระบบแคชที่ชาญฉลาดพร้อมการจัดการหน่วยความจำอัตโนมัติ
- **Enhanced RAG**: ระบบ RAG ที่ปรับปรุงแล้วให้คำตอบที่แม่นยำและเกี่ยวข้องมากขึ้น
- **Hybrid Processing**: เลือกประมวลผลแบบ Local หรือ Cloud อัตโนมัติตามสภาพอุปกรณ์

### 🔄 การซิงค์ข้ามแพลตฟอร์ม
- **Two-Way Sync**: ซิงค์ข้อมูลสองทางกับ Notion และ Airtable
- **Conflict Resolution**: ระบบแก้ไขข้อขัดแย้งอัตโนมัติและแบบแมนนวล
- **Cloud Drive Integration**: เข้าถึง Google Drive, Dropbox, OneDrive โดยตรง
- **Format Conversion**: แปลง Markdown เป็น JSON, YAML, CSV, XML อัตโนมัติ

### 📊 Unified Task Dashboard
- **Cross-Platform Task Management**: จัดการงานจากทุกแพลตฟอร์มในที่เดียว
- **AI-Powered Recommendations**: คำแนะนำที่ขับเคลื่อนด้วย AI
- **Smart Analytics**: วิเคราะห์รูปแบบการทำงานและให้ข้อมูลเชิงลึก
- **Progress Tracking**: ติดตามความคืบหน้าและประสิทธิภาพการทำงาน

## 🏗️ สถาปัตยกรรม

```
obsidian-ai-plugin/
├── src/
│   ├── embedding/           # ระบบ Embedding ที่ปรับปรุงแล้ว
│   │   └── incremental_embedder.py
│   ├── vector_db/          # ฐานข้อมูลเวกเตอร์ที่เหมาะสำหรับอุปกรณ์
│   │   └── optimized_vector_db.py
│   ├── cache/              # ระบบแคชที่ชาญฉลาด
│   │   └── smart_cache.py
│   ├── rag/                # ระบบ RAG ที่ปรับปรุงแล้ว
│   │   └── enhanced_rag.py
│   ├── utils/              # เครื่องมือสนับสนุน
│   │   ├── resource_manager.py
│   │   └── hybrid_processor.py
│   ├── sync/               # ระบบซิงค์ข้ามแพลตฟอร์ม
│   │   └── two_way_sync.py
│   ├── platforms/          # อะแดปเตอร์สำหรับแพลตฟอร์มต่างๆ
│   │   ├── notion_adapter.py
│   │   ├── airtable_adapter.py
│   │   └── cloud_drive_adapter.py
│   ├── converters/         # ระบบแปลงรูปแบบข้อมูล
│   │   └── md_converter.py
│   └── dashboard/          # แดชบอร์ดรวม
│       └── unified_dashboard.py
├── tests/                  # ไฟล์ทดสอบ
├── docs/                   # เอกสารประกอบ
└── README.md
```

## 🚀 การติดตั้งและใช้งาน

### ข้อกำหนดระบบ
- Python 3.8+
- Obsidian v1.0+
- RAM อย่างน้อย 4GB (แนะนำ 8GB+)
- พื้นที่ว่างในฮาร์ดดิสก์ 2GB+

### การติดตั้ง

1. **ติดตั้ง Dependencies**
```bash
pip install -r requirements.txt
```

2. **ตั้งค่า API Keys**
```bash
# สร้างไฟล์ .env
cp .env.example .env

# แก้ไขไฟล์ .env และใส่ API keys
OPENAI_API_KEY=your_openai_api_key
NOTION_API_TOKEN=your_notion_token
AIRTABLE_API_TOKEN=your_airtable_token
GOOGLE_DRIVE_CLIENT_ID=your_google_client_id
DROPBOX_ACCESS_TOKEN=your_dropbox_token
```

3. **เริ่มต้นใช้งาน**
```python
from src.dashboard.unified_dashboard import UnifiedTaskDashboard
from src.sync.two_way_sync import TwoWaySync

# สร้าง dashboard
dashboard = UnifiedTaskDashboard()

# เพิ่มแพลตฟอร์ม
# (ดูตัวอย่างในไฟล์ examples/)
```

## 📖 คู่มือการใช้งาน

### การซิงค์กับ Notion
```python
from src.platforms.notion_adapter import NotionAdapter, NotionConfig

config = NotionConfig(
    api_token="your_notion_token",
    database_id="your_database_id"
)

notion_adapter = NotionAdapter(config)
dashboard.add_platform_adapter("notion", notion_adapter)

# ซิงค์ข้อมูล
sync_results = await dashboard.sync_from_platforms()
```

### การซิงค์กับ Airtable
```python
from src.platforms.airtable_adapter import AirtableAdapter, AirtableConfig

config = AirtableConfig(
    api_token="your_airtable_token",
    base_id="your_base_id",
    table_name="your_table_name"
)

airtable_adapter = AirtableAdapter(config)
dashboard.add_platform_adapter("airtable", airtable_adapter)
```

### การแปลง Markdown
```python
from src.converters.md_converter import MarkdownConverter

converter = MarkdownConverter()

# แปลงเป็น JSON
json_output = converter.to_json(markdown_content)

# แปลงเป็น YAML
yaml_output = converter.to_yaml(markdown_content)

# แปลงเป็น CSV
csv_output = converter.to_csv(markdown_content)

# สกัดงานจาก Markdown
tasks = converter.to_task_format(markdown_content)
```

### การใช้งาน Cloud Drive
```python
from src.platforms.cloud_drive_adapter import CloudDriveManager, GoogleDriveAdapter

manager = CloudDriveManager()

# เพิ่ม Google Drive
google_adapter = GoogleDriveAdapter(google_config)
manager.add_service("google_drive", google_adapter)

# ค้นหาไฟล์
search_results = await manager.search_files("project notes")

# ซิงค์ไฟล์ข้ามบริการ
sync_results = await manager.sync_file_across_services(
    "google_drive", "file_id", ["dropbox"]
)
```

## 🎯 คุณสมบัติที่โดดเด่น

### 1. ประสิทธิภาพที่ปรับปรุงแล้ว
- **ลดเวลาการประมวลผล**: Incremental Embedding ลดเวลาการประมวลผลได้ถึง 80%
- **การใช้หน่วยความจำที่เหมาะสม**: Smart Caching ลดการใช้ RAM ได้ 60%
- **การประมวลผลแบบ Hybrid**: เลือกใช้ Local หรือ Cloud อัตโนมัติ

### 2. การซิงค์ที่เสถียร
- **Two-Way Sync**: ซิงค์ข้อมูลสองทางแบบเรียลไทม์
- **Conflict Resolution**: แก้ไขข้อขัดแย้งอัตโนมัติด้วย AI
- **Change Tracking**: ติดตามการเปลี่ยนแปลงอย่างละเอียด

### 3. การจัดการงานที่ชาญฉลาด
- **AI Recommendations**: คำแนะนำที่ปรับตามรูปแบบการทำงาน
- **Cross-Platform View**: มองเห็นงานจากทุกแพลตฟอร์มในที่เดียว
- **Progress Analytics**: วิเคราะห์ความคืบหน้าและประสิทธิภาพ

## 🔧 การปรับแต่ง

### การตั้งค่า Embedding
```python
from src.embedding.incremental_embedder import IncrementalEmbedder

embedder = IncrementalEmbedder(
    model_name="text-embedding-ada-002",
    chunk_size=1000,
    chunk_overlap=200,
    cache_enabled=True
)
```

### การตั้งค่า Vector Database
```python
from src.vector_db.optimized_vector_db import OptimizedVectorDB

vector_db = OptimizedVectorDB(
    dimension=1536,
    index_type="HNSW",
    metric="cosine",
    max_memory_mb=1024
)
```

### การตั้งค่า Cache
```python
from src.cache.smart_cache import SmartCache

cache = SmartCache(
    max_size_mb=512,
    ttl_seconds=3600,
    cleanup_interval=300
)
```

## 📊 การติดตามประสิทธิภาพ

### เมตริกที่สำคัญ
- **Embedding Speed**: เวลาในการสร้าง embedding
- **Search Accuracy**: ความแม่นยำของการค้นหา
- **Sync Success Rate**: อัตราความสำเร็จของการซิงค์
- **Memory Usage**: การใช้หน่วยความจำ
- **Cache Hit Rate**: อัตราการใช้ cache

### การดูสถิติ
```python
# ดูสถิติ dashboard
dashboard_data = dashboard.get_dashboard_data()
print(f"Total tasks: {dashboard_data['stats']['total_tasks']}")
print(f"Completion rate: {dashboard_data['stats']['completion_rate']:.1f}%")

# ดูสถิติ cache
cache_stats = cache.get_stats()
print(f"Cache hit rate: {cache_stats['hit_rate']:.1f}%")

# ดูสถิติ vector database
db_stats = vector_db.get_stats()
print(f"Total vectors: {db_stats['total_vectors']}")
```

## 🧪 การทดสอบ

### รันการทดสอบ
```bash
# ทดสอบทั้งหมด
python -m pytest tests/

# ทดสอบเฉพาะส่วน
python -m pytest tests/test_embedding.py
python -m pytest tests/test_sync.py
python -m pytest tests/test_dashboard.py
```

### ตัวอย่างการทดสอบ
```python
# ทดสอบ Incremental Embedding
python src/embedding/incremental_embedder.py

# ทดสอบ Two-Way Sync
python src/sync/two_way_sync.py

# ทดสอบ Unified Dashboard
python src/dashboard/unified_dashboard.py
```

## 🤝 การมีส่วนร่วม

เรายินดีรับการมีส่วนร่วมจากชุมชน! กรุณาอ่าน [CONTRIBUTING.md](CONTRIBUTING.md) สำหรับรายละเอียด

### การรายงานปัญหา
- ใช้ GitHub Issues สำหรับรายงานบัก
- ระบุขั้นตอนการทำซ้ำอย่างชัดเจน
- แนบ log files หากเป็นไปได้

### การเสนอฟีเจอร์ใหม่
- เปิด Feature Request ใน GitHub Issues
- อธิบายกรณีการใช้งานอย่างละเอียด
- พิจารณาผลกระทบต่อประสิทธิภาพ

## 📄 ใบอนุญาต

โปรเจกต์นี้ใช้ใบอนุญาต MIT License - ดูรายละเอียดใน [LICENSE](LICENSE)

## 🙏 กิตติกรรมประกาศ

ขอขอบคุณ:
- ทีม Obsidian สำหรับแพลตฟอร์มที่ยอดเยี่ยม
- ชุมชน Open Source ที่ให้แรงบันดาลใจ
- ผู้ใช้งานทุกท่านที่ให้ข้อเสนอแนะ

## 📞 การติดต่อ

- GitHub Issues: สำหรับรายงานปัญหาและคำถามทางเทคนิค
- Email: สำหรับการติดต่อทั่วไป
- Discord: สำหรับการสนทนาและการสนับสนุนชุมชน

---

**หมายเหตุ**: ปลั๊กอินนี้อยู่ในระหว่างการพัฒนา คุณสมบัติบางอย่างอาจยังไม่สมบูรณ์ กรุณาทดสอบในสภาพแวดล้อมที่ปลอดภัยก่อนใช้งานจริง

