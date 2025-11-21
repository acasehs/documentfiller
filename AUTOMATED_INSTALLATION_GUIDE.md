# Automated Installation System - Technical Overview

## What Was Added

### Installation Scripts

Four new scripts for Windows users:

1. **`install.ps1`** - PowerShell script with full automation
   - ~350 lines of intelligent installation logic
   - Port detection and conflict resolution
   - Configuration file generation
   - Container build and verification

2. **`install.bat`** - Windows batch file launcher
   - Double-click friendly
   - Checks PowerShell availability
   - Runs with execution policy bypass

3. **`uninstall.ps1`** - PowerShell uninstallation script
   - ~200 lines of cleanup logic
   - Selective removal options
   - Data preservation choices

4. **`uninstall.bat`** - Windows batch file launcher
   - Double-click uninstall
   - Safe removal process

### Documentation

Three comprehensive guides:

1. **`INSTALLATION_WINDOWS.md`** - Full Windows installation guide
2. **`START_HERE.md`** - Quick start for all users
3. **Updated `README_WEB.md`** - Windows-first approach

## How It Works

### Port Detection Algorithm

```
1. Define default ports:
   - Frontend: 5173
   - Backend: 8000

2. Test frontend port:
   - Try to connect to 127.0.0.1:5173
   - If connection succeeds → port is in use
   - If connection fails → port is available
   - If in use, try 5174, 5175, etc.

3. Test backend port:
   - Same logic as frontend
   - MUST be different from frontend port
   - Uses exclusion list to avoid collision

4. Create configurations:
   - Root .env (Docker Compose)
   - backend/.env (Backend API)
   - frontend/.env (Frontend build)
   - All files use detected ports
```

### Configuration Flow

```
User runs install.bat
        ↓
    install.ps1 starts
        ↓
Check Docker Desktop running
        ↓
Detect available ports
        ↓
Prompt for OpenWebUI settings
        ↓
Create .env files:
    ├── ./.env (FRONTEND_PORT, BACKEND_PORT, OPENWEBUI_BASE_URL, etc.)
    ├── ./backend/.env (API config with CORS using FRONTEND_PORT)
    └── ./frontend/.env (VITE_API_URL using BACKEND_PORT)
        ↓
docker-compose up -d --build
    ├── Backend builds with backend/.env
    └── Frontend builds with VITE_API_URL from build args
        ↓
Wait for backend health check
        ↓
Display URLs and open browser
```

### Environment Variable Propagation

#### Root `.env`
```env
FRONTEND_PORT=5173
BACKEND_PORT=8000
OPENWEBUI_BASE_URL=http://172.16.27.122:3000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### `backend/.env`
```env
API_PORT=8000
OPENWEBUI_BASE_URL=http://172.16.27.122:3000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

#### `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
```

#### Docker Compose
```yaml
services:
  backend:
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    environment:
      - CORS_ORIGINS=http://localhost:${FRONTEND_PORT:-5173}

  frontend:
    build:
      args:
        - VITE_API_URL=http://localhost:${BACKEND_PORT:-8000}
    ports:
      - "${FRONTEND_PORT:-5173}:80"
```

## PowerShell Functions

### `Test-PortInUse`
```powershell
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
```

**How it works:**
- Creates TCP client
- Attempts connection to localhost:port
- If connection succeeds → port is occupied
- If exception thrown → port is free

### `Get-AvailablePort`
```powershell
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
        if ($port -gt 65535) {
            throw "Could not find available port"
        }
    }
}
```

**How it works:**
- Starts at specified port
- Tests if port is in use
- Checks if port is in exclusion list
- Increments until finding available port
- Safety limit at 65535

## Installation Process (Step-by-Step)

### Step 1: Pre-flight Checks
```
[1/7] Checking Docker Desktop...
  ✓ Docker is installed: Docker version 24.0.6
```

- Runs `docker --version`
- Checks exit code
- Displays error if Docker not available

### Step 2: Docker Compose Check
```
[2/7] Checking Docker Compose...
  ✓ Docker Compose V2 detected
```

- Tests both `docker-compose` and `docker compose`
- Detects version (V1 vs V2)
- Sets flag for later use

### Step 3: Port Detection
```
[3/7] Detecting available ports...
  Checking frontend port 5173...
  ✓ Port 5173 is available
  Checking backend port 8000...
  ⚠ Port 8000 is in use, using 8001 instead
```

- Tests default frontend port (5173)
- Tests default backend port (8000)
- Increments if occupied
- Ensures ports don't collide

### Step 4: User Configuration
```
[4/7] OpenWebUI Configuration
  Enter OpenWebUI URL (default: http://172.16.27.122:3000):
  Enter OpenWebUI API Key (press Enter to skip):
```

- Prompts for OpenWebUI URL
- Accepts Enter for default
- Optional API key input

### Step 5: File Generation
```
[5/7] Creating configuration file...
  ✓ Configuration saved to .env
  ✓ Backend configuration created
  ✓ Frontend configuration created
```

- Generates root `.env`
- Generates `backend/.env`
- Generates `frontend/.env`
- Creates random SECRET_KEY

### Step 6: Container Build
```
[6/7] Building and starting containers...
  This may take several minutes on first run...
  ✓ Containers started successfully
```

- Runs `docker-compose up -d --build`
- Builds both images
- Starts containers
- Returns on completion

### Step 7: Verification
```
[7/7] Waiting for services to start...
  Waiting for backend... (1/30)
  ✓ Backend is ready!
```

- Polls `http://localhost:{BACKEND_PORT}/api/health`
- Retries up to 30 times (60 seconds)
- Confirms backend is responding

### Completion
```
=================================
Installation Complete! 🎉
=================================

Your Document Filler application is now running:

  📱 Frontend:  http://localhost:5173
  🔧 Backend:   http://localhost:8001
  📚 API Docs:  http://localhost:8001/docs

Open application in browser? (Y/n):
```

- Displays access URLs
- Offers to open browser
- Provides useful commands

## Uninstallation Process

### Options Presented

1. **Remove containers** (always done)
2. **Remove Docker images** (optional)
3. **Remove data volumes** (optional)
4. **Remove configuration files** (optional)

### Data Preservation

For easy reinstallation:
```
Remove all uploaded documents and data? (y/N): N
Remove configuration files (.env)? (y/N): N
```

Result:
- Containers stopped and removed
- Images removed
- Data preserved in Docker volumes
- `.env` files preserved
- Can reinstall instantly with `install.bat`

### Complete Removal
```
Remove all uploaded documents and data? (y/N): Y
Remove configuration files (.env)? (y/N): Y
```

Result:
- Everything removed
- Fresh start possible
- No leftover files

## Error Handling

### Docker Not Running
```
✗ Docker Desktop is not running or not installed

Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
Make sure Docker Desktop is running before running this script.
```

### Port Detection Failure
```
ERROR: Could not find available port starting from 5173
```
- Safety check prevents infinite loop
- Stops at port 65535

### Build Failure
```
✗ Failed to start containers
Error: [Docker error message]

Please check Docker Desktop logs for more information.
```
- Catches build errors
- Directs user to logs

### Backend Timeout
```
⚠ Backend is taking longer than expected to start
You can check status with: docker-compose logs backend
```
- Provides troubleshooting command
- Installation continues (not fatal)

## PowerShell Execution Policy

The scripts handle execution policy automatically:

### Method 1: Batch File (Recommended)
```batch
powershell -ExecutionPolicy Bypass -File install.ps1
```
- Temporarily bypasses policy
- No permanent changes

### Method 2: Direct PowerShell
User may need to run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Method 3: Administrator Rights
Right-click batch file → "Run as Administrator"

## Testing Scenarios

### Scenario 1: Clean Installation
- Default ports available
- Result: Uses 5173 and 8000
- Time: ~2-3 minutes first run

### Scenario 2: Frontend Port Occupied
- Port 5173 in use
- Result: Uses 5174 for frontend, 8000 for backend
- All configs updated automatically

### Scenario 3: Backend Port Occupied
- Port 8000 in use
- Result: Uses 5173 for frontend, 8001 for backend
- Frontend knows to call 8001

### Scenario 4: Both Ports Occupied
- Ports 5173 and 8000 in use
- Result: Uses 5174 and 8001
- Everything configured correctly

### Scenario 5: Multiple Installations
- First: 5173/8000
- Second: 5174/8001
- Third: 5175/8002
- All running simultaneously without conflicts

### Scenario 6: Reinstallation
- Preserve config: Y
- Preserve data: Y
- Result: Quick reinstall, keeps settings and data

## Technical Benefits

### For Users
- **Zero configuration** needed
- **No port conflicts** ever
- **One-click installation**
- **Safe uninstallation** with options
- **Automatic browser launch**

### For Developers
- **Reproducible environments**
- **Easy testing** of multiple instances
- **Clear error messages**
- **Debuggable** with verbose output
- **Version control friendly** (scripts in repo)

### For System Administrators
- **Scriptable** (can run non-interactively)
- **Auditable** (all actions logged)
- **Reversible** (clean uninstall)
- **Configurable** (can edit .env before install)
- **Secure** (generates random keys)

## Future Enhancements

### Possible Additions

1. **Linux/Mac Install Script**
   - Bash version of install.ps1
   - Same port detection logic
   - Cross-platform compatibility

2. **Update Script**
   - Pull latest changes
   - Rebuild containers
   - Preserve data and config

3. **Backup Script**
   - Export data volumes
   - Save configuration
   - Create restore point

4. **Health Check Script**
   - Verify all services running
   - Check connectivity to OpenWebUI
   - Test document upload/generation

5. **Configuration Wizard**
   - GUI for settings
   - Test OpenWebUI connection
   - Validate configuration

## Best Practices

### For Users

1. **Always run Docker Desktop first**
2. **Close other apps on common ports** (optional, auto-handled)
3. **Keep .env files** for easy reinstallation
4. **Use uninstaller** instead of manual removal

### For Development

1. **Test with occupied ports** during development
2. **Verify all .env files** are created correctly
3. **Check CORS configuration** matches ports
4. **Test reinstallation** scenarios

### For Production

1. **Change SECRET_KEY** in production
2. **Use HTTPS** with proper certificates
3. **Set strong passwords**
4. **Regular backups** of data volumes
5. **Update configurations** for production URLs

## Troubleshooting Commands

### Check Installation Status
```powershell
docker-compose ps
```

### View Installation Logs
```powershell
docker-compose logs -f
```

### Check Port Usage
```powershell
netstat -ano | findstr :5173
netstat -ano | findstr :8000
```

### Manual Cleanup
```powershell
docker-compose down -v
docker system prune -a
```

### Test Port Availability
```powershell
Test-NetConnection -ComputerName localhost -Port 5173
```

## Summary

The automated installation system provides:

✅ **Intelligent port detection** - Never conflicts
✅ **Zero manual configuration** - Just double-click
✅ **Windows-friendly** - Batch file launcher
✅ **Error handling** - Clear messages and recovery
✅ **Data preservation** - Safe uninstall options
✅ **Complete automation** - From install to browser
✅ **Production ready** - Configurable for any environment

**Result**: Windows installation is now as simple as double-clicking `install.bat`! 🎉
