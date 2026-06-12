@echo off
chcp 65001 >nul

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
set "PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%"

if not exist "%PROJECT_ROOT%.env" (
    echo [WARN] .env 文件不存在，请先复制 .env.example 并填入配置
)

python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    pip install -r "%PROJECT_ROOT%requirements.txt"
    if %errorlevel% neq 0 (
        pause
        exit /b 1
    )
)

start http://127.0.0.1:8080
python -m uvicorn src.main:app --host 127.0.0.1 --port 8080
