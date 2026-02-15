#!/bin/bash
# XHS Batch Downloader Skill 安装脚本

set -e

echo "=========================================="
echo "小红书批量下载器 Skill 安装程序"
echo "=========================================="

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$PROJECT_ROOT/src"

echo ""
echo "项目路径: $PROJECT_ROOT"

# 检查 Python
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python 3.8+"
    exit 1
fi

echo "Python 版本: $(python --version)"

# 检查 pip
if ! command -v pip &> /dev/null; then
    echo "错误: 未找到 pip，请先安装 pip"
    exit 1
fi

# 安装依赖
echo ""
echo "正在安装依赖..."
pip install -q playwright httpx click rich

# 安装 Playwright 浏览器
echo ""
echo "正在安装 Playwright 浏览器..."
playwright install chromium

# 创建命令别名（可选）
echo ""
echo "是否创建快捷命令 'xhs-download'? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    # 检测 shell
    if [[ "$SHELL" == *"zsh"* ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.bashrc"
    fi
    
    # 添加别名
    echo "alias xhs-download='python -m $SRC_DIR'" >> "$SHELL_RC"
    echo "快捷命令已添加到 $SHELL_RC"
    echo "请运行 'source $SHELL_RC' 或重新打开终端以生效"
fi

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "使用方法:"
echo "  1. 登录:    python -m $SRC_DIR login"
echo "  2. 添加博主: python -m $SRC_DIR add <博主ID>"
echo "  3. 下载:    python -m $SRC_DIR download <博主ID> --count 10"
echo "  4. 查看列表: python -m $SRC_DIR list"
echo ""
echo "详细文档: $PROJECT_ROOT/SKILL.md"
echo ""
