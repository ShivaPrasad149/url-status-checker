@echo off
chcp 65001 > nul
echo ========================================
echo 📦 Push to Docker Hub - URL Status Checker
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

echo 📝 Instructions:
echo 1. Make sure you have a Docker Hub account
echo 2. Replace "yourusername" with your actual Docker Hub username
echo 3. You will be prompted to login to Docker Hub
echo.

set /p DOCKER_USERNAME="shivaprasad149"

if "%DOCKER_USERNAME%"=="" (
    echo ❌ ERROR: Username cannot be empty!
    pause
    exit /b 1
)

echo.
echo 🔑 Logging in to Docker Hub...
docker login

if errorlevel 1 (
    echo ❌ ERROR: Docker login failed!
    pause
    exit /b 1
)

echo.
echo 🔨 Rebuilding image with Docker Hub tag...
cd ..\app
docker build -t %DOCKER_USERNAME%/url-status-checker:latest .

if errorlevel 1 (
    echo ❌ ERROR: Docker build failed!
    pause
    exit /b 1
)

echo.
echo 📤 Pushing image to Docker Hub...
docker push %DOCKER_USERNAME%/url-status-checker:latest

if errorlevel 1 (
    echo ❌ ERROR: Docker push failed!
    pause
    exit /b 1
)

echo.
echo ✅ Successfully pushed to Docker Hub!
echo 📍 Your image is available at: https://hub.docker.com/r/%DOCKER_USERNAME%/url-status-checker
echo.
echo 💡 You can now run your app anywhere using:
echo    docker run -p 5000:5000 %DOCKER_USERNAME%/url-status-checker:latest
echo.

pause