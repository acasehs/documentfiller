# DocumentFiller v2.0 - Quick Start Guide

Get up and running with DocumentFiller in under 5 minutes!

## 🚀 Option 1: Docker (Recommended - Fastest!)

### Prerequisites
- Docker and Docker Compose installed
- OpenWebUI/Ollama running (or access to an instance)

### Steps

```bash
# 1. Navigate to project directory
cd documentfiller

# 2. Create environment file (optional)
cp .env.example .env
# Edit .env if needed

# 3. Start the application
docker-compose up -d

# 4. Wait for containers to start (30-60 seconds)
docker-compose logs -f

# 5. Access the application
# Open browser: http://localhost:3000
```

**That's it!** 🎉

---

## 💻 Option 2: Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenWebUI/Ollama running

### Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# 6. Start the backend
python app_enhanced.py

# Backend running at: http://localhost:8000
```

### Frontend Setup (New Terminal)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# Frontend running at: http://localhost:3000
```

---

## 🔑 First Time Setup

### 1. Register Account

1. Open http://localhost:3000/login
2. Click **"Register"** tab
3. Enter:
   - Email: your@email.com
   - Username: yourusername
   - Password: (secure password)
4. Click **"Register"**
5. You'll be automatically logged in!

### 2. Configure OpenWebUI API

1. Click **"Configuration"** in the top navigation
2. Enter your settings:
   - **API URL**: `http://localhost:3000` (or your OpenWebUI URL)
   - **API Key**: Your OpenWebUI API key
   - Click **"Fetch Available Models"**
   - Select a **Model** from the dropdown
3. Click **"Save Configuration"**

### 3. Upload Your First Document

1. Click **"Dashboard"**
2. Click **"Choose Document"**
3. Select a `.docx` file with structured headings
4. Wait for upload and parsing
5. You'll be redirected to the Document Editor

### 4. Generate Content

1. In the Document Editor:
   - Select a section from the tree (left sidebar)
   - Choose operation mode:
     - **REPLACE**: Generate new content from scratch
     - **REWORK**: Improve existing content
     - **APPEND**: Add to existing content
2. Click **"Generate"**
3. Review the generated content (right panel)
4. Click **"Review"** to get quality metrics (optional)
5. Click **"Commit"** to save to document
6. Click **"Download"** when done

---

## 🎯 Key Features to Try

### Model Comparison
1. Go to **"Compare"** in navigation
2. Enter section title and content
3. Select up to 3 models
4. Click **"Generate & Compare"**
5. See results side-by-side
6. Select the best one!

### Batch Processing
1. In Document Editor, click **"Auto-Complete"** (coming soon in UI)
2. Select sections to process
3. Watch real-time progress
4. Pause/Resume as needed

### Technical Review
1. After generating content, click **"Review"**
2. Get scores for:
   - Cohesion
   - Clarity
   - Accuracy
   - Factual Veracity
   - Completeness
3. Get specific recommendations
4. Regenerate based on feedback

---

## 📁 Document Requirements

Your DOCX files should have:
- **Structured headings** (Heading 1, Heading 2, etc.)
- Sections with titles
- (Optional) Some existing content

Example structure:
```
Heading 1: System Security Plan
  Heading 2: 1. Introduction
    Paragraph: This document describes...
  Heading 2: 2. System Overview
    Paragraph: The system consists of...
  Heading 2: 3. Security Controls
    ...
```

---

## 🔧 Common Issues & Solutions

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# If using Docker, check logs
docker-compose logs backend
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Can't upload document
- Ensure file is `.docx` (not `.doc`)
- Check file has proper heading structure
- Verify backend is running
- Check browser console for errors

### Generation fails
- Verify OpenWebUI configuration
- Test API: `curl http://localhost:8000/api/models`
- Check OpenWebUI is accessible
- Verify API key is correct

### Login doesn't work
- Check if backend is running
- Clear browser localStorage
- Try incognito/private mode
- Check browser console for errors

---

## 📊 Default Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| Backend API Docs | 8000 | http://localhost:8000/docs |
| OpenWebUI (typical) | 3000 | http://localhost:3000 |

If ports conflict, edit:
- Backend: `docker-compose.yml` or run with `--port` flag
- Frontend: `vite.config.ts`

---

## 🎓 Tips for Best Results

### Content Generation
- **Be specific** in section titles
- **Use master prompts** for consistency
- **Set temperature**:
  - 0.0-0.3: Precise, factual (technical docs)
  - 0.4-0.7: Balanced (default)
  - 0.8-2.0: Creative (marketing, stories)

### Document Quality
- Start with a **template document** with headings
- Use **REWORK** to improve existing content
- Use **APPEND** to add details
- Use **REPLACE** for completely new sections

### Performance
- **Batch process** empty sections overnight
- Use **model comparison** for critical sections
- **Review** important sections before committing

---

## 📚 Additional Resources

- **Full Documentation**: [WEB_APP_README.md](./WEB_APP_README.md)
- **v2.0 Features**: [V2_UPDATES.md](./V2_UPDATES.md)
- **Migration Status**: [MIGRATION_STATUS.md](./MIGRATION_STATUS.md)
- **API Documentation**: http://localhost:8000/docs (when running)

---

## 🐛 Troubleshooting

### Validation Check
```bash
# Run validation script
python validate_v2.py
```

### View Docker Logs
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### Reset Everything
```bash
# Stop and remove containers
docker-compose down -v

# Remove database (fresh start)
rm -f documentfiller.db

# Rebuild and start
docker-compose up -d --build
```

---

## 🆘 Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Run validation**: `python validate_v2.py`
3. **Check documentation**: See files above
4. **GitHub Issues**: Report bugs with logs attached

---

## ✅ Verification Checklist

After setup, verify these work:

- [ ] Can access http://localhost:3000
- [ ] Can register new account
- [ ] Can login successfully
- [ ] Can access Configuration page
- [ ] Can fetch models from OpenWebUI
- [ ] Can upload a DOCX file
- [ ] Document sections appear in tree
- [ ] Can select a section
- [ ] Can generate content
- [ ] Can review content
- [ ] Can commit changes
- [ ] Can download document
- [ ] Can access Model Comparison
- [ ] Can logout

If all checked, you're ready to go! 🎉

---

## 🚀 Next Steps

Now that you're set up:

1. **Upload your first document**
2. **Try different models** via Compare page
3. **Experiment with temperatures**
4. **Use batch processing** for multiple sections
5. **Review and refine** generated content
6. **Download** your enhanced document

**Happy Document Filling!** 📄✨

---

**Version**: 2.0.0
**Last Updated**: 2025-11-20
**Questions?** Check [WEB_APP_README.md](./WEB_APP_README.md)
