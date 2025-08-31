# Chonost Development Roadmap - Advanced Features Integration

## ภาพรวมโครงการ

Chonost - แพลตฟอร์มเขียนหนังสืออัจฉริยะที่ผสาน AI เข้ากับเครื่องมือสร้างสรรค์

## Phase 1: Foundation & Core Infrastructure (เดือนที่ 1-2)

### 1.1 Project Setup & Basic Architecture

- [x] สร้าง Monorepo structure

- [x] ตั้งค่า FastAPI Backend

- [x] ตั้งค่า React Frontend

- [x] ตั้งค่า Database (PostgreSQL)

- [x] ตั้งค่า Docker environment

### 1.2 Core Editor Implementation

- [x] Basic Markdown Editor

- [x] File Management System

- [x] Project Structure

- [x] Basic UI Components

### 1.3 Basic AI Integration

- [x] Azure LLM Integration (GPT-4.1-mini, Llama-4-Scout, Phi-4-multimodal)

- [x] Enhanced AI Agents System

- [x] Dataset Management

- [x] Feedback Loop System

## Phase 2: Advanced AI & Background Services (เดือนที่ 3-4)

### 2.1 The Project Manifest System ("The All-Seeing Eye")

**เป้าหมาย:** สร้างดัชนีอัตโนมัติของทุกไฟล์และ Entity ในโปรเจกต์

#### 2.1.1 File System Watcher

```python
# ใช้ watchdog สำหรับตรวจจับการเปลี่ยนแปลงไฟล์
# ใช้ dramatiq + redis สำหรับ background job queue
```

- [x] ติดตั้ง `watchdog`, `dramatiq`, `redis`

- [x] สร้าง FileSystemEventHandler

- [x] สร้าง Background Worker สำหรับ Indexing

- [ ] ทดสอบการทำงานของ File Watcher

#### 2.1.2 Entity Extraction & Indexing

```python
# ใช้ transformers + torch สำหรับ Local NER Model
# ใช้ sentence-transformers สำหรับ Embeddings
```

- [x] ติดตั้ง `transformers`, `torch`, `sentence-transformers`

- [x] สร้าง NER Pipeline (`dslim/bert-base-NER`)

- [x] สร้าง Embedding Service (`all-MiniLM-L6-v2`)

- [ ] สร้าง Manifest JSON Structure

- [ ] ทดสอบ Entity Extraction

#### 2.1.3 Vector Database Integration

```python
# ใช้ Qdrant สำหรับ Vector Database
```

- [x] ติดตั้ง Qdrant

- [x] สร้าง Collection Management

- [x] สร้าง Search Service

- [ ] ทดสอบ Vector Search

### 2.2 The Code Interpreter ("The Forge")

**เป้าหมาย:** รันโค้ด Python, วิเคราะห์ข้อมูล, และสร้างกราฟได้โดยตรง

#### 2.2.1 Docker Kernel Management

```python
# ใช้ docker Python SDK สำหรับจัดการ containers
# ใช้ jupyter_client สำหรับสื่อสารกับ kernel
```

- [x] ติดตั้ง `docker`, `jupyter_client`

- [x] สร้าง Custom Jupyter Docker Image

- [x] สร้าง Kernel Manager Service

- [ ] สร้าง Container Lifecycle Management

#### 2.2.2 Code Execution API

```python
# สร้าง API endpoint สำหรับรันโค้ด
# จัดการ stdout, stderr, display_data
```

- [x] สร้าง `/forge/execute` endpoint

- [x] สร้าง Code Execution Service

- [ ] จัดการ Message Types (stdout, stderr, image)

- [ ] ทดสอบ Code Execution

#### 2.2.3 Data Analysis & Visualization

```python
# เพิ่ม pandas, numpy, matplotlib, scikit-learn ใน Docker image
```

- [ ] สร้าง Data Analysis Templates

- [ ] สร้าง Visualization Service

- [ ] ทดสอบ Data Analysis Features

### 2.3 Dataset Management System
**เป้าหมาย:** จัดการข้อมูลสำหรับ feedback loop และงานเฉพาะทาง

#### 2.3.1 Feedback Loop Datasets

- [ ] สร้าง SQLite Database Schema

- [ ] สร้าง Error Context Storage

- [ ] สร้าง User Preference Learning

- [ ] สร้าง Block Text Data Management

#### 2.3.2 Specialized Task Datasets

- [ ] สร้าง Creative Writing Datasets

- [ ] สร้าง Technical Documentation Datasets

- [ ] สร้าง Code Generation Datasets

- [ ] สร้าง Dataset Versioning System

#### 2.3.3 Dataset Export/Import

- [ ] สร้าง JSON Export Functionality

- [ ] สร้าง CSV Export Functionality

- [ ] สร้าง Dataset Backup System

- [ ] ทดสอบ Dataset Operations

## Phase 3: Advanced UI & User Experience

### 3.1 Dynamic View Switching (Editor ↔ Whiteboard)

**เป้าหมาย:** แปลง Markdown เป็น Whiteboard และแปลงกลับได้

#### 3.1.1 Excalidraw Integration

```javascript
// ใช้ @excalidraw/excalidraw สำหรับ Whiteboard
```

- [x] ติดตั้ง `@excalidraw/excalidraw`

- [ ] สร้าง Whiteboard Component

- [ ] สร้าง View Switching Logic

- [ ] ทดสอบ Whiteboard Features

#### 3.1.2 Markdown to Canvas Conversion

```python
# ใช้ litellm + Claude 3.5 Sonnet สำหรับแปลง Markdown เป็น Excalidraw JSON
```

- [ ] สร้าง `/transform/md-to-canvas` endpoint

- [ ] สร้าง Markdown Parser

- [ ] สร้าง Canvas to Markdown Converter

- [ ] ทดสอบ Conversion

### 3.2 Proactive Knowledge Suggestions

**เป้าหมาย:** สกัด "แก่นความรู้" และเสนอให้ผู้ใช้บันทึก

#### 3.2.1 Knowledge Extraction Service

```python
# ใช้ litellm สำหรับสกัดความรู้จากข้อความ
```

- [ ] สร้าง `/ai/suggest-knowledge` endpoint

- [ ] สร้าง Knowledge Extraction Logic

- [ ] สร้าง Knowledge Storage System

- [ ] ทดสอบ Knowledge Suggestions

#### 3.2.2 UI Integration

```javascript
// สร้าง UI สำหรับแสดง Knowledge Suggestions
```

- [ ] สร้าง Knowledge Suggestion Component

- [ ] สร้าง Knowledge Management UI

- [ ] ทดสอบ UI Integration

### 3.3 The Living Dictionary & Doc Reference

**เป้าหมาย:** สร้างสารานุกรมส่วนตัวและคุยกับเอกสารได้

#### 3.3.1 RAG Service Implementation

```python
# ใช้ qdrant-client + sentence-transformers สำหรับ RAG
```

- [ ] สร้าง RAG Service

- [ ] สร้าง Context Search Function

- [ ] สร้าง Answer Generation Service

- [ ] ทดสอบ RAG Features

#### 3.3.2 Dictionary UI

```javascript
// สร้าง UI สำหรับ Living Dictionary
```

- [ ] สร้าง Dictionary Component

- [ ] สร้าง Search Interface

- [ ] สร้าง Chat Interface

- [ ] ทดสอบ Dictionary Features

### 3.4 The Trinity Layout - หัวใจของ UX

**เป้าหมาย:** สร้าง Layout 3 ส่วนหลักที่เป็นหัวใจของประสบการณ์ทั้งหมด

#### 3.4.1 Left Sidebar (File & Knowledge Explorer)

- [ ] สร้าง FileTree Component

- [ ] สร้าง GlobalDashboard Component

- [ ] สร้าง Tab Switching Logic

- [ ] สร้าง Craft-style Thumbnails

#### 3.4.2 Right Sidebar (Tools & Information)

- [ ] สร้าง ChatPanel Component

- [ ] สร้าง StatusDashboard Component

- [ ] สร้าง PropertiesPanel Component

- [ ] สร้าง OutlinePanel Component

#### 3.4.3 MainContent (Editor & Whiteboard)

- [ ] สร้าง EditorView Component

- [ ] สร้าง WhiteboardView Component

- [ ] สร้าง View Switching Logic

- [ ] สร้าง State Management

### 3.5 The Dual Palettes (เครื่องมือคู่ใจ)

**เป้าหมาย:** สร้างเครื่องมือที่ยืดหยุ่นและใช้งานง่าย

#### 3.5.1 Left Palette (Contextual Info)

- [ ] สร้าง Backlinks Display

- [ ] สร้าง Outline Generator

- [ ] สร้าง Entity Detection

- [ ] สร้าง Contextual Tools

#### 3.5.2 Right Palette (Global Tools)

- [ ] สร้าง Project-wide Search

- [ ] สร้าง Assistant Chat

- [ ] สร้าง Knowledge Graph

- [ ] สร้าง Global Settings

## Phase 4: Advanced Automation & Integration

### 4.1 Editor Integration (VS Code API)

**เป้าหมาย:** เชื่อมต่อกับ VS Code API

#### 4.1.1 VS Code Extension Development

```typescript
// สร้าง VS Code Extension
```

- [ ] สร้าง VS Code Extension Project

- [ ] สร้าง API Integration

- [ ] สร้าง Command Palette Integration

- [ ] ทดสอบ VS Code Integration

#### 4.1.2 Cursor & Selection Management

- [ ] สร้าง Cursor Position Tracking

- [ ] สร้าง Text Selection Management

- [ ] สร้าง Content Insertion/Replacement

- [ ] สร้าง Auto Code Formatting

### 4.2 Keyboard & Mouse Automation

**เป้าหมาย:** ควบคุม keyboard และ mouse events

#### 4.2.1 Keyboard Automation Service

```python
# ใช้ pyautogui หรือ pynput สำหรับ automation
```

- [ ] ติดตั้ง automation libraries

- [ ] สร้าง Keyboard Event Control

- [ ] สร้าง Shortcut Sending

- [ ] สร้าง Auto Text Typing

#### 4.2.2 Mouse Automation Service

- [ ] สร้าง Mouse Click Control

- [ ] สร้าง Mouse Movement Control

- [ ] สร้าง Automation Sequence Recording

- [ ] สร้าง Automation Sequence Playback

#### 4.2.3 Cross-Platform Support

- [ ] รองรับ Windows

- [ ] รองรับ MacOS

- [ ] รองรับ Linux

- [ ] ทดสอบ Cross-Platform Compatibility

### 4.3 Context Awareness

**เป้าหมาย:** วิเคราะห์โค้ดและโครงสร้างโปรเจกต์

#### 4.3.1 Code Analysis Service

```python
# ใช้ ast หรือ tree-sitter สำหรับ code analysis
```

- [ ] ติดตั้ง code analysis libraries

- [ ] สร้าง Code Parser

- [ ] สร้าง Pattern Detection

- [ ] สร้าง Design Pattern Recognition

#### 4.3.2 Programming Language Context

- [ ] สร้าง Language Detection

- [ ] สร้าง Syntax Analysis

- [ ] สร้าง Context Caching

- [ ] สร้าง Performance Optimization

### 4.4 Intelligent Actions

**เป้าหมาย:** แปลงคำสั่งธรรมชาติเป็น actions

#### 4.4.1 Natural Language Processing

```python
# ใช้ LLM สำหรับแปลงคำสั่งธรรมชาติ
```

- [ ] สร้าง Command Parser

- [ ] สร้าง Action Mapping

- [ ] สร้าง Template Generator

- [ ] สร้าง Function/Class Templates

#### 4.4.2 Auto Code Refactoring

- [ ] สร้าง Code Refactoring Logic

- [ ] สร้าง Pattern Matching

- [ ] สร้าง Code Quality Analysis

- [ ] ทดสอบ Intelligent Actions

## Phase 5: AI Model Integration & Optimization

### 5.1 Azure LLM Integration

**เป้าหมาย:** เชื่อมต่อกับ Azure LLM services

#### 5.1.1 GPT-4.1-mini Integration

- [ ] สร้าง Azure OpenAI Client

- [ ] สร้าง Model Configuration

- [ ] สร้าง Cost Management

- [ ] ทดสอบ GPT-4.1-mini

#### 5.1.2 Llama-4-Scout Integration

- [ ] สร้าง Llama-4-Scout Client

- [ ] สร้าง Model Configuration

- [ ] สร้าง Performance Optimization

- [ ] ทดสอบ Llama-4-Scout

#### 5.1.3 Phi-4-multimodal Integration

- [ ] สร้าง Phi-4-multimodal Client

- [ ] สร้าง Multimodal Processing

- [ ] สร้าง Image-Text Integration

- [ ] ทดสอบ Phi-4-multimodal

### 5.2 Local Model Management

**เป้าหมาย:** จัดการโมเดล local อย่างมีประสิทธิภาพ

#### 5.2.1 Phi-4-mini Local Integration

- [ ] สร้าง Local Model Loader

- [ ] สร้าง Model Caching

- [ ] สร้าง Memory Management

- [ ] ทดสอบ Phi-4-mini

#### 5.2.2 Llama 3.1/3.2 8B Integration

- [ ] สร้าง Llama Model Loader

- [ ] สร้าง Quantization Support

- [ ] สร้าง Performance Optimization

- [ ] ทดสอบ Llama Models

### 5.3 Model Routing & Selection

**เป้าหมาย:** เลือกโมเดลที่เหมาะสมสำหรับแต่ละงาน

#### 5.3.1 Router AI Implementation

- [ ] สร้าง Model Selection Logic

- [ ] สร้าง Cost-Benefit Analysis

- [ ] สร้าง Performance Monitoring

- [ ] ทดสอบ Model Routing

#### 5.3.2 Fallback Mechanisms

- [ ] สร้าง Primary Model Fallback

- [ ] สร้าง Secondary Model Fallback

- [ ] สร้าง Offline Mode Support

- [ ] ทดสอบ Fallback Scenarios

## Phase 6: Testing & Deployment

### 6.1 Comprehensive Testing

#### 6.1.1 AI Gauntlet Testing

**เป้าหมาย:** ทดสอบ AI models ในสถานการณ์ต่างๆ

##### สนามที่ 1: The Router's Crossroads (ทดสอบ Phi-4-mini)

- [ ] ทดสอบ Simple QA

- [ ] ทดสอบ Tool Use

- [ ] ทดสอบ Complex Reasoning

- [ ] ทดสอบ Creative Writing

- [ ] ทดสอบ Ambiguous Requests

##### สนามที่ 2: The Local's Arena (ทดสอบ Llama 3.1/3.2-8B)

- [ ] ทดสอบ Summarization

- [ ] ทดสอบ Fact Extraction

- [ ] ทดสอบ Inline Completion

- [ ] ทดสอบ Error Handling

##### สนามที่ 3: The Analyst's Gauntlet (ทดสอบ Claude 3.5 Sonnet)

- [ ] ทดสอบ Dynamic View Switching

- [ ] ทดสอบ Proactive Analysis

- [ ] ทดสอบ Complex RAG & Reasoning

- [ ] ทดสอบ Meta-Programming

##### สนามที่ 4: The Specialist's Corner (ทดสอบโมเดลเฉพาะทาง)

- [ ] ทดสอบ Long Context QA (Kimi K2)

- [ ] ทดสอบ Multilingual Performance (Qwen)

- [ ] ทดสอบ Cost-Effective Reasoning (GPT-OSS-20B)

#### 6.1.2 User Journey Testing

**เป้าหมาย:** ทดสอบประสบการณ์ผู้ใช้ในสถานการณ์จริง

##### ผู้ใช้คนที่ 1: The Novelist (นักเขียนนิยาย)

- [ ] ทดสอบ Quick Start Template

- [ ] ทดสอบ Character Creation

- [ ] ทดสอบ Outlining Process

- [ ] ทดสอบ Drafting Process

- [ ] ทดสอบ Revision Process

- [ ] ทดสอบ Finalization

##### ผู้ใช้คนที่ 2: The Researcher (นักวิจัย)

- [ ] ทดสอบ Data Ingestion

- [ ] ทดสอบ Knowledge Synthesis

- [ ] ทดสอบ Literature Review

- [ ] ทดสอบ Citation Management

- [ ] ทดสอบ Drafting Process

##### ผู้ใช้คนที่ 3: The World-Builder (นักสร้างโลก)

- [ ] ทดสอบ Map Making

- [ ] ทดสอบ History & Lore

- [ ] ทดสอบ Magic System

- [ ] ทดสอบ Relationship Mapping

- [ ] ทดสอบ Consistency Check

#### 6.1.3 Stress Testing

**เป้าหมาย:** ทดสอบระบบภายใต้สภาวะกดดัน

##### UX Stress Test 1: "The Tab Hoarder"

- [ ] ทดสอบ Multiple Document Tabs

- [ ] ทดสอบ Multiple Whiteboard Tabs

- [ ] ทดสอบ Chat Panel Performance

- [ ] ทดสอบ Memory Usage

- [ ] ทดสอบ Memory Leak Detection

##### UX Stress Test 2: "The Impatient User"

- [ ] ทดสอบ Rapid View Switching

- [ ] ทดสอบ Multiple AI Requests

- [ ] ทดสอบ Task Queue Management

- [ ] ทดสอบ Loading State Management

- [ ] ทดสอบ Error State Management

### 6.2 Performance & Optimization

- [ ] Optimize Database Queries

- [ ] Implement Caching Strategy

- [ ] Optimize AI Model Loading

- [ ] Performance Testing

### 6.3 Security & Reliability

- [ ] Implement Security Measures

- [ ] Add Error Handling

- [ ] Create Backup Systems

- [ ] Security Testing

### 6.4 Deployment Preparation

- [ ] Docker Configuration

- [ ] CI/CD Pipeline

- [ ] Production Environment Setup

- [ ] Monitoring & Logging

## Phase 7: Chonost-MCP Platform Integration

### 7.1 MCP Platform Coordination

**เป้าหมาย:** ประสานงานกับ Chonost-MCP Platform เพื่อหลีกเลี่ยงการซ้ำซ้อน

#### 7.1.1 Shared Infrastructure

- [ ] **Shared Redis Instance:** ใช้ Redis เดียวกันสำหรับทั้งสอง platform
- [ ] **Shared Qdrant Instance:** ใช้ Qdrant เดียวกันสำหรับ vector storage
- [ ] **Shared Docker Registry:** ใช้ Docker images ร่วมกัน
- [ ] **Shared Configuration:** ใช้ environment variables ร่วมกัน

#### 7.1.2 API Integration

- [ ] **MCP Tool Integration:** เชื่อมต่อกับ MCP tools จาก Chonost-MCP
- [ ] **Shared AI Services:** ใช้ AI services ร่วมกัน
- [ ] **File Management Sync:** ซิงค์ file management ระหว่าง platforms
- [ ] **RAG System Integration:** ใช้ RAG system ร่วมกัน

#### 7.1.3 Development Coordination

- [ ] **Shared Testing Framework:** ใช้ testing framework ร่วมกัน
- [ ] **Shared Documentation:** สร้าง documentation ร่วมกัน
- [ ] **Shared CI/CD Pipeline:** ใช้ deployment pipeline ร่วมกัน
- [ ] **Shared Monitoring:** ใช้ monitoring system ร่วมกัน

### 7.2 Platform-Specific Features

#### 7.2.1 Chonost-App Specific (Tauri + Sidecar)

- [ ] **Desktop UI Components:** The Trinity Layout, Editor/Whiteboard
- [ ] **Tauri Integration:** Desktop app features
- [ ] **User Experience:** Creative writing workflow
- [ ] **Local Processing:** Offline capabilities

#### 7.2.2 Chonost-MCP Specific (Extensible Platform)

- [ ] **MCP Server:** WebSocket server for external tools
- [ ] **Tool Registry:** Dynamic tool loading system
- [ ] **API-First Design:** RESTful and WebSocket APIs
- [ ] **External Integration:** Third-party tool support

### 7.3 Cross-Platform Communication

#### 7.3.1 Inter-Platform APIs

- [ ] **Chonost-App → Chonost-MCP:** เรียกใช้ MCP tools
- [ ] **Chonost-MCP → Chonost-App:** ส่งข้อมูลกลับไปยัง desktop app
- [ ] **Shared Event System:** Real-time event synchronization
- [ ] **Data Synchronization:** Sync data between platforms

#### 7.3.2 Unified User Experience

- [ ] **Seamless Integration:** ผู้ใช้ไม่รู้สึกว่ามีสอง platform
- [ ] **Shared Authentication:** ใช้ authentication system เดียวกัน
- [ ] **Unified Settings:** ตั้งค่าหนึ่งครั้งใช้ได้ทั้งสอง platform
- [ ] **Cross-Platform Data:** ข้อมูลซิงค์ระหว่าง platforms

## เทคโนโลยีที่ใช้

### Backend Technologies

- **FastAPI**: Web framework

- **PostgreSQL**: Database

- **Redis**: Caching & Job Queue

- **Qdrant**: Vector Database

- **Docker**: Containerization

- **Dramatiq**: Background Tasks

### AI/ML Libraries

- **Transformers**: NLP models

- **Torch**: Deep learning

- **Sentence-Transformers**: Embeddings

- **LiteLLM**: LLM integration

- **Jupyter Client**: Code execution

### Frontend Technologies

- **React**: UI framework

- **TypeScript**: Type safety

- **Tailwind CSS**: Styling

- **Excalidraw**: Whiteboard

- **Alpine.js**: Interactivity

### Development Tools

- **Docker**: Containerization

- **Git**: Version control

- **ESLint**: Code linting

- **Prettier**: Code formatting

- **Jest**: Testing

## การประเมินความคืบหน้า

### Metrics ที่ใช้

- **Feature Completion**: จำนวนฟีเจอร์ที่เสร็จสิ้น

- **Code Coverage**: ความครอบคลุมของ test

- **Performance**: Response time และ throughput

- **User Experience**: Usability testing results

### Milestones

- **Month 2**: Foundation complete

- **Month 4**: Advanced AI features complete

- **Month 6**: UI/UX features complete

- **Month 8**: Automation features complete

- **Month 10**: Optimization complete

- **Month 12**: Production ready

## ความเสี่ยงและแผนรอง

### ความเสี่ยงหลัก

1.  **AI Model Performance**: อาจต้องปรับโมเดลหรือใช้ cloud services

1.  **Complexity Management**: อาจต้องแบ่งฟีเจอร์ออกเป็น phases ย่อย

1.  **Performance Issues**: อาจต้อง optimize หรือ scale infrastructure

### แผนรอง

1.  **Fallback to Cloud AI**: หาก local models ไม่เพียงพอ

1.  **Feature Prioritization**: หากต้องลดฟีเจอร์บางส่วน

1.  **Infrastructure Scaling**: หากต้องเพิ่ม resources

## สรุป

แผนการพัฒนานี้ครอบคลุมฟีเจอร์ขั้นสูงทั้งหมดที่ระบุในเอกสาร โดยแบ่งเป็น 6 phases ที่ชัดเจน แต่ละ phase มีเป้าหมายและ deliverables ที่วัดผลได้ การใช้เทคโนโลยีที่ทันสมัยและมีชุมชนผู้ใช้ขนาดใหญ่จะช่วยให้การพัฒนามีประสิทธิภาพและสามารถหาความช่วยเหลือได้ง่ายเมื่อเกิดปัญหา

