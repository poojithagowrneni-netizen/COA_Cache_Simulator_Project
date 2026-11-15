#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/cache_build/COA FRONTEND"

echo "========================================================"
echo "        COA Cache Simulator - Starting Services"
echo "========================================================"
echo ""

# Ensure venv exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r backend/requirements.txt
fi

# Ensure node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "[1/2] Starting Flask Backend on http://127.0.0.1:5000 ..."
.venv/bin/python backend/app.py &
BACKEND_PID=$!

echo "[2/2] Starting Vite Frontend on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill "$BACKEND_PID" 2>/dev/null || true
    kill "$FRONTEND_PID" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

echo ""
echo "========================================================"
echo "Both servers are running!"
echo "Frontend URL: http://localhost:5173"
echo "Backend API:  http://127.0.0.1:5000"
echo "Press Ctrl+C to stop both servers."
echo "========================================================"

wait

