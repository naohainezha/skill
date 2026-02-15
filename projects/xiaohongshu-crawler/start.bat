@echo off
echo Xiaohongshu Crawler V3.0
echo ============================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    pause
    exit /b 1
)

pip show playwright >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Installing browser...
playwright install chromium

echo.
echo Starting crawler...
python crawler_v3.py

echo.
echo Done!
pause
