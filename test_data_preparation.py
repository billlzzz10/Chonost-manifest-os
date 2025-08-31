"""
Test Data Preparation for Chonost Desktop App
เตรียมข้อมูลทดสอบที่ครบถ้วนสำหรับการทดสอบระบบ
"""

import requests
import json
import time

class TestDataPreparation:
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        self.test_documents = []
        
    def prepare_test_documents(self):
        """เตรียมเอกสารทดสอบที่ครอบคลุมทุกฟีเจอร์"""
        
        documents = [
            {
                "file_path": "DEVELOPMENT_ROADMAP.md",
                "content": """
# Chonost Development Roadmap - Advanced Features Integration

## Phase 1: Foundation & Core Infrastructure ✅
- [x] Project Structure Setup
- [x] Tauri + React Integration
- [x] Basic UI Components
- [x] Database Schema Design
- [x] API Endpoints Structure

## Phase 2: Advanced AI & Background Services
### Phase 2.1: The Project Manifest System ("The All-Seeing Eye")
- [x] File Watcher & Indexing System
- [x] Entity Extraction & Classification
- [x] Vector Search Implementation
- [x] Real-time File Monitoring

### Phase 2.2: The Code Interpreter ("The Forge")
- [x] Jupyter Kernel Integration
- [x] Docker Container Management
- [x] Code Execution Engine
- [x] Data Visualization Service

### Phase 2.3: Dataset Management System
- [ ] Multi-format Document Support
- [ ] Automatic Metadata Extraction
- [ ] Version Control Integration
- [ ] Collaborative Editing Features

## Phase 3: Advanced UI & User Experience
### Phase 3.1: The Trinity Layout Implementation
- [x] Three-Panel Layout Design
- [x] Responsive Sidebar Components
- [x] Dynamic Content Switching
- [x] Customizable Workspace Layout

### Phase 3.2: Editor & Whiteboard Integration
- [x] Markdown Editor with Preview
- [x] Excalidraw Whiteboard Integration
- [x] Real-time Collaboration Tools
- [x] Multi-format Export Options

### Phase 3.3: Knowledge Explorer
- [x] Document Tree Navigation
- [x] Advanced Search & Filtering
- [x] Tag-based Organization
- [x] Quick Access Bookmarks

### Phase 3.4: Assistant Panel
- [x] AI Chat Interface
- [x] Context-aware Suggestions
- [x] Code Generation Tools
- [x] Documentation Assistant

## Phase 4: Advanced Automation & Integration
### Phase 4.1: AI Agent System
- [ ] Multi-agent Architecture
- [ ] Task Delegation & Coordination
- [ ] Learning & Adaptation
- [ ] Performance Optimization

### Phase 4.2: Workflow Automation
- [ ] Custom Workflow Builder
- [ ] Trigger-based Actions
- [ ] Integration with External Tools
- [ ] Analytics & Reporting

## Phase 5: AI Model Integration & Optimization
### Phase 5.1: Model Management
- [ ] Multiple AI Provider Support
- [ ] Model Performance Monitoring
- [ ] Cost Optimization
- [ ] Quality Assurance

### Phase 5.2: Advanced RAG Implementation
- [ ] Multi-modal RAG
- [ ] Context-aware Retrieval
- [ ] Dynamic Knowledge Graph
- [ ] Continuous Learning

## Phase 6: Testing & Deployment
### Phase 6.1: Comprehensive Testing
- [ ] Unit Testing Suite
- [ ] Integration Testing
- [ ] Performance Testing
- [ ] User Acceptance Testing

### Phase 6.2: Deployment & Distribution
- [ ] Automated Build Pipeline
- [ ] Cross-platform Distribution
- [ ] Update Management
- [ ] User Feedback System

## Phase 7: Chonost-MCP Platform Integration
### Phase 7.1: Shared Infrastructure
- [ ] Common Database Schema
- [ ] Shared Authentication
- [ ] Unified Configuration
- [ ] Cross-platform Communication

### Phase 7.2: API Integration
- [ ] RESTful API Standards
- [ ] WebSocket Communication
- [ ] Event-driven Architecture
- [ ] Real-time Synchronization

### Phase 7.3: Development Coordination
- [ ] Shared Development Tools
- [ ] Common Testing Framework
- [ ] Documentation Standards
- [ ] Release Management
                """,
                "title": "Chonost Development Roadmap",
                "type": "markdown"
            },
            {
                "file_path": "THE_TRINITY_LAYOUT.md",
                "content": """
# The Trinity Layout - Core UI Architecture

## Overview
The Trinity Layout is the heart of Chonost's user experience, providing a seamless three-panel interface that adapts to different workflows and user preferences.

## Panel Structure

### 1. Left Sidebar - Knowledge Explorer
**Purpose:** Document navigation, search, and knowledge management

**Features:**
- Document tree with hierarchical organization
- Advanced search with filters and tags
- Quick access bookmarks
- Recent documents list
- File type indicators and metadata

**Technical Implementation:**
- React component with virtual scrolling
- Real-time search with debouncing
- Drag-and-drop file organization
- Context menu with actions

### 2. Main Content Area - Editor/Whiteboard
**Purpose:** Primary workspace for content creation and visualization

**Editor Mode:**
- Rich text editor with Markdown support
- Syntax highlighting for code blocks
- Live preview with split view
- Auto-save functionality
- Version history tracking

**Whiteboard Mode:**
- Excalidraw integration for diagrams
- Free-form drawing tools
- Shape and text insertion
- Export to multiple formats
- Collaborative editing support

**Technical Implementation:**
- Dynamic component switching
- State management with Zustand
- Real-time collaboration via WebSocket
- Plugin architecture for extensions

### 3. Right Sidebar - Assistant Panel
**Purpose:** AI assistance, tools, and contextual help

**Features:**
- AI chat interface with context awareness
- Code generation and explanation
- Documentation lookup
- Task automation suggestions
- Real-time collaboration tools

**Technical Implementation:**
- Chat interface with message history
- Context injection from current document
- Tool integration via MCP protocol
- Real-time response streaming

## Responsive Design
- Collapsible sidebars for mobile devices
- Adaptive layout based on screen size
- Touch-friendly interface elements
- Keyboard shortcuts for power users

## State Management
- Global app state with Zustand
- Persistent user preferences
- Document state synchronization
- Real-time collaboration state

## Performance Optimization
- Lazy loading of components
- Virtual scrolling for large lists
- Debounced search operations
- Efficient re-rendering with React.memo
                """,
                "title": "The Trinity Layout Design",
                "type": "markdown"
            },
            {
                "file_path": "AI_INTEGRATION_GUIDE.md",
                "content": """
# AI Integration Guide - Chonost Platform

## Overview
Chonost integrates multiple AI capabilities to provide intelligent assistance across all aspects of content creation and knowledge management.

## Core AI Components

### 1. RAG (Retrieval-Augmented Generation)
**Purpose:** Context-aware document search and generation

**Implementation:**
- Vector database with sentence transformers
- Semantic search across document corpus
- Context injection for AI responses
- Real-time document indexing

**Features:**
- Multi-modal document support
- Dynamic knowledge graph
- Continuous learning from user interactions
- Cross-document reference linking

### 2. Code Interpreter
**Purpose:** Execute and analyze code within the platform

**Implementation:**
- Jupyter kernel integration
- Docker container management
- Real-time code execution
- Data visualization tools

**Features:**
- Multiple programming language support
- Interactive data analysis
- Chart and graph generation
- Code explanation and optimization

### 3. AI Agents
**Purpose:** Automated task execution and workflow management

**Implementation:**
- Multi-agent architecture
- Task delegation and coordination
- Learning from user patterns
- Performance optimization

**Features:**
- Custom workflow automation
- Intelligent task prioritization
- Context-aware suggestions
- Continuous improvement

## AI Provider Integration

### LiteLLM Support
- Multiple model provider support
- Cost optimization and monitoring
- Quality assurance metrics
- Fallback mechanisms

### Model Management
- Performance monitoring
- Usage analytics
- Cost tracking
- Quality metrics

## User Experience

### Context Awareness
- Document-aware AI responses
- Project-specific knowledge
- User preference learning
- Personalized suggestions

### Real-time Interaction
- Streaming responses
- Interactive code execution
- Live collaboration
- Instant feedback

## Security and Privacy
- Local data processing
- Secure API communication
- User data protection
- Compliance with regulations
                """,
                "title": "AI Integration Guide",
                "type": "markdown"
            },
            {
                "file_path": "FILE_MANAGEMENT_SYSTEM.md",
                "content": """
# File Management System - Chonost Platform

## Overview
The File Management System provides comprehensive document organization, version control, and collaboration features for the Chonost platform.

## Core Features

### 1. Document Organization
**Hierarchical Structure:**
- Folder-based organization
- Tag-based categorization
- Metadata management
- Search and filtering

**Smart Organization:**
- Automatic file type detection
- Content-based categorization
- Duplicate detection
- Reference linking

### 2. Version Control
**Document History:**
- Automatic version tracking
- Change comparison tools
- Rollback capabilities
- Branch management

**Collaboration:**
- Real-time editing
- Conflict resolution
- Comment and review system
- Approval workflows

### 3. Search and Discovery
**Advanced Search:**
- Full-text search across documents
- Semantic search with AI
- Filter by metadata
- Saved search queries

**Discovery Features:**
- Related document suggestions
- Popular content highlighting
- Recent activity tracking
- Personalized recommendations

## Technical Implementation

### Database Schema
- Document metadata storage
- Version history tracking
- User permissions management
- Search index optimization

### File Processing
- Multi-format document support
- Automatic metadata extraction
- Content indexing
- Thumbnail generation

### Security
- User authentication
- Permission-based access
- Data encryption
- Audit logging

## Integration Points

### The All-Seeing Eye
- Real-time file monitoring
- Automatic indexing
- Change detection
- Notification system

### AI Integration
- Content analysis
- Automatic tagging
- Smart categorization
- Quality assessment

### Collaboration Tools
- Real-time editing
- Comment system
- Review workflows
- Sharing controls
                """,
                "title": "File Management System",
                "type": "markdown"
            },
            {
                "file_path": "PERFORMANCE_TESTING.md",
                "content": """
# Performance Testing - Chonost Platform

## Testing Objectives
- Validate system performance under various loads
- Identify bottlenecks and optimization opportunities
- Ensure responsive user experience
- Measure resource utilization

## Test Scenarios

### 1. Document Loading Performance
**Test Cases:**
- Load large documents (10MB+)
- Load multiple documents simultaneously
- Search across large document corpus
- Real-time indexing performance

**Success Criteria:**
- Document load time < 2 seconds
- Search response time < 1 second
- Smooth scrolling and navigation
- No memory leaks

### 2. AI Response Performance
**Test Cases:**
- RAG search response time
- Code execution performance
- AI chat response streaming
- Model switching performance

**Success Criteria:**
- RAG search < 500ms
- Code execution < 5 seconds
- Streaming response < 100ms delay
- Model switching < 2 seconds

### 3. UI Responsiveness
**Test Cases:**
- Editor/Whiteboard switching
- Sidebar collapse/expand
- Real-time collaboration
- Large document editing

**Success Criteria:**
- UI interactions < 100ms
- Smooth animations (60fps)
- No blocking operations
- Responsive on all screen sizes

### 4. Memory and Resource Usage
**Test Cases:**
- Long-running sessions
- Multiple document editing
- Large file operations
- Background processes

**Success Criteria:**
- Memory usage < 500MB
- CPU usage < 30%
- No memory leaks
- Efficient garbage collection

## Testing Tools
- Performance monitoring tools
- Load testing frameworks
- Memory profiling
- Network analysis

## Optimization Strategies
- Lazy loading implementation
- Caching strategies
- Code splitting
- Resource optimization
                """,
                "title": "Performance Testing Guide",
                "type": "markdown"
            }
        ]
        
        return documents
    
    def add_documents_to_rag(self):
        """เพิ่มเอกสารทดสอบเข้า RAG system"""
        documents = self.prepare_test_documents()
        
        print("📚 Adding test documents to RAG system...")
        
        for doc in documents:
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/rag/documents",
                    json=doc,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Added: {doc['title']}")
                    self.test_documents.append(doc)
                else:
                    print(f"❌ Failed to add {doc['title']}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error adding {doc['title']}: {e}")
        
        print(f"\n📊 Total documents added: {len(self.test_documents)}")
        return self.test_documents
    
    def verify_rag_system(self):
        """ตรวจสอบ RAG system หลังเพิ่มข้อมูล"""
        try:
            # Get RAG info
            response = requests.get(f"{self.api_base_url}/api/rag/info")
            if response.status_code == 200:
                info = response.json()
                print(f"\n📈 RAG System Status:")
                print(f"   - Total Documents: {info['total_documents']}")
                print(f"   - Total Chunks: {info['total_chunks']}")
                print(f"   - Documents: {list(info['documents'].keys())}")
                return info
            else:
                print(f"❌ Failed to get RAG info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error verifying RAG system: {e}")
            return None

def main():
    print("🚀 Chonost Test Data Preparation")
    print("=" * 50)
    
    # Initialize test data preparation
    test_prep = TestDataPreparation()
    
    # Add documents to RAG
    documents = test_prep.add_documents_to_rag()
    
    # Verify RAG system
    rag_info = test_prep.verify_rag_system()
    
    print("\n" + "=" * 50)
    print("✅ Test data preparation completed!")
    print(f"📚 Added {len(documents)} test documents")
    
    if rag_info:
        print(f"📊 RAG system ready with {rag_info['total_documents']} documents")
    
    print("\n🎯 Ready for comprehensive testing!")

if __name__ == "__main__":
    main()
