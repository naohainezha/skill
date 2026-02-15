@echo off
chcp 65001 >nul
echo ========================================
echo   Xiaohongshu Crawler V3.0
echo ========================================
echo.

echo [1/3] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [2/3] Checking dependencies...
pip show playwright >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo [3/3] Installing Playwright browser...
playwright install chromium

echo.
echo Starting crawler V3.0...
python crawler_v3.py

echo.
echo Done! Check output folder for results.
echo.
pause
