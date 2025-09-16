#!/bin/bash

# MediaMaestro Startup Script
# This script starts both backend and frontend in desktop application mode

echo "🎵 Starting MediaMaestro..."

# Check if we're in the correct directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the MediaMaestro root directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on specific ports
cleanup() {
    echo "🧹 Cleaning up processes..."
    if check_port 8000; then
        echo "Stopping backend server on port 8000..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    fi
    if check_port 3000; then
        echo "Stopping frontend server on port 3000..."
        lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    fi
}

# Handle script termination
trap cleanup EXIT INT TERM

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed or not in PATH"
    exit 1
fi

# Create logs directory
mkdir -p logs

echo "🔧 Checking dependencies..."

# Check and install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install Python dependencies
pip install -q -r requirements.txt

cd ..

# Check and install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install --silent
fi
cd ..

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating default .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Spotify API credentials"
fi

echo "🚀 Starting services..."

# Start backend
echo "Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
$PYTHON_CMD main.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if check_port 8000; then
        echo "✅ Backend started successfully on port 8000"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs/backend.log for details."
        exit 1
    fi
done

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
for i in {1..30}; do
    if check_port 3000; then
        echo "✅ Frontend started successfully on port 3000"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start. Check logs/frontend.log for details."
        exit 1
    fi
done

echo ""
echo "🎉 MediaMaestro is now running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs are saved in the logs/ directory"
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Try to open browser (cross-platform)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000 >/dev/null 2>&1 &
elif command -v open > /dev/null; then
    open http://localhost:3000 >/dev/null 2>&1 &
elif command -v start > /dev/null; then
    start http://localhost:3000 >/dev/null 2>&1 &
fi

# Keep the script running and monitor processes
while true; do
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend process died unexpectedly"
        break
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend process died unexpectedly"
        break
    fi
    
    sleep 5
done

echo "🛑 MediaMaestro stopped"