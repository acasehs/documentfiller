# DocumentFiller Web Application

A modern web-based version of the DocumentFiller application, featuring a FastAPI backend and React frontend for AI-powered document generation.

## 🌟 Features

### Core Functionality
- **Document Upload & Parsing** - Upload DOCX files and automatically parse structure
- **AI Content Generation** - Generate content using OpenWebUI/Ollama with RAG support
- **Multiple Operation Modes** - REPLACE, REWORK, or APPEND content
- **Technical Review** - Comprehensive quality analysis with metrics
- **Real-time Updates** - WebSocket support for batch processing
- **Document Download** - Export modified documents

### Modern Architecture
- **FastAPI Backend** - High-performance async REST API
- **React + TypeScript Frontend** - Modern, type-safe UI
- **Responsive Design** - TailwindCSS for beautiful, mobile-friendly interface
- **Docker Support** - Easy deployment with docker-compose
- **WebSocket Integration** - Real-time progress updates

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose (recommended), OR
- Python 3.11+ and Node.js 20+
- OpenWebUI/Ollama instance running

### Option 1: Docker (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd documentfiller
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Download NLTK data:**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
   ```

3. **Start the backend:**
   ```bash
   python app.py
   # Or use uvicorn directly:
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install Node dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## 📁 Project Structure

```
documentfiller/
├── backend/
│   ├── app.py                 # FastAPI application
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   └── Layout.tsx
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── DocumentEditor.tsx
│   │   │   └── Configuration.tsx
│   │   ├── App.tsx            # Main app component
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── package.json           # Node dependencies
│   ├── vite.config.ts         # Vite configuration
│   └── Dockerfile             # Frontend Docker image
├── content_processor.py       # RAG and strategy logic
├── document_reviewer.py       # Technical review system
├── credential_manager.py      # Encrypted credential storage
├── docker-compose.yml         # Docker orchestration
├── Dockerfile.backend         # Backend Docker image
└── WEB_APP_README.md          # This file
```

## 🔧 Configuration

### 1. Configure OpenWebUI Connection

Navigate to the Configuration page (http://localhost:3000/config) and enter:

- **API URL**: Your OpenWebUI endpoint (e.g., `http://localhost:3000`)
- **API Key**: Your OpenWebUI API key
- **Model**: Select from available models
- **Temperature**: 0.0 (precise) to 2.0 (creative)
- **Max Tokens**: Maximum tokens for generation

### 2. Environment Variables

Edit `.env` file:

```env
# Backend
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend
VITE_API_URL=http://localhost:8000

# OpenWebUI
OPENWEBUI_API_URL=http://localhost:3000
OPENWEBUI_API_KEY=your-api-key
```

## 📖 Usage Guide

### 1. Upload a Document

1. Go to the Dashboard
2. Click "Choose Document"
3. Select a `.docx` file with structured headings
4. Document will be parsed and you'll be redirected to the editor

### 2. Generate Content

1. In the Document Editor, select a section from the tree
2. Choose an operation mode:
   - **REPLACE**: Generate new content from scratch
   - **REWORK**: Improve existing content
   - **APPEND**: Add to existing content
3. Click "Generate"
4. Review the generated content in the right panel

### 3. Review Quality

1. After generating content, click "Review"
2. View scores for:
   - Cohesion
   - Clarity
   - Accuracy
   - Factual Veracity
   - Completeness
3. Read specific feedback and recommendations

### 4. Commit Changes

1. Edit the generated content if needed
2. Click "Commit" to save changes to the document
3. Download the modified document when done

## 🔌 API Endpoints

### Document Management
- `POST /api/documents/upload` - Upload DOCX document
- `GET /api/documents/{id}` - Get document metadata
- `POST /api/documents/{id}/commit` - Commit content changes
- `GET /api/documents/{id}/download` - Download document

### Content Generation
- `POST /api/generate` - Generate content for a section
- `POST /api/review` - Review content quality
- `POST /api/batch/process` - Batch process multiple sections

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Save configuration
- `GET /api/models` - Get available models
- `GET /api/collections` - Get knowledge collections

### WebSocket
- `WS /ws/{client_id}` - WebSocket connection for real-time updates

Full API documentation: http://localhost:8000/docs

## 🎨 UI Features

### Dark Theme
Modern dark theme optimized for extended use with reduced eye strain.

### Responsive Layout
- **Left Panel**: Document tree and controls
- **Right Panel**: Split view showing existing vs. generated content
- **Top Bar**: Navigation and quick actions

### Real-time Updates
WebSocket integration provides live progress updates during batch operations.

### Markdown Rendering
Generated content supports full markdown with syntax highlighting.

## 🔐 Security Considerations

### Current Implementation
- Session-based configuration storage
- CORS protection
- Request validation with Pydantic

### Recommended for Production
- [ ] Implement JWT authentication
- [ ] Add user account management
- [ ] Use PostgreSQL instead of in-memory storage
- [ ] Implement rate limiting
- [ ] Add HTTPS/TLS
- [ ] Secure credential encryption with user-specific keys
- [ ] Add audit logging

## 🚧 Future Enhancements

### High Priority
- [ ] User authentication and multi-user support
- [ ] Persistent database (PostgreSQL)
- [ ] Background task queue (Celery/Redis)
- [ ] Complete batch processing with WebSocket updates
- [ ] File upload size limits and validation
- [ ] Error handling and user feedback improvements

### Medium Priority
- [ ] Model comparison (side-by-side generation)
- [ ] Prompt template library
- [ ] Document version history
- [ ] Collaborative editing
- [ ] Export to multiple formats (PDF, HTML, Markdown)

### Low Priority
- [ ] Mobile app (React Native)
- [ ] Offline mode with service workers
- [ ] Advanced analytics dashboard
- [ ] Integration with SharePoint/OneDrive
- [ ] Custom review metrics

## 📊 Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **python-docx** - DOCX manipulation
- **Pydantic** - Data validation
- **tiktoken** - Token counting
- **scikit-learn** - RAG similarity
- **NLTK** - NLP analysis
- **textstat** - Readability metrics

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **TanStack Query** - Data fetching
- **Axios** - HTTP client
- **React Markdown** - Markdown rendering
- **Lucide React** - Icons

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is available
lsof -i :8000

# Check Python dependencies
pip install -r backend/requirements.txt

# Check NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

### Frontend won't start
```bash
# Clear npm cache
rm -rf node_modules package-lock.json
npm install

# Check if port 3000 is available
lsof -i :3000
```

### Document upload fails
- Ensure file is `.docx` format (not `.doc`)
- Check file has proper heading structure
- Verify backend is running and accessible
- Check browser console for errors

### Generation fails
- Verify OpenWebUI configuration in Settings
- Test API connection: `curl http://localhost:8000/api/models`
- Check OpenWebUI is running and accessible
- Verify API key is correct

### Docker issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 📝 Development

### Running Tests
```bash
# Backend tests (to be implemented)
cd backend
pytest

# Frontend tests (to be implemented)
cd frontend
npm test
```

### Code Quality
```bash
# Backend linting
black backend/
flake8 backend/

# Frontend linting
cd frontend
npm run lint
```

### Building for Production
```bash
# Frontend production build
cd frontend
npm run build

# Backend with gunicorn
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

This is a migration of the existing DocumentFiller desktop application. Contributions welcome!

### Priority Areas
1. Authentication system implementation
2. Database integration (PostgreSQL)
3. Test coverage
4. Performance optimization
5. Documentation improvements

## 📄 License

Same as parent DocumentFiller project.

## 🙏 Acknowledgments

- Built on top of the original DocumentFiller desktop application
- Uses OpenWebUI/Ollama for LLM integration
- Designed for DoD cybersecurity documentation compliance

---

**Note**: This web application is in active development. Some features from the desktop version are still being migrated. See TODO items above for planned enhancements.
