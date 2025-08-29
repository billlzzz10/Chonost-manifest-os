# Chonost MCP Tool

Model Context Protocol (MCP) tool สำหรับ Chonost - The Ultimate Creative Workspace

## 🎯 Features

### 📝 Document Management
- Create, read, update, delete documents
- Rich text editing with AI assistance
- Document versioning and history

### 🎨 Visual Organization
- Interactive whiteboard for visual thinking
- Mind mapping and brainstorming tools
- Drag & drop interface

### 🤖 AI Integration
- OpenAI GPT-4 integration
- Anthropic Claude integration
- Azure OpenAI services
- Context-aware AI assistance

### 🔧 Rotary Tools
- Customizable tool palette (6+6 slots)
- Hotkey support
- Movable and resizable interface

### 📊 Knowledge Management
- Hierarchical knowledge explorer
- Tag-based organization
- Search and filtering

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Docker (for databases)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/billlzzz10/Chonost-manifest-os.git
cd Chonost-manifest-os
```

2. **Setup Frontend (Tauri)**
```bash
cd packages/frontend
npm install
npm run tauri:dev
```

3. **Setup Backend & Database**
```bash
python scripts/setup_database_and_ai.py
```

4. **Configure AI Keys**
Edit `packages/backend/.env`:
```env
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AZURE_OPENAI_API_KEY=your-azure-key
```

## 🏗️ Architecture

### Frontend (Tauri + React)
- **Framework**: Tauri for desktop app
- **UI**: React with TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand
- **Components**: 
  - Editor with rich text
  - Whiteboard for visual thinking
  - Rotary Tools palette
  - Knowledge Explorer
  - AI Assistant Panel

### Backend (FastAPI)
- **Framework**: FastAPI
- **Database**: PostgreSQL + MongoDB
- **ORM**: SQLAlchemy (async)
- **AI**: OpenAI, Anthropic, Azure
- **Vector DB**: Qdrant

### Database Schema
- **PostgreSQL**: Structured data (users, documents, relationships)
- **MongoDB**: Flexible document storage
- **Qdrant**: Vector embeddings for AI

## 🎨 UI Components

### Editor
- Rich text editing
- Real-time collaboration
- AI-powered suggestions
- Export to multiple formats

### Whiteboard
- Infinite canvas
- Shapes and connectors
- Free-form drawing
- Import/export images

### Rotary Tools
- 6 contextual tools (left)
- 6 global tools (right)
- Customizable shortcuts
- Drag & drop positioning

### Knowledge Explorer
- Tree view of documents
- Search functionality
- Tag-based filtering
- Quick navigation

### Assistant Panel
- AI chat interface
- Context-aware responses
- File upload support
- Conversation history

## 🔧 API Endpoints

### Health
- `GET /api/v1/health` - System health check

### Documents
- `GET /api/v1/documents` - List documents
- `POST /api/v1/documents` - Create document
- `GET /api/v1/documents/{id}` - Get document
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

### AI
- `POST /api/v1/ai/chat` - Chat with AI
- `GET /api/v1/ai/providers` - Available providers

### MongoDB
- `GET /api/v1/mongodb/documents` - MongoDB documents
- `POST /api/v1/mongodb/documents` - Create in MongoDB

## 🎯 Use Cases

### For Writers
- Manuscript organization
- Character development
- Plot planning
- Research management

### For Researchers
- Note-taking and organization
- Literature review
- Data visualization
- Collaboration

### For Students
- Study notes
- Project planning
- Mind mapping
- Research papers

## 🔮 Future Features

- [ ] Real-time collaboration
- [ ] Advanced AI features
- [ ] Mobile app
- [ ] Cloud sync
- [ ] Plugin system
- [ ] Advanced export options

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- GitHub Issues: [Report bugs](https://github.com/billlzzz10/Chonost-manifest-os/issues)
- Discussions: [Community forum](https://github.com/billlzzz10/Chonost-manifest-os/discussions)

---

**Chonost** - The Ultimate Creative Workspace 🚀
