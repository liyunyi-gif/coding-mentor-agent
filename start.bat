@echo off
chcp 65001 >nul

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

REM === .env check ===
if not exist "%PROJECT_ROOT%.env" (
    echo [WARN] .env not found, please configure AI_API_KEY
)

REM === Python dependencies ===
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing Python dependencies...
    pip install -r "%PROJECT_ROOT%requirements.txt"
    if %errorlevel% neq 0 (
        pause
        exit /b 1
    )
)

REM === Frontend build ===
cd /d "%PROJECT_ROOT%front"
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARN] Node.js not found, using pre-built frontend if available
) else (
    if not exist "node_modules\" (
        echo [INFO] Installing frontend dependencies...
        call npm install
    )
    echo [INFO] Building frontend...
    call npm run build
    if %errorlevel% neq 0 (
        echo [WARN] Frontend build failed, falling back to old static/
    )
)
cd /d "%PROJECT_ROOT%"

REM === Start ===
start http://127.0.0.1:8080
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080
