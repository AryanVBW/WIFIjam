@echo off
REM Quick start script for WIFIjam on Windows

echo.
echo ╦ ╦╦╔═╗╦ ╦┌─┐┌┬┐
echo ║║║║╠╣ ║ ║├─┤│││
echo ╚╩╝╩╚  ╩ ╩┴ ┴┴ ┴
echo WiFi Security Testing Tool v2.0
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [INFO] Checking dependencies...

REM Check if dependencies are installed
python -c "import aiohttp" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo [INFO] Starting WIFIjam...
echo [WARNING] Windows has limited support. Use WSL2 for full functionality.
echo.

REM Run the application
python -m wifijam.cli gui %*

pause

