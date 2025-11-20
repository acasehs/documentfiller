#!/bin/bash

echo "🚀 DocumentFiller Web Application Setup"
echo "========================================"
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker and Docker Compose found"
    USE_DOCKER=true
else
    echo "⚠️  Docker not found. Will set up for local development."
    USE_DOCKER=false
fi

echo ""
echo "Setting up environment..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created. Please edit with your configuration."
else
    echo "✅ .env file already exists"
fi

echo ""

if [ "$USE_DOCKER" = true ]; then
    echo "🐳 Docker Setup"
    echo "---------------"
    read -p "Do you want to start the application with Docker now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Building and starting containers..."
        docker-compose up -d --build
        echo ""
        echo "✅ Application started!"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "To view logs: docker-compose logs -f"
        echo "To stop: docker-compose down"
    else
        echo "To start later, run: docker-compose up -d"
    fi
else
    echo "💻 Local Development Setup"
    echo "--------------------------"
    echo ""

    # Backend setup
    echo "Setting up backend..."
    cd backend || exit 1

    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    REQUIRED_VERSION="3.11"

    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        echo "✅ Python $PYTHON_VERSION found"
    else
        echo "❌ Python 3.11+ required. Found: $PYTHON_VERSION"
        exit 1
    fi

    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "Installing Python dependencies..."
    pip install -r requirements.txt

    echo "Downloading NLTK data..."
    python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

    cd ..

    echo ""
    echo "✅ Backend setup complete!"
    echo ""

    # Frontend setup
    echo "Setting up frontend..."
    cd frontend || exit 1

    # Check Node version
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | grep -oP '\d+' | head -1)
        if [ "$NODE_VERSION" -ge 18 ]; then
            echo "✅ Node.js $NODE_VERSION found"
        else
            echo "❌ Node.js 18+ required. Found: $NODE_VERSION"
            exit 1
        fi
    else
        echo "❌ Node.js not found. Please install Node.js 18+"
        exit 1
    fi

    echo "Installing Node dependencies..."
    npm install

    cd ..

    echo ""
    echo "✅ Frontend setup complete!"
    echo ""

    # Create startup script
    cat > start-dev.sh << 'EOF'
#!/bin/bash

echo "Starting DocumentFiller Web Application..."

# Start backend
echo "Starting backend on http://localhost:8000..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Application started!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

    chmod +x start-dev.sh

    echo "📝 Created start-dev.sh script"
    echo ""
    echo "To start the application, run: ./start-dev.sh"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your OpenWebUI configuration"
echo "2. Start the application"
echo "3. Navigate to Configuration page and set up API connection"
echo "4. Upload a document and start generating!"
echo ""
echo "Documentation:"
echo "- Web App Guide: WEB_APP_README.md"
echo "- Migration Status: MIGRATION_STATUS.md"
echo "- Original Desktop: CODEBASE_OVERVIEW.md"
