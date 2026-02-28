@echo off
REM ============================================================
REM AI Freelancing Agency - Production Start Script (Windows)
REM ============================================================

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║    AI Freelancing Automation Agency              ║
echo  ║    Production Mode Startup                       ║
echo  ╚══════════════════════════════════════════════════╝
echo.

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH. Please install Python 3.10+
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Initialize database tables
echo [1/3] Initializing database...
python -m backend.db.init_db
if errorlevel 1 (
    echo [WARN] Database init had issues, continuing...
)

echo.
echo [2/3] Starting FastAPI Backend on http://localhost:8000
echo        API Docs: http://localhost:8000/docs
echo.
start "AI Freelancing - Backend" cmd /k "python -m gunicorn backend.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --log-level info"

timeout /t 4 /nobreak >nul

echo [3/3] Starting Streamlit Dashboard on http://localhost:8501
echo.
start "AI Freelancing - Frontend" cmd /k "python -m streamlit run frontend/dashboard.py --server.port 8501"

echo.
echo  ════════════════════════════════════════════════════
echo  ✅ Services started!
echo    Backend  →  http://localhost:8000
echo    Frontend →  http://localhost:8501
echo  ════════════════════════════════════════════════════
echo.
echo  Close the opened terminals to stop the services.
echo.
pause
