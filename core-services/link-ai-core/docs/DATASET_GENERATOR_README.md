# 📊 AI Agent Multi-Action Dataset Generator

ระบบอัตโนมัติสำหรับการสร้างดาต้าเซ็ตจาก log และข้อมูลต่างๆ ในโปรเจ็ค Chonost

## 🎯 วัตถุประสงค์

ระบบนี้ถูกออกแบบมาเพื่อแปลงข้อมูล log ที่ดูวุ่นวายให้กลายเป็น **ทรัพย์สินดิจิทัล (Digital Asset)** ที่จะทำให้ AI Agent ของ Chonost ** ฉลาดขึ้นในบริบทของโปรเจกต์โดยเฉพาะ** ## 📋 ประเภทของดาต้าเซ็ตที่สร้าง

### 1. ** Instruction Fine-Tuning (IFT) Dataset** - ** เป้าหมาย:** สอนโมเดล AI ให้ "คิดและทำ" เหมือนผู้ช่วยพัฒนาในอุดมคติ
- ** โครงสร้าง:** `(Instruction, Context, Response)` - ** ไฟล์:** ` datasets/instruction_fine_tuning/instruction_fine_tuning_dataset.jsonl` ### 2. ** RAG Knowledge Base Dataset** - ** เป้าหมาย:** สร้างคลังความรู้สำหรับการค้นหาและตอบคำถาม
- ** โครงสร้าง:** Chunks ของข้อความ + Metadata
- ** ไฟล์:** ` datasets/rag_knowledge_base/rag_knowledge_base.json` ### 3. ** Forecasting & Prediction Dataset** - ** เป้าหมาย:** ฝึกโมเดลให้คาดการณ์แนวโน้มและผลลัพธ์
- ** โครงสร้าง:** ` (Previous State, Action, New State, Outcome)` - ** ไฟล์:** ` datasets/forecasting_prediction/forecasting_dataset.json` ## 🚀 การเริ่มต้นใช้งาน

### การติดตั้ง

```
# ติดตั้ง dependencies
pip install -r requirements_dataset.txt

# หรือใช้ Makefile
make setup
```

### การใช้งานพื้นฐาน

```
# 1. สร้างไฟล์ log ตัวอย่าง
make create-example-log

# 2. สร้างดาต้าเซ็ตจากไฟล์ตัวอย่าง
make generate-example

# 3. ดูผลลัพธ์
make list-datasets
make show-stats
```

### การใช้งานกับไฟล์ log ของคุณ

```
# สร้างดาต้าเซ็ตจากไฟล์ log ของคุณ
make generate-datasets LOG_FILE=path/to/your/log.txt

# ตัวอย่าง
make generate-datasets LOG_FILE=logs/conversation_2024_12_19.txt
```

## 📁 โครงสร้างไฟล์

```
datasets/
├── instruction_fine_tuning/
│   └── instruction_fine_tuning_dataset.jsonl
├── rag_knowledge_base/
│   └── rag_knowledge_base.json
├── forecasting_prediction/
│   └── forecasting_dataset.json
└── dataset_generation_summary.json
```

## 🔧 คำสั่ง Makefile ที่มีประโยชน์

```
# แสดงความช่วยเหลือ
make help

# ติดตั้งระบบ
make setup

# สร้างดาต้าเซ็ต
make generate-datasets LOG_FILE=your_log.txt

# ทดสอบระบบ
make test

# ลบไฟล์ดาต้าเซ็ต
make clean

# แสดงรายการดาต้าเซ็ต
make list-datasets

# แสดงสถิติ
make show-stats

# เริ่มต้นใช้งานอย่างรวดเร็ว
make quick-start
```

## 📝 รูปแบบไฟล์ Log ที่รองรับ

ระบบรองรับไฟล์ log ที่มีรูปแบบดังนี้:

```
User: คำสั่งหรือคำถามของผู้ใช้
- --
AI: คำตอบหรือการตอบสนองของ AI
- --
System: ข้อความระบบหรือ error
- --
User: คำสั่งต่อไป
- --
AI: คำตอบต่อไป
```

### ตัวอย่างไฟล์ log

```
User: วิเคราะห์และสร้างดาต้าเซ็ตตามข้อมูลนี้
- --
AI: ฉันจะวิเคราะห์และสร้างดาต้าเซ็ตตามที่คุณต้องการ
- --
User: แล้วก็ลองใช้ออลามาลิสเช้คเพิ่มเติมดูว่าจะเอาเอเจนตัวไหนไปทำอะไรบ้าง
- --
AI: ฉันจะตรวจสอบ Ollama และแนะนำการใช้งาน AI agents
- --
System: Error occurred: Connection timeout
- --
AI: ฉันจะแก้ไขปัญหาการเชื่อมต่อ
```

## 🔍 การทำงานของระบบ

### 1. การสกัดและทำความสะอาดข้อมูล
- แยกบล็อกตาม ` ---`
- ระบุประเภทของแต่ละบล็อก (User, AI, System)
- ทำความสะอาดข้อความ (ลบ request ID, แก้ไขอักขระผิดเพี้ยน)

### 2. การสร้างโครงสร้างและ Annotation
- สร้าง ` DatasetEntry` objects
- สกัด metadata (file path, language, etc.)
- สร้างความสัมพันธ์ระหว่าง entries

### 3. การสร้างดาต้าเซ็ตแต่ละประเภท
- ** IFT:** สร้างคู่ (Instruction, Response)
- ** RAG:** แบ่งเนื้อหาเป็น chunks
- ** Forecast:** สร้างลำดับ (State, Action, Outcome)

## 📊 ตัวอย่างผลลัพธ์

### IFT Dataset (JSONL format)

```
{
  "instruction": "วิเคราะห์และสร้างดาต้าเซ็ตตามข้อมูลนี้",
  "context": "System: Error occurred: Connection timeout",
  "response": "ฉันจะวิเคราะห์และสร้างดาต้าเซ็ตตามที่คุณต้องการ",
  "metadata": {
    "source_entry": "log_entry_001",
    "response_entry": "log_entry_002",
    "type": "Instruction"
  }
}
```

### RAG Dataset (JSON format)

```
{
  "dataset_name": "rag_knowledge_base",
  "description": "Knowledge base for RAG system",
  "version": "1.0.0",
  "created_date": "2024-12-19T10:30:00Z",
  "chunks": [
    {
      "chunk_id": "log_entry_001_chunk_0",
      "content": "User: วิเคราะห์และสร้างดาต้าเซ็ต...",
      "metadata": {
        "source_entry": "log_entry_001",
        "chunk_index": 0,
        "file_path": "",
        "language": "",
        "type": "Instruction"
      }
    }
  ]
}
```

## 🛠 ️ การปรับแต่งและขยาย

### การเพิ่มประเภทข้อมูลใหม่

แก้ไขไฟล์ ` src/dataset_generator.py` :

```
def _classify_block(self, block: str) -> str:
    # เพิ่มเงื่อนไขใหม่
    if 'your_keyword' in block.lower():
        return 'YourNewType'
    # ... existing code
```

### การปรับแต่งการ chunking

```
def _create_chunks(self, content: str, max_chunk_size: int = 1000) -> List[str]:
    # ปรับขนาด chunk หรือวิธีการแบ่ง
    # ... existing code
```

## 🔍 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

1. ** Import Error:** ```bash
   # ตรวจสอบว่าไฟล์ dataset_generator.py อยู่ใน src/
   ls src/dataset_generator.py
   ```

2. ** Log file not found:** ```bash
   # ตรวจสอบ path ของไฟล์ log
   ls -la your_log_file.txt
   ```

3. ** No datasets generated:** ```bash
   # ตรวจสอบรูปแบบของไฟล์ log
   head -10 your_log_file.txt
   ```

### การ Debug

```
# รันในโหมด verbose
python -v scripts/generate_datasets.py your_log.txt

# ตรวจสอบ logs
tail -f logs/dataset_generation.log
```

## 📈 การใช้งานขั้นสูง

### การสร้าง Embeddings

```
# เพิ่มใน requirements_dataset.txt
# sentence-transformers>=2.2.0

# ใช้ใน dataset_generator.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks)
```

### การเชื่อมต่อกับ Vector Database

```
# เพิ่มใน requirements_dataset.txt
# qdrant-client>=1.1.0

# ใช้ใน dataset_generator.py
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)
client.upsert(collection_name="rag_chunks", points=embeddings)
```

## 🤝 การมีส่วนร่วม

1. Fork โปรเจ็ค
2. สร้าง feature branch
3. Commit การเปลี่ยนแปลง
4. Push ไปยัง branch
5. สร้าง Pull Request

## 📄 License

MIT License - ดูรายละเอียดในไฟล์ LICENSE

## 📞 การติดต่อ

หากมีคำถามหรือปัญหา กรุณาสร้าง Issue ใน GitHub repository

