@echo off
chcp 65001 >nul
cd /d "%~dp0"

if "%~1"=="" (
    echo 用法：search_xhs "关键词" [数量]
    echo 示例：search_xhs "眼镜" 10
    echo       search_xhs "眼镜,墨镜" 20
    exit /b 1
)

set KEYWORDS=%~1
if "%~2"=="" (
    set TARGET_COUNT=10
) else (
    set TARGET_COUNT=%~2
)

echo 🔍 小红书搜索
echo    关键词: %KEYWORDS%
echo    数量: %TARGET_COUNT%
echo ----------------------------------------

python crawler_v4.py

