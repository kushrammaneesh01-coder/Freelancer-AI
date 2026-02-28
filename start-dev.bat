@echo off
REM ============================================================
REM AI Freelancing Agency - Development Start Script (Windows)
REM ============================================================

echo.
echo  Starting in DEVELOPMENT mode (with hot-reload)...
echo.

if not exist "logs" mkdir logs

echo [1/2] Starting FastAPI Backend (reload mode)...
start "API Backend - Dev" cmd /k "python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit Frontend...
start "Streamlit - Dev" cmd /k "python -m streamlit run frontend/dashboard.py --server.port 8501"

echo.
echo  Backend  → http://localhost:8000/docs
echo  Frontend → http://localhost:8501
echo.
pause
