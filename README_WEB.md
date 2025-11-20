# Document Filler - Web Application

AI-powered document content generation and analysis tool, now as a web application.

## Overview

This is the web version of the Document Filler desktop application, featuring:
- **FastAPI Backend**: RESTful API with async support
- **React Frontend**: Modern UI with real-time updates
- **Docker Support**: Easy deployment with Docker Compose
- **OpenWebUI Integration**: AI-powered content generation
- **Document Analysis**: Technical review, tense checking, readability metrics

## Quick Start with Docker Compose

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker + Docker Compose (Linux)
- OpenWebUI instance accessible from your machine

### 1. Configure Ports (Optional)

Copy the example environment file:
```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # Linux/Mac
```

Edit `.env` to customize ports if needed:
```env
FRONTEND_PORT=5173      # Change if port 5173 is in use
BACKEND_PORT=8000       # Change if port 8000 is in use
OPENWEBUI_BASE_URL=http://172.16.27.122:3000
OPENWEBUI_API_KEY=your-api-key-here
```

### 2. Start the Application

```bash
docker-compose up -d
```

This will:
- Build both frontend and backend containers
- Start the services with your configured ports
- Create persistent volumes for uploads and data

### 3. Access the Application

- **Frontend**: http://localhost:5173 (or your custom FRONTEND_PORT)
- **Backend API**: http://localhost:8000 (or your custom BACKEND_PORT)
- **API Documentation**: http://localhost:8000/docs

### 4. Stop the Application

```bash
docker-compose down
```

To remove volumes (deletes uploaded files and data):
```bash
docker-compose down -v
```

## Development Setup (Without Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file from .env.example
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173

## Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── documents.py # Document upload/management
│   │       ├── content.py   # AI content generation
│   │       ├── review.py    # Document review/analysis
│   │       └── config.py    # Configuration
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── document_service.py
│   │   ├── content_service.py
│   │   └── review_service.py
│   └── utils/               # Utilities
└── requirements.txt
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── components/          # React components
│   ├── pages/               # Page components
│   ├── services/            # API client
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── package.json
└── vite.config.js
```

## Features

### Document Management
- Upload Word documents (.docx)
- Parse hierarchical structure (headings 1-6)
- Extract and display comments
- Download modified documents

### Content Generation
- Three operation modes:
  - **Replace**: Generate new content from scratch
  - **Rework**: Enhance existing content
  - **Append**: Add to existing content
- Model selection and comparison
- Knowledge base integration (RAG)
- Real-time generation status via WebSocket

### Document Analysis
- Technical review with scoring (cohesion, clarity, accuracy, etc.)
- Tense consistency analysis
- Readability metrics
- Automated suggestions

### Configuration
- OpenWebUI connection settings
- Prompt template library
- Formatting preferences
- Auto-backup options

## API Endpoints

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/{id}/structure` - Get document structure
- `POST /api/documents/{id}/save` - Save updates
- `GET /api/documents/{id}/download` - Download document
- `DELETE /api/documents/{id}` - Delete document

### Content Generation
- `POST /api/content/generate` - Generate content
- `POST /api/content/compare-models` - Compare models
- `WS /api/content/ws/generate/{client_id}` - Real-time generation
- `GET /api/content/models` - List available models
- `GET /api/content/knowledge-collections` - List RAG collections

### Review & Analysis
- `POST /api/review/conduct` - Conduct technical review
- `POST /api/review/analyze-tenses` - Analyze tenses
- `POST /api/review/apply-suggestions/{doc_id}/{section_id}` - Apply suggestions
- `GET /api/review/readability/{doc_id}/{section_id}` - Get readability metrics

### Configuration
- `GET/POST /api/config/openwebui` - OpenWebUI settings
- `GET/POST/DELETE /api/config/prompts` - Prompt templates
- `GET/POST /api/config/app` - App configuration

## Environment Variables

### Backend (.env)
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenWebUI
OPENWEBUI_BASE_URL=http://172.16.27.122:3000
OPENWEBUI_API_KEY=your-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./documentfiller.db

# File Upload
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Port Conflicts

If the default ports are in use, update `.env`:

```env
FRONTEND_PORT=8080   # Instead of 5173
BACKEND_PORT=9000    # Instead of 8000
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Backend won't start
- Check if port is already in use
- Verify OpenWebUI URL is accessible
- Check Docker logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify BACKEND_PORT matches in .env
- Check CORS settings in backend/.env
- Ensure both containers are running: `docker-compose ps`

### Document upload fails
- Check file size (max 50MB by default)
- Verify uploads volume is mounted
- Check backend logs for errors

## Migration from Desktop App

The desktop application (documentFiller5.py) is still available and functional. The web version provides:
- Multi-user access
- No local Python installation needed
- Better scalability
- Remote access capability
- Modern UI/UX

Core features have been ported:
- ✅ Document parsing and structure extraction
- ✅ OpenWebUI integration
- ✅ Content generation (replace/rework/append)
- ✅ Model comparison
- ✅ Technical review
- ✅ Tense analysis
- 🚧 Prompt library (partial)
- 🚧 External RAG management (pending)
- 🚧 Advanced formatting (pending)

## License

Same as the desktop application.
