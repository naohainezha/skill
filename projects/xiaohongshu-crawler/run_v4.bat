@echo off
chcp 65001 >nul
echo ========================================
echo   小红书爬虫 V4.0
echo   基于 xhs-crawler 改进版
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python not found
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] Installing dependencies...
pip install playwright python-dotenv pydantic rich slugify 2>nul

REM 安装浏览器
echo [2/3] Installing browser...
playwright install chromium

REM 运行V4
echo [3/3] Starting crawler V4.0...
echo.
echo Core strategies:
echo   - Simple but realistic environment
echo   - Sync Playwright
echo   - Smart scroll detection
echo   - Perfect error handling
echo.
python crawler_v4.py

echo.
echo Done!
pause
