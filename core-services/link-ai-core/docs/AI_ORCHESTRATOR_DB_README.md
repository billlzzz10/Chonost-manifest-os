# 🗄️ AI Orchestrator Database Schema

## 📋 ภาพรวม

PostgreSQL database schema สำหรับระบบ AI Orchestrator ที่ออกแบบมาเพื่อจัดการ Worker Nodes, AI Tools, และ Artifacts อย่างมีประสิทธิภาพ

## 🏗️ โครงสร้างฐานข้อมูล

### 📊 ตารางหลัก

#### 1. **nodes** - Worker Nodes Management
```
CREATE TABLE nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    node_type VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'INACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

* * Node Types:**
- ` TOOL_EXECUTOR` - สำหรับรัน AI tools
- ` OBSERVATION_NODE` - สำหรับติดตามและเก็บข้อมูล
- ` ANALYSIS_NODE` - สำหรับวิเคราะห์ข้อมูล
- ` STORAGE_NODE` - สำหรับจัดการ storage

* * Status Values:**
- ` ACTIVE` - ทำงานปกติ
- ` INACTIVE` - ไม่ทำงาน
- ` MAINTENANCE` - กำลังบำรุงรักษา
- ` ERROR` - มีข้อผิดพลาด

#### 2. ** tools** - AI Tools Management
```
CREATE TABLE tools (
    tool_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    status VARCHAR(20) NOT NULL DEFAULT 'ENABLED',
    input_schema JSONB,
    output_schema JSONB,
    target_node_id UUID REFERENCES nodes(node_id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

* * Categories:**
- ` ANALYSIS` - เครื่องมือวิเคราะห์
- ` PROCESSING` - เครื่องมือประมวลผล
- ` VALIDATION` - เครื่องมือตรวจสอบ
- ` STORAGE` - เครื่องมือจัดการ storage

#### 3. ** tool_tags** - Many-to-Many Relationship
```
CREATE TABLE tool_tags (
    tool_id UUID NOT NULL REFERENCES tools(tool_id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (tool_id, tag_name)
);
```

#### 4. ** artifacts** - File Output Metadata
```
CREATE TABLE artifacts (
    artifact_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    storage_pointer TEXT NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_tool_id UUID REFERENCES tools(tool_id) ON DELETE SET NULL
);
```

## 🔗 ความสัมพันธ์ระหว่างตาราง

```
nodes (1) ←→ (N) tools
tools (1) ←→ (N) tool_tags
tools (1) ←→ (N) artifacts
```

## 📈 Indexes และ Performance

### Primary Indexes
- ` nodes.node_id` (Primary Key)
- ` tools.tool_id` (Primary Key)
- ` tool_tags.(tool_id, tag_name)` (Composite Primary Key)
- ` artifacts.artifact_id` (Primary Key)

### Foreign Key Indexes
- ` tools.target_node_id` → ` nodes.node_id`
- ` tool_tags.tool_id` → ` tools.tool_id`
- ` artifacts.created_by_tool_id` → ` tools.tool_id`

### Performance Indexes
- ` nodes.node_type` , ` nodes.status` , ` nodes.created_at`
- ` tools.name` , ` tools.category` , ` tools.status`
- ` tool_tags.tag_name`
- ` artifacts.file_name` , ` artifacts.mime_type` , ` artifacts.created_at`

### JSONB Indexes
- ` tools.input_schema` (GIN)
- ` tools.output_schema` (GIN)

## 🎯 Views ที่มีประโยชน์

### 1. ** active_tools_with_nodes**
แสดง tools ที่ active พร้อมข้อมูล node ที่เกี่ยวข้อง

### 2. ** tools_with_tags**
แสดง tools พร้อม tags ที่เกี่ยวข้อง

### 3. ** artifacts_with_tools**
แสดง artifacts พร้อมข้อมูล tool ที่สร้าง

## 🔧 Functions ที่มีประโยชน์

### 1. ** get_tools_by_tag(tag_search)**
ค้นหา tools ตาม tag

```
SELECT * FROM get_tools_by_tag('analysis');
```

### 2. **get_node_statistics()** แสดงสถิติของ nodes

```
SELECT * FROM get_node_statistics();
```

### 3. **search_tools_by_schema(input_property, output_property)** ค้นหา tools ตาม schema properties

```
SELECT * FROM search_tools_by_schema('file_path');
```

## 🚀 วิธีการใช้งาน

### การติดตั้ง

1. **สร้างฐานข้อมูล PostgreSQL** ```bash
createdb ai_orchestrator
```

2. ** รัน Schema Script** ```bash
psql -d ai_orchestrator -f ai_orchestrator_schema.sql
```

3. ** รัน Queries Script (ถ้าต้องการ)** ```bash
psql -d ai_orchestrator -f ai_orchestrator_queries.sql
```

### การใช้งานพื้นฐาน

#### เพิ่ม Node ใหม่
```
INSERT INTO nodes (node_type, address, status)
VALUES ('TOOL_EXECUTOR', 'http://worker-2:8000', 'ACTIVE');
```

#### เพิ่ม Tool ใหม่
```
INSERT INTO tools (name, description, category, target_node_id, input_schema, output_schema)
VALUES (
    'text_analyzer',
    'Analyze text content and extract insights',
    'ANALYSIS',
    (SELECT node_id FROM nodes WHERE node_type = 'ANALYSIS_NODE' LIMIT 1),
    '{"type": "object", "properties": {"text": {"type": "string"}}}',
    '{"type": "object", "properties": {"sentiment": {"type": "string"}, "keywords": {"type": "array"}}}'
);
```

#### เพิ่ม Tag ให้ Tool
```
INSERT INTO tool_tags (tool_id, tag_name)
VALUES (
    (SELECT tool_id FROM tools WHERE name = 'text_analyzer'),
    'nlp'
);
```

#### บันทึก Artifact
```
INSERT INTO artifacts (file_name, mime_type, storage_pointer, size_bytes, created_by_tool_id)
VALUES (
    'analysis_result.json',
    'application/json',
    's3://bucket/results/analysis_result.json',
    2048,
    (SELECT tool_id FROM tools WHERE name = 'text_analyzer')
);
```

## 🔍 Queries ที่ใช้บ่อย

### 1. ** หา Tools ที่ Active พร้อม Node** ```sql
SELECT t.name, t.category, n.node_type, n.address
FROM tools t
LEFT JOIN nodes n ON t.target_node_id = n.node_id
WHERE t.status = 'ENABLED';
```

### 2. ** หา Tools ตาม Category** ```sql
SELECT name, description, version
FROM tools
WHERE category = 'ANALYSIS' AND status = 'ENABLED';
```

### 3. ** หา Tools ตาม Tag** ```sql
SELECT t.name, t.description
FROM tools t
JOIN tool_tags tt ON t.tool_id = tt.tool_id
WHERE tt.tag_name = 'analysis';
```

### 4. ** ดูสถิติการใช้งาน Tools** ```sql
SELECT
    t.name,
    COUNT(a.artifact_id) as usage_count,
    SUM(a.size_bytes) as total_output_size
FROM tools t
LEFT JOIN artifacts a ON t.tool_id = a.created_by_tool_id
GROUP BY t.tool_id, t.name
ORDER BY usage_count DESC;
```

## 🛠 ️ การบำรุงรักษา

### Health Check Queries
```
- - ตรวจสอบ data integrity
SELECT 'Tools without nodes' as issue, COUNT(* ) as count
FROM tools
WHERE target_node_id IS NULL AND status = 'ENABLED'
UNION ALL
SELECT 'Orphaned artifacts' as issue, COUNT(* ) as count
FROM artifacts a
LEFT JOIN tools t ON a.created_by_tool_id = t.tool_id
WHERE t.tool_id IS NULL;
```

### Cleanup Queries
```
- - ลบ orphaned artifacts
DELETE FROM artifacts
WHERE created_by_tool_id IS NULL
OR created_by_tool_id NOT IN (SELECT tool_id FROM tools);

- - อัปเดต tool status ตาม node status
UPDATE tools
SET status = 'DISABLED'
WHERE target_node_id IN (
    SELECT node_id FROM nodes WHERE status IN ('INACTIVE', 'MAINTENANCE', 'ERROR')
)
AND status = 'ENABLED';
```

## 🔒 ความปลอดภัย

### Permissions
```
- - สร้าง user สำหรับ application
CREATE USER app_user WITH PASSWORD 'secure_password';

- - ให้สิทธิ์ที่จำเป็น
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
```

### Backup Strategy
```
# Backup schema และ data
pg_dump -d ai_orchestrator -f backup_$(date +%Y%m%d_%H%M%S).sql

# Backup เฉพาะ schema
pg_dump -d ai_orchestrator --schema-only -f schema_backup.sql
```

## 📊 Monitoring และ Performance

### Performance Metrics
- **Query Performance**: ใช้ ` EXPLAIN ANALYZE` เพื่อวิเคราะห์
- ** Index Usage**: ตรวจสอบ index usage statistics
- ** Storage Growth**: ติดตามขนาดของ artifacts table
- ** Connection Pool**: ตรวจสอบ connection pool usage

### Monitoring Queries
```
- - ดูขนาดตาราง
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename IN ('nodes', 'tools', 'tool_tags', 'artifacts');

- - ดู index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename IN ('nodes', 'tools', 'tool_tags', 'artifacts');
```

## 🎯 Best Practices

### 1. ** การออกแบบ Schema** - ใช้ UUID สำหรับ Primary Keys เพื่อความปลอดภัย
- ใช้ JSONB สำหรับ schema ที่ยืดหยุ่น
- ตั้งค่า constraints ที่เหมาะสม

### 2. ** Performance** - สร้าง indexes สำหรับ columns ที่ใช้ค้นหาบ่อย
- ใช้ GIN indexes สำหรับ JSONB columns
- ตรวจสอบ query performance อย่างสม่ำเสมอ

### 3. ** Maintenance** - ทำ cleanup ข้อมูลเก่าอย่างสม่ำเสมอ
- ตรวจสอบ data integrity
- backup ข้อมูลเป็นประจำ

### 4. ** Security** - ใช้ prepared statements
- ตรวจสอบ input validation
- จำกัดสิทธิ์การเข้าถึง

- --

* * สร้างโดย**: Orion Senior Dev
* * วันที่**: 21 สิงหาคม 2025
* * เวอร์ชัน**: 1.0.0

