# Document Filler - Windows Installation Script
# Automatically detects available ports and configures the application

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Document Filler - Installation" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a port is in use
function Test-PortInUse {
    param([int]$Port)

    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $Port)
        $connection.Close()
        return $true  # Port is in use
    }
    catch {
        return $false  # Port is available
    }
}

# Function to find next available port
function Get-AvailablePort {
    param(
        [int]$StartPort,
        [int[]]$ExcludePorts = @()
    )

    $port = $StartPort
    while ($true) {
        if (-not (Test-PortInUse -Port $port) -and $port -notin $ExcludePorts) {
            return $port
        }
        $port++

        # Safety check - don't go beyond 65535
        if ($port -gt 65535) {
            Write-Host "ERROR: Could not find available port starting from $StartPort" -ForegroundColor Red
            exit 1
        }
    }
}

# Check if Docker Desktop is running
Write-Host "[1/7] Checking Docker Desktop..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker command failed"
    }
    Write-Host "  ✓ Docker is installed: $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Docker Desktop is not running or not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "Make sure Docker Desktop is running before running this script." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if docker-compose is available
Write-Host ""
Write-Host "[2/7] Checking Docker Compose..." -ForegroundColor Yellow
try {
    docker-compose --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        # Try docker compose (v2 syntax)
        docker compose version 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose not found"
        }
        $script:useDockerComposeV2 = $true
        Write-Host "  ✓ Docker Compose V2 detected" -ForegroundColor Green
    }
    else {
        $script:useDockerComposeV2 = $false
        Write-Host "  ✓ Docker Compose detected" -ForegroundColor Green
    }
}
catch {
    Write-Host "  ✗ Docker Compose not available" -ForegroundColor Red
    exit 1
}

# Find available ports
Write-Host ""
Write-Host "[3/7] Detecting available ports..." -ForegroundColor Yellow

$defaultFrontendPort = 5173
$defaultBackendPort = 8000

Write-Host "  Checking frontend port $defaultFrontendPort..." -ForegroundColor Gray
$frontendPort = Get-AvailablePort -StartPort $defaultFrontendPort

if ($frontendPort -ne $defaultFrontendPort) {
    Write-Host "  ⚠ Port $defaultFrontendPort is in use, using $frontendPort instead" -ForegroundColor Yellow
}
else {
    Write-Host "  ✓ Port $frontendPort is available" -ForegroundColor Green
}

Write-Host "  Checking backend port $defaultBackendPort..." -ForegroundColor Gray
$backendPort = Get-AvailablePort -StartPort $defaultBackendPort -ExcludePorts @($frontendPort)

if ($backendPort -ne $defaultBackendPort) {
    Write-Host "  ⚠ Port $defaultBackendPort is in use, using $backendPort instead" -ForegroundColor Yellow
}
else {
    Write-Host "  ✓ Port $backendPort is available" -ForegroundColor Green
}

# Get OpenWebUI configuration
Write-Host ""
Write-Host "[4/7] OpenWebUI Configuration" -ForegroundColor Yellow

$openwebuiUrl = Read-Host "  Enter OpenWebUI URL (default: http://172.16.27.122:3000)"
if ([string]::IsNullOrWhiteSpace($openwebuiUrl)) {
    $openwebuiUrl = "http://172.16.27.122:3000"
}

$openwebuiApiKey = Read-Host "  Enter OpenWebUI API Key (press Enter to skip)"

# Create .env file
Write-Host ""
Write-Host "[5/7] Creating configuration file..." -ForegroundColor Yellow

$envContent = @"
# Document Filler - Auto-generated Configuration
# Generated on: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Port Configuration (auto-detected)
FRONTEND_PORT=$frontendPort
BACKEND_PORT=$backendPort

# OpenWebUI Configuration
OPENWEBUI_BASE_URL=$openwebuiUrl
OPENWEBUI_API_KEY=$openwebuiApiKey

# CORS Configuration (auto-configured)
CORS_ORIGINS=http://localhost:$frontendPort,http://127.0.0.1:$frontendPort

# Security (change in production)
SECRET_KEY=$(([char[]]([char]'a'..[char]'z') + ([char[]]([char]'A'..[char]'Z')) + 0..9 | Get-Random -Count 32) -join '')

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./documentfiller.db

# File Upload
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "  ✓ Configuration saved to .env" -ForegroundColor Green

# Also create backend/.env for local development
if (-not (Test-Path "backend")) {
    New-Item -ItemType Directory -Path "backend" -Force | Out-Null
}

$backendEnvContent = @"
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenWebUI
OPENWEBUI_BASE_URL=$openwebuiUrl
OPENWEBUI_API_KEY=$openwebuiApiKey

# Database
DATABASE_URL=sqlite+aiosqlite:///./documentfiller.db

# File Upload
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads

# CORS
CORS_ORIGINS=http://localhost:$frontendPort,http://127.0.0.1:$frontendPort

# Security
SECRET_KEY=$(([char[]]([char]'a'..[char]'z') + ([char[]]([char]'A'..[char]'Z')) + 0..9 | Get-Random -Count 32) -join '')
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"@

$backendEnvContent | Out-File -FilePath "backend/.env" -Encoding UTF8
Write-Host "  ✓ Backend configuration created" -ForegroundColor Green

# Update frontend environment variable for API URL
if (-not (Test-Path "frontend")) {
    New-Item -ItemType Directory -Path "frontend" -Force | Out-Null
}

$frontendEnvContent = @"
VITE_API_URL=http://localhost:$backendPort
"@

$frontendEnvContent | Out-File -FilePath "frontend/.env" -Encoding UTF8
Write-Host "  ✓ Frontend configuration created" -ForegroundColor Green

# Build and start containers
Write-Host ""
Write-Host "[6/7] Building and starting containers..." -ForegroundColor Yellow
Write-Host "  This may take several minutes on first run..." -ForegroundColor Gray

try {
    if ($script:useDockerComposeV2) {
        docker compose up -d --build
    }
    else {
        docker-compose up -d --build
    }

    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed"
    }

    Write-Host "  ✓ Containers started successfully" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ Failed to start containers" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check Docker Desktop logs for more information." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Wait for services to be ready
Write-Host ""
Write-Host "[7/7] Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

$maxAttempts = 30
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$backendPort/api/health" -Method GET -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
        }
    }
    catch {
        $attempt++
        Write-Host "  Waiting for backend... ($attempt/$maxAttempts)" -ForegroundColor Gray
        Start-Sleep -Seconds 2
    }
}

if ($backendReady) {
    Write-Host "  ✓ Backend is ready!" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ Backend is taking longer than expected to start" -ForegroundColor Yellow
    Write-Host "  You can check status with: docker-compose logs backend" -ForegroundColor Gray
}

# Installation complete
Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "Installation Complete! 🎉" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Document Filler application is now running:" -ForegroundColor White
Write-Host ""
Write-Host "  📱 Frontend:  http://localhost:$frontendPort" -ForegroundColor Cyan
Write-Host "  🔧 Backend:   http://localhost:$backendPort" -ForegroundColor Cyan
Write-Host "  📚 API Docs:  http://localhost:$backendPort/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration saved in .env file" -ForegroundColor Gray
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor White
Write-Host "  View logs:    docker-compose logs -f" -ForegroundColor Gray
Write-Host "  Stop:         docker-compose stop" -ForegroundColor Gray
Write-Host "  Restart:      docker-compose restart" -ForegroundColor Gray
Write-Host "  Uninstall:    .\uninstall.ps1" -ForegroundColor Gray
Write-Host ""

# Open browser
$openBrowser = Read-Host "Open application in browser? (Y/n)"
if ($openBrowser -eq "" -or $openBrowser -eq "Y" -or $openBrowser -eq "y") {
    Start-Process "http://localhost:$frontendPort"
}

Write-Host ""
Read-Host "Press Enter to exit"
