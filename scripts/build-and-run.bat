@echo off
chcp 65001 > nul
echo ========================================
echo 🐳 Docker Build & Run - URL Status Checker
echo ========================================
echo.

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Navigate to app directory
cd ..\app

echo 🔨 Building Docker image...
docker build -t url-status-checker:latest .

if errorlevel 1 (
    echo ❌ ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo ✅ Docker image built successfully!
echo.

echo 🚀 Starting container...
echo 📍 Application will be available at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop the container
echo.

REM Run the container
docker run -it --rm -p 5000:5000 --name url-checker-container url-status-checker:latest