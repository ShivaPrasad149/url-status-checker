@echo off
chcp 65001 > nul
echo ========================================
echo 🚀 URL Status Checker - Phase 1
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "app\requirements.txt" (
    echo ❌ ERROR: Please run this script from the project root directory
    echo Current directory should contain 'app' folder and 'run-app.bat'
    pause
    exit /b 1
)

echo ✅ Python is installed
echo 📦 Installing dependencies...

REM Install Python dependencies
cd app
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ✅ Dependencies installed successfully!
echo.
echo 🎯 Starting the URL Status Checker...
echo.
echo 📍 Access your dashboard at: http://localhost:5000
echo 📊 API endpoints available at: http://localhost:5000/api
echo 🛑 Press Ctrl+C to stop the application
echo.

REM Run the application
python app.py


pause
