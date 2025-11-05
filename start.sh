#!/bin/bash

# Zeit Erfassung Startup Script
# Kills processes on ports 8000 and 3000, then starts backend and frontend

echo "🔄 Zeit Erfassung - Starting servers..."
echo ""

# Kill existing processes on ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "   ✓ Killed process on port 8000"
lsof -ti:3000 | xargs kill -9 2>/dev/null && echo "   ✓ Killed process on port 3000"
pkill -f "uvicorn" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 2

# Start backend
echo ""
echo "🚀 Starting backend on port 8000..."
cd backend
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🚀 Starting frontend on port 3000..."
cd frontend
PORT=3000 npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started successfully!"
echo ""
echo "📍 Backend:  http://localhost:8000"
echo "📍 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait
