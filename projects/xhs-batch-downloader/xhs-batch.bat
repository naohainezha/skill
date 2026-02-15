@echo off
REM 小红书博主笔记批量下载器启动脚本

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.12+
    pause
    exit /b 1
)

REM 运行 CLI
python cli.py %*
