# 🐳 Docker Universal File System MCP Server

## 📋 ภาพรวม

Docker setup สำหรับ Universal File System MCP Server ที่แก้ปัญหาความแตกต่างของ user และ environment ได้อย่างสมบูรณ์

## 🚀 การใช้งานด่วน

### 1. สร้าง Docker Image
```
.\scripts\start-docker.ps1 -Action build
```

### 2. เริ่มต้น Container (Development Mode)
```
.\scripts\start-docker.ps1 -Action start
```

### 3. เริ่มต้น Container (Production Mode)
```
.\scripts\start-docker.ps1 -Action start -Mode prod
```

### 4. ดู Logs
```
.\scripts\start-docker.ps1 -Action logs
```

### 5. หยุด Container
```
.\scripts\start-docker.ps1 -Action stop
```

## 🛠 ️ คำสั่ง Docker โดยตรง

### สร้าง Image
```
docker build -t universal-fs-mcp:latest .
```

### เริ่มต้น Container
```
# Development mode (with logs)
docker-compose up --build

# Production mode (background)
docker-compose up -d --build
```

### จัดการ Container
```
# ดูสถานะ
docker-compose ps

# ดู logs
docker-compose logs -f universal-mcp-server

# หยุด
docker-compose down

# รีสตาร์ท
docker-compose restart
```

### เข้าไปใน Container
```
docker exec -it universal-fs-mcp-server /bin/bash
```

## 📁 โครงสร้าง Docker

```
FileSystemMCP/
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Container orchestration
├── .dockerignore             # Files to exclude from image
├── scripts/
│   └── start-docker.ps1      # Docker management script
└── DOCKER_README.md          # This file
```

## 🔧 การตั้งค่า

### Environment Variables
```
environment:
  - PYTHONPATH=/app
  - PYTHONUNBUFFERED=1
  - MCP_SERVER_MODE=production
  - LOG_LEVEL=INFO
```

### Volume Mounts
```
volumes:
  - ./data:/data              # Persistent data
  - ./logs:/logs              # Log files
  - ./datasets:/app/datasets  # Configuration
  - /:/host:ro                # Host file system (read-only)
  - ./config:/app/config      # Custom config
```

### Resource Limits
```
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

## 🌐 Network Configuration

### Port Mapping
- **8000**: HTTP API (if enabled)
- ** Internal**: MCP Server communication

### Network Isolation
```
networks:
  mcp-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🔒 Security Features

### User Isolation
```
user: "1000:1000"  # Non-root user
```

### Security Options
```
security_opt:
  - no-new-privileges:true
```

### Read-only Host Access
```
volumes:
  - /:/host:ro  # Read-only access to host
```

## 📊 Monitoring & Health Checks

### Health Check
```
healthcheck:
  test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Resource Monitoring
```
# ดู resource usage
docker stats universal-fs-mcp-server

# ดู container status
docker-compose ps
```

## 🧹 การบำรุงรักษา

### ทำความสะอาด Resources
```
.\scripts\start-docker.ps1 -Action clean
```

### อัปเดต Image
```
# Rebuild image
docker build -t universal-fs-mcp:latest .

# Update containers
docker-compose up -d --build
```

### Backup Data
```
# Backup data volume
docker run --rm -v universal-fs-mcp_data:/data -v $(pwd):/backup alpine tar czf /backup/mcp-data-backup.tar.gz -C /data .

# Restore data
docker run --rm -v universal-fs-mcp_data:/data -v $(pwd):/backup alpine tar xzf /backup/mcp-data-backup.tar.gz -C /data
```

## 🔍 Troubleshooting

### ปัญหาที่พบบ่อย

#### 1. Permission Denied
```
# ตรวจสอบ user permissions
docker exec -it universal-fs-mcp-server id

# แก้ไข permissions
chmod -R 755 ./data
```

#### 2. Port Already in Use
```
# ตรวจสอบ port usage
 netstat -tulpn | grep :8000

# เปลี่ยน port ใน docker-compose.yml
ports:
  - "8001:8000"  # เปลี่ยนจาก 8000 เป็น 8001
```

#### 3. Out of Memory
```
# เพิ่ม memory limit
deploy:
  resources:
    limits:
      memory: 4G  # เพิ่มจาก 2G เป็น 4G
```

#### 4. Container Won't Start
```
# ดู detailed logs
docker-compose logs universal-mcp-server

# ตรวจสอบ image
 docker images | grep universal-fs-mcp

# Rebuild image
docker build --no-cache -t universal-fs-mcp:latest .
```

## 🎯 ประโยชน์ของ Docker

### ✅ แก้ปัญหาความแตกต่างของ User
- ** Consistent Environment**: ทุก user ได้ environment เดียวกัน
- ** No Python Path Issues**: ไม่มีปัญหา Python path
- ** Isolated Dependencies**: Dependencies แยกจากระบบ

### ✅ Cross-Platform Compatibility
- ** Windows**: Docker Desktop
- ** macOS**: Docker Desktop
- ** Linux**: Docker Engine

### ✅ Resource Management
- ** Memory Limits**: ควบคุมการใช้ memory
- ** CPU Limits**: ควบคุมการใช้ CPU
- ** Disk Space**: ควบคุมการใช้ disk

### ✅ Security
- ** User Isolation**: ทำงานด้วย non-root user
- ** Network Isolation**: แยก network
- ** Read-only Access**: เข้าถึง host แบบ read-only

### ✅ Scalability
- ** Easy Deployment**: deploy ง่าย
- ** Version Control**: ควบคุมเวอร์ชัน
- ** Rollback**: ย้อนกลับได้ง่าย

## 🚀 ขั้นตอนต่อไป

1. ** Build และ Test**: สร้าง image และทดสอบ
2. ** Configure Volumes**: ตั้งค่า volume mounts
3. ** Set Permissions**: ตั้งค่า permissions
4. ** Monitor**: ตรวจสอบการทำงาน
5. ** Optimize**: ปรับแต่งประสิทธิภาพ

- --

* * 🎉 Docker setup พร้อมใช้งานแล้ว!**

ใช้ ` .\scripts\start-docker.ps1 -Action build` เพื่อเริ่มต้นครับ 🚀

