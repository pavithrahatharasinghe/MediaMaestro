@echo off
setlocal enabledelayedexpansion

echo.
echo 🎵 Starting MediaMaestro...
echo.

REM Check if we're in the correct directory
if not exist "backend\main.py" (
    echo ❌ Error: Please run this script from the MediaMaestro root directory
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo ❌ Error: Please run this script from the MediaMaestro root directory
    pause
    exit /b 1
)

REM Check if Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if npm is available
where npm >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: npm is not installed or not in PATH
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

echo 🔧 Checking dependencies...

REM Check and install Python dependencies
echo 📦 Installing Python dependencies...
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

cd ..

REM Check and install Node.js dependencies
echo 📦 Installing Node.js dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    npm install --silent
)
cd ..

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️  Creating default .env file...
    copy .env.example .env
    echo 📝 Please edit .env file with your Spotify API credentials
)

echo.
echo 🚀 Starting services...

REM Start backend
echo Starting backend server...
cd backend
call venv\Scripts\activate.bat
start /b python main.py > ..\logs\backend.log 2>&1
cd ..

REM Wait for backend to start
echo ⏳ Waiting for backend to start...
timeout /t 10 /nobreak >nul

REM Start frontend
echo Starting frontend server...
cd frontend
start /b npm run dev > ..\logs\frontend.log 2>&1
cd ..

REM Wait for frontend to start
echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo 🎉 MediaMaestro is now running!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo.
echo 📝 Logs are saved in the logs\ directory
echo 🛑 Press any key to stop all services
echo.

REM Try to open browser
start http://localhost:3000

REM Wait for user input to stop
pause >nul

REM Cleanup
echo.
echo 🧹 Stopping services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo 🛑 MediaMaestro stopped
pause