#!/bin/bash

echo "========================================"
echo "  小红书爬虫 - 快速启动脚本"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查依赖
echo "[1/4] 检查依赖..."
if ! python3 -c "import playwright" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 安装浏览器
echo "[2/4] 检查Playwright浏览器..."
python3 -m playwright install chromium

# 运行爬虫
echo "[3/4] 启动爬虫..."
echo
python3 crawler_v2.py

echo
echo "[4/4] 完成！"
echo "输出文件保存在 output 目录中"
echo
