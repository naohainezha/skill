@echo off
chcp 65001 >nul
echo ========================================
echo   小红书爬虫 V3.0 - 深度人工模拟版
echo   使用更逼真的人类行为，避免反爬
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo [1/4] 检查依赖...
pip show playwright >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

REM 安装浏览器
echo [2/4] 检查Playwright浏览器...
playwright install chromium

REM 运行V3爬虫（推荐）
echo [3/4] 启动V3爬虫（深度人工模拟）...
echo.
echo 提示：V3版本使用更逼真的人类行为模拟
echo      可以有效避免触发小红书的反爬机制
echo.
python crawler_v3.py

echo.
echo [4/4] 完成！
echo 输出文件保存在 output 目录中
echo.
pause
