@echo off
REM Document Filler - Windows Uninstall Launcher
REM This script launches the PowerShell uninstall script

echo =========================================
echo Document Filler - Uninstall
echo =========================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available on this system.
    echo Please install PowerShell or run uninstall.ps1 directly.
    pause
    exit /b 1
)

REM Run the PowerShell script
echo Starting uninstall...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Uninstall failed. Please check the error messages above.
    pause
    exit /b 1
)

exit /b 0
