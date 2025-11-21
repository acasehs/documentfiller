# Document Filler - Windows Installation Guide

## Automated Installation (Recommended)

### Quick Start

1. **Ensure Docker Desktop is running**
   - Download from: https://www.docker.com/products/docker-desktop
   - Make sure Docker Desktop is started before installation

2. **Run the installer**
   - Double-click `install.bat` in the project folder
   - OR right-click `install.bat` and select "Run as Administrator"
   - OR open PowerShell and run: `.\install.ps1`

3. **Follow the prompts**
   - The installer will automatically detect available ports
   - Enter your OpenWebUI URL (or press Enter for default)
   - Enter your OpenWebUI API key (optional)
   - Wait for containers to build and start

4. **Access your application**
   - Frontend will open automatically in your browser
   - Or navigate to the URL shown (e.g., http://localhost:5173)

### What the Installer Does

The automated installer handles everything for you:

✅ **Port Detection**: Automatically finds available ports
  - Starts with defaults (5173 for frontend, 8000 for backend)
  - If occupied, increments to find free ports
  - Ensures frontend and backend use different ports

✅ **Configuration**: Creates `.env` files with correct settings
  - Root `.env` for Docker Compose
  - `backend/.env` for backend configuration
  - `frontend/.env` for frontend API URL
  - Generates secure random secret key

✅ **Docker Setup**: Builds and starts containers
  - Pulls required images
  - Builds custom images with your configuration
  - Starts services with correct port mappings
  - Waits for services to be ready

✅ **Verification**: Checks that services are running
  - Tests backend health endpoint
  - Confirms containers are up
  - Reports any issues

### Installation Output

```
=================================
Document Filler - Installation
=================================

[1/7] Checking Docker Desktop...
  ✓ Docker is installed: Docker version 24.0.6

[2/7] Checking Docker Compose...
  ✓ Docker Compose detected

[3/7] Detecting available ports...
  Checking frontend port 5173...
  ✓ Port 5173 is available
  Checking backend port 8000...
  ⚠ Port 8000 is in use, using 8001 instead

[4/7] OpenWebUI Configuration
  Enter OpenWebUI URL (default: http://172.16.27.122:3000):
  Enter OpenWebUI API Key (press Enter to skip):

[5/7] Creating configuration file...
  ✓ Configuration saved to .env
  ✓ Backend configuration created
  ✓ Frontend configuration created

[6/7] Building and starting containers...
  This may take several minutes on first run...
  ✓ Containers started successfully

[7/7] Waiting for services to start...
  ✓ Backend is ready!

=================================
Installation Complete! 🎉
=================================

Your Document Filler application is now running:

  📱 Frontend:  http://localhost:5173
  🔧 Backend:   http://localhost:8001
  📚 API Docs:  http://localhost:8001/docs

Configuration saved in .env file
```

## Port Conflict Resolution

### Automatic Handling

The installer automatically handles port conflicts:

- **Default Ports**: 5173 (frontend), 8000 (backend)
- **If Occupied**: Automatically increments to next available port
- **Ensures Separation**: Frontend and backend always use different ports
- **Updates Configuration**: All references updated automatically

### Example Scenarios

**Scenario 1: Port 8000 occupied**
```
Backend port 8000 in use → switches to 8001
Frontend uses 5173 (available)
Frontend configured to call http://localhost:8001
```

**Scenario 2: Both ports occupied**
```
Frontend port 5173 in use → switches to 5174
Backend port 8000 in use → switches to 8001
All configurations updated accordingly
```

**Scenario 3: Multiple installations**
```
First install: Frontend 5173, Backend 8000
Second install: Frontend 5174, Backend 8001
Third install: Frontend 5175, Backend 8002
```

### Manual Port Configuration

If you want to use specific ports:

1. Edit `.env` before running install:
   ```env
   FRONTEND_PORT=8080
   BACKEND_PORT=9000
   ```

2. Run the installer - it will detect if your chosen ports are occupied

## Uninstallation

### Automated Uninstall

1. **Run the uninstaller**
   - Double-click `uninstall.bat`
   - OR run: `.\uninstall.ps1` in PowerShell

2. **Choose what to remove**
   - Containers (always removed)
   - Docker images (optional)
   - Uploaded documents and data (optional)
   - Configuration files (optional)

### Uninstall Options

```
=================================
Document Filler - Uninstall
=================================

Are you sure you want to uninstall Document Filler? (y/N): y

This will:
  - Stop and remove containers
  - Remove Docker images
  - Optionally remove uploaded documents and data

Remove all uploaded documents and data? (y/N): n

[1/4] Stopping containers...
  ✓ Containers stopped

[2/4] Removing containers...
  ✓ Containers removed (data preserved)

[3/4] Removing Docker images...
  ✓ Docker images removed

[4/4] Cleaning up configuration files...
Remove configuration files (.env)? (y/N): n
  ℹ Configuration files preserved

=================================
Uninstall Complete!
=================================
```

### Partial Uninstall

To keep your data for reinstallation:
- Choose "N" when asked about removing data
- Choose "N" when asked about removing configuration

To completely remove everything:
- Choose "Y" for all prompts
- This deletes all documents, data, and configuration

## Troubleshooting

### Docker Desktop Not Running

**Error:**
```
✗ Docker Desktop is not running or not installed
```

**Solution:**
1. Start Docker Desktop
2. Wait for it to fully initialize (whale icon stops animating)
3. Run installer again

### Port Already in Use (Manual Override)

If you need to use a specific port that's occupied:

1. Stop the application using that port
2. Run the installer
3. Or edit `.env` manually and rebuild:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Installation Hangs

**If installation seems stuck:**

1. Check Docker Desktop is running
2. Check Docker Desktop resources (CPU/Memory)
3. Cancel (Ctrl+C) and run again
4. Check logs: `docker-compose logs`

### Backend Not Ready

**If installer reports backend timeout:**

```
⚠ Backend is taking longer than expected to start
You can check status with: docker-compose logs backend
```

**Solutions:**
1. Wait a bit longer - first build can take time
2. Check logs: `docker-compose logs backend`
3. Verify `.env` file was created correctly
4. Ensure OpenWebUI URL is accessible

### Permission Errors

**Error:** Access denied or permission errors

**Solution:**
1. Run as Administrator:
   - Right-click `install.bat`
   - Select "Run as Administrator"
2. Or in PowerShell (Admin):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   .\install.ps1
   ```

### PowerShell Execution Policy

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Option 1: Run with bypass (one-time)
powershell -ExecutionPolicy Bypass -File install.ps1

# Option 2: Change policy (permanent)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Manual Installation (Alternative)

If you prefer manual installation or automated scripts don't work:

### Step 1: Create `.env` file

```env
FRONTEND_PORT=5173
BACKEND_PORT=8000
OPENWEBUI_BASE_URL=http://172.16.27.122:3000
OPENWEBUI_API_KEY=your-key-here
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
SECRET_KEY=your-secret-key-here
```

### Step 2: Start containers

```bash
docker-compose up -d --build
```

### Step 3: Access application

- Frontend: http://localhost:5173
- Backend: http://localhost:8000/docs

## Useful Commands

### Check Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart backend only
docker-compose restart backend
```

### Stop Services
```bash
docker-compose stop
```

### Start Stopped Services
```bash
docker-compose start
```

### Rebuild After Changes
```bash
docker-compose down
docker-compose up -d --build
```

## Upgrading

To upgrade to a new version:

1. Pull latest code:
   ```bash
   git pull
   ```

2. Run installer again:
   ```bash
   .\install.bat
   ```

   OR manually rebuild:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

Your data and configuration will be preserved.

## System Requirements

### Minimum
- Windows 10 64-bit or Windows 11
- 4 GB RAM
- 10 GB free disk space
- Docker Desktop 4.0+

### Recommended
- Windows 11
- 8 GB RAM
- 20 GB free disk space
- Docker Desktop (latest version)
- Fast internet for first-time container downloads

## Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Check Docker Desktop**: Look for errors in Docker Desktop dashboard
3. **Verify configuration**: Ensure `.env` files exist and are correct
4. **Test OpenWebUI**: Verify OpenWebUI is accessible from your machine
5. **Restart Docker Desktop**: Sometimes helps resolve issues

## Security Notes

### Development vs Production

The installer creates a **development configuration** suitable for:
- Local development
- Single-user testing
- Evaluation

### For Production Use

If deploying to production, you should:

1. **Change the SECRET_KEY** in `.env`
2. **Use HTTPS** with proper certificates
3. **Set strong passwords** for any authentication
4. **Restrict CORS origins** to your actual domain
5. **Configure firewall rules** appropriately
6. **Regular backups** of data volumes
7. **Keep Docker and images updated**

## Next Steps

After installation:

1. **Configure OpenWebUI** in Settings page
2. **Upload a test document** to verify functionality
3. **Generate content** for a section
4. **Explore features** (review, tense analysis, etc.)
5. **Read documentation** in README_WEB.md

Enjoy using Document Filler! 🎉
