# 🚀 Document Filler - Quick Start Guide

Welcome to Document Filler! This guide will get you up and running in minutes.

## For Windows Users

### Easiest Way - Double-Click Installation

1. **Make sure Docker Desktop is running**
   - If you don't have it: Download from https://www.docker.com/products/docker-desktop
   - Start Docker Desktop and wait for it to be ready (whale icon stops animating)

2. **Run the installer**
   - Find `install.bat` in this folder
   - Double-click `install.bat`
   - That's it! Follow the prompts.

3. **Application will open automatically**
   - Or go to: http://localhost:5173
   - API Docs: http://localhost:8000/docs

**No port conflicts!** The installer automatically detects if ports 5173 or 8000 are in use and finds available alternatives.

### What to Expect

```
=================================
Document Filler - Installation
=================================

[1/7] Checking Docker Desktop...
  ✓ Docker is installed

[2/7] Checking Docker Compose...
  ✓ Docker Compose detected

[3/7] Detecting available ports...
  ✓ Port 5173 is available
  ✓ Port 8000 is available

[4/7] OpenWebUI Configuration
  Enter OpenWebUI URL: [press Enter for default]
  Enter API Key: [optional]

... installation continues ...

Installation Complete! 🎉

  📱 Frontend:  http://localhost:5173
  🔧 Backend:   http://localhost:8000
```

**Full Windows guide**: See [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)

---

## For Linux/Mac Users

### Quick Start

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env if needed (optional)
nano .env   # or vim .env

# 3. Start the application
docker-compose up -d

# 4. Access at http://localhost:5173
```

---

## First Time Setup

Once the application is running:

### 1. Configure OpenWebUI Connection

- Click **Settings** in the top menu
- Enter your OpenWebUI URL (e.g., http://172.16.27.122:3000)
- Enter your API key if required
- Click **Save Settings**

### 2. Upload Your First Document

- Click **Upload Document** button
- Select a Word document (.docx)
- Wait for parsing to complete

### 3. Generate Content

- Select a section from the tree on the left
- Choose operation mode (Replace/Rework/Append)
- Select AI model
- Click **Generate Content**
- Review and edit the generated content
- Click **Save Changes**

### 4. Download Your Document

- Click **Download** button
- Your document will include all changes

---

## Common Issues

### "Docker Desktop is not running"
- Start Docker Desktop
- Wait for it to initialize completely
- Run installer again

### "Port already in use" (Manual setup only)
- **Windows**: Just run `install.bat` - it auto-detects available ports!
- **Linux/Mac**: Edit `.env` file and change ports:
  ```env
  FRONTEND_PORT=5174  # or any available port
  BACKEND_PORT=8001   # or any available port
  ```

### Can't access OpenWebUI
- Verify OpenWebUI URL is correct
- Test in browser: http://your-openwebui-url
- Check firewall settings
- Ensure OpenWebUI is running

---

## Useful Commands

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
docker-compose logs -f
```

### Restart
```bash
docker-compose restart
```

### Stop
```bash
docker-compose stop
```

### Uninstall (Windows)
```bash
# Double-click uninstall.bat
# Or run: .\uninstall.ps1
```

### Uninstall (Linux/Mac)
```bash
docker-compose down -v  # -v removes data volumes
```

---

## Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Read full docs**:
   - Windows: [INSTALLATION_WINDOWS.md](INSTALLATION_WINDOWS.md)
   - General: [README_WEB.md](README_WEB.md)
3. **Check Docker Desktop**: Look at containers in Docker Desktop dashboard

---

## Key URLs (Default Ports)

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main application |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/api/health | Backend status |

*If installer detected port conflicts, your ports will be different - check installer output.*

---

## What's Included

✅ **Document Processing**
- Upload Word documents
- Parse hierarchical structure
- Extract comments as guidance

✅ **AI Content Generation**
- Three modes: Replace, Rework, Append
- Multiple AI models
- Knowledge base integration (RAG)

✅ **Document Analysis**
- Technical review
- Tense consistency checking
- Readability metrics

✅ **Modern Web Interface**
- Markdown preview
- Syntax highlighting
- Real-time status updates

---

## Next Steps

- Upload a document and try generating content
- Explore the Settings page
- Try different AI models
- Experiment with operation modes (Replace/Rework/Append)
- Check out the API documentation at /docs

Enjoy Document Filler! 🎉
