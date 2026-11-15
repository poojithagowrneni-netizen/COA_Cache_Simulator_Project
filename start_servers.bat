@echo off
title COA Cache Simulator Launcher
echo ========================================================
echo         COA Cache Simulator - Starting Services
echo ========================================================
echo.
cd /d "%~dp0cache_build\COA FRONTEND"

echo [1/2] Starting Flask Backend on http://127.0.0.1:5000 ...
start "COA Backend (Flask)" cmd /k ".venv\Scripts\python.exe backend\app.py"

echo [2/2] Starting Vite Frontend on http://localhost:5173 ...
start "COA Frontend (Vite)" cmd /k "npm.cmd run dev"

echo.
echo ========================================================
echo Both servers are starting up!
echo Frontend URL: http://localhost:5173
echo Backend API:  http://127.0.0.1:5000
echo ========================================================
echo.
ping 127.0.0.1 -n 4 >nul
start http://localhost:5173
