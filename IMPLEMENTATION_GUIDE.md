
## การติดตั้งและใช้งานฟีเจอร์ขั้นสูง

### 1. The Project Manifest System ("The All-Seeing Eye")

#### การติดตั้ง Dependencies

```bash
# Backend dependencies
pip install watchdog dramatiq redis transformers torch sentence-transformers

# หรือใช้ requirements.txt
pip install -r requirements.txt
```

#### การตั้งค่า Redis

```bash
# ติดตั้ง Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# หรือใช้ Docker
docker run -d -p 6379:6379 redis:alpine

# เริ่มต้น Redis service
sudo systemctl start redis-server
```

#### การตั้งค่า File Watcher

```python
# file: services/file_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import dramatiq
from dramatiq.brokers.redis import RedisBroker

# ตั้งค่า Redis broker
broker = RedisBroker(host="localhost", port=6379)
dramatiq.set_broker(broker)

class ProjectEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.txt')):
            # ส่งงานเข้าคิว
            process_file_change.send(event.src_path)

def start_watcher(project_path: str):
    observer = Observer()
    observer.schedule(ProjectEventHandler(), project_path, recursive=True)
    observer.start()
    return observer
```

#### การใช้งาน

```python
# เริ่มต้น file watcher
observer = start_watcher("/path/to/your/project")
print("File watcher started...")

# หยุด file watcher
observer.stop()
observer.join()
```

### 2. The Code Interpreter ("The Forge")

#### การสร้าง Docker Image

```dockerfile
# Dockerfile สำหรับ Jupyter Kernel
FROM jupyter/minimal-notebook:latest

USER root

# ติดตั้ง dependencies สำหรับ data analysis
RUN pip install pandas numpy matplotlib scikit-learn jupyter-kernel-gateway

# สร้าง user สำหรับ kernel
RUN useradd -m -s /bin/bash kernel_user
USER kernel_user

# เปิด kernel gateway
EXPOSE 8888
CMD ["jupyter", "kernelgateway", "--KernelGatewayApp.ip=0.0.0.0", "--KernelGatewayApp.port=8888"]
```

#### การสร้าง Docker Image

```bash
# Build Docker image
docker build -t chonost-kernel:latest .

# หรือใช้ pre-built image
docker pull chonost-kernel:latest
```

#### การใช้งาน Code Interpreter
