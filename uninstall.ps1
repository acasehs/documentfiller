# Document Filler - Uninstall Script

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Document Filler - Uninstall" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Confirm uninstall
$confirm = Read-Host "Are you sure you want to uninstall Document Filler? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Uninstall cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  - Stop and remove containers" -ForegroundColor Gray
Write-Host "  - Remove Docker images" -ForegroundColor Gray
Write-Host "  - Optionally remove uploaded documents and data" -ForegroundColor Gray
Write-Host ""

$removeData = Read-Host "Remove all uploaded documents and data? (y/N)"

# Check if docker-compose is available
try {
    docker-compose --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        # Try docker compose (v2 syntax)
        docker compose version 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose not found"
        }
        $script:useDockerComposeV2 = $true
    }
    else {
        $script:useDockerComposeV2 = $false
    }
}
catch {
    Write-Host "✗ Docker Compose not available" -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is running." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Stop and remove containers
Write-Host ""
Write-Host "[1/4] Stopping containers..." -ForegroundColor Yellow

try {
    if ($script:useDockerComposeV2) {
        docker compose stop
    }
    else {
        docker-compose stop
    }
    Write-Host "  ✓ Containers stopped" -ForegroundColor Green
}
catch {
    Write-Host "  ⚠ No containers to stop or error occurred" -ForegroundColor Yellow
}

# Remove containers
Write-Host ""
Write-Host "[2/4] Removing containers..." -ForegroundColor Yellow

try {
    if ($script:useDockerComposeV2) {
        if ($removeData -eq "y" -or $removeData -eq "Y") {
            docker compose down -v
            Write-Host "  ✓ Containers and volumes removed" -ForegroundColor Green
        }
        else {
            docker compose down
            Write-Host "  ✓ Containers removed (data preserved)" -ForegroundColor Green
        }
    }
    else {
        if ($removeData -eq "y" -or $removeData -eq "Y") {
            docker-compose down -v
            Write-Host "  ✓ Containers and volumes removed" -ForegroundColor Green
        }
        else {
            docker-compose down
            Write-Host "  ✓ Containers removed (data preserved)" -ForegroundColor Green
        }
    }
}
catch {
    Write-Host "  ⚠ Error removing containers" -ForegroundColor Yellow
}

# Remove images
Write-Host ""
Write-Host "[3/4] Removing Docker images..." -ForegroundColor Yellow

try {
    $images = docker images --filter "reference=documentfiller*" -q
    if ($images) {
        docker rmi $images -f
        Write-Host "  ✓ Docker images removed" -ForegroundColor Green
    }
    else {
        Write-Host "  ℹ No Document Filler images found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "  ⚠ Error removing images" -ForegroundColor Yellow
}

# Clean up configuration files
Write-Host ""
Write-Host "[4/4] Cleaning up configuration files..." -ForegroundColor Yellow

$removeConfig = Read-Host "Remove configuration files (.env)? (y/N)"
if ($removeConfig -eq "y" -or $removeConfig -eq "Y") {
    if (Test-Path ".env") {
        Remove-Item ".env" -Force
        Write-Host "  ✓ Removed .env" -ForegroundColor Green
    }
    if (Test-Path "backend/.env") {
        Remove-Item "backend/.env" -Force
        Write-Host "  ✓ Removed backend/.env" -ForegroundColor Green
    }
    if (Test-Path "frontend/.env") {
        Remove-Item "frontend/.env" -Force
        Write-Host "  ✓ Removed frontend/.env" -ForegroundColor Green
    }
}
else {
    Write-Host "  ℹ Configuration files preserved" -ForegroundColor Gray
}

# Remove local data directories if requested
if ($removeData -eq "y" -or $removeData -eq "Y") {
    Write-Host ""
    Write-Host "Removing local data directories..." -ForegroundColor Yellow

    if (Test-Path "uploads") {
        Remove-Item "uploads" -Recurse -Force
        Write-Host "  ✓ Removed uploads directory" -ForegroundColor Green
    }
    if (Test-Path "backend/uploads") {
        Remove-Item "backend/uploads" -Recurse -Force
        Write-Host "  ✓ Removed backend/uploads directory" -ForegroundColor Green
    }
    if (Test-Path "backend/data") {
        Remove-Item "backend/data" -Recurse -Force
        Write-Host "  ✓ Removed backend/data directory" -ForegroundColor Green
    }
    if (Test-Path "backend/*.db") {
        Remove-Item "backend/*.db" -Force
        Write-Host "  ✓ Removed database files" -ForegroundColor Green
    }
}

# Complete
Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "Uninstall Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""
Write-Host "Document Filler has been removed from your system." -ForegroundColor White
Write-Host ""

if ($removeData -ne "y" -and $removeData -ne "Y") {
    Write-Host "Note: Docker volumes with your uploaded documents were preserved." -ForegroundColor Yellow
    Write-Host "To remove them manually, run: docker volume prune" -ForegroundColor Gray
}

if ($removeConfig -ne "y" -and $removeConfig -ne "Y") {
    Write-Host "Note: Configuration files were preserved for future reinstallation." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
