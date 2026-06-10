@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Coding Mentor Agent - Python 课程学伴
echo ========================================
echo.

REM 检查 .env 是否存在
if not exist ".env" (
    echo [WARN] 未找到 .env 文件，请先复制 .env.example 并填入配置
    echo   copy .env.example .env
    echo.
)

REM 检查依赖
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 正在安装依赖...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装失败
        pause
        exit /b 1
    )
    echo.
)

echo [INFO] 启动服务器 http://127.0.0.1:8080
echo [INFO] 按 Ctrl+C 停止
echo.

python -m uvicorn src.main:app --host 127.0.0.1 --port 8080

pause
