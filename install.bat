@echo off
REM Document Filler - Windows Installation Launcher
REM This script launches the PowerShell installation script

echo =========================================
echo Document Filler - Installation
echo =========================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available on this system.
    echo Please install PowerShell or run install.ps1 directly.
    pause
    exit /b 1
)

REM Check if running as Administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Not running as Administrator.
    echo Some Docker operations may require elevated privileges.
    echo.
    echo Right-click this file and select "Run as Administrator" if you encounter issues.
    echo.
    pause
)

REM Run the PowerShell script
echo Starting installation...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Installation failed. Please check the error messages above.
    pause
    exit /b 1
)

exit /b 0
