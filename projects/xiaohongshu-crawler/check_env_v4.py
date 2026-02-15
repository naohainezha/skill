#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""环境测试脚本 - 诊断启动问题"""
import sys
import subprocess
import io

# 设置UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("  小红书爬虫 V4.0 - 环境诊断")
print("=" * 60)
print()

# 测试1: Python版本
print("[1/6] 检查Python版本...")
print(f"      Python版本: {sys.version.split()[0]}")
print(f"      Python路径: {sys.executable}")
print(f"      平台: {sys.platform}")
if sys.version_info >= (3, 8):
    print("      ✓ Python版本符合要求 (3.8+)")
else:
    print("      ✗ Python版本过低，需要3.8+")
print()

# 测试2: 模块检查
print("[2/6] 检查必需模块...")
modules = {
    'playwright': 'Playwright',
    'dotenv': 'python-dotenv',
    'pydantic': 'pydantic',
    'rich': 'rich',
    'slugify': 'slugify'
}

all_ok = True
for module, name in modules.items():
    try:
        __import__(module)
        print(f"      ✓ {name} 已安装")
    except ImportError:
        print(f"      ✗ {name} 未安装")
        all_ok = False
print()

# 测试3: Playwright浏览器
print("[3/6] 检查Playwright浏览器...")
try:
    from playwright.sync_api import sync_playwright
    print("      ✓ Playwright 模块正常")
except Exception as e:
    print(f"      ✗ Playwright 错误: {e}")
    all_ok = False
print()

# 测试4: 文件检查
import os
print("[4/6] 检查必需文件...")
files = {
    'crawler_v4.py': '主程序',
    '.env': '配置文件',
    'requirements_refined.txt': '依赖列表'
}

for filename, desc in files.items():
    if os.path.exists(filename):
        print(f"      ✓ {desc} ({filename})")
    else:
        print(f"      ✗ {desc} ({filename}) 不存在")
        all_ok = False
print()

# 测试5: 目录检查
print("[5/6] 检查目录结构...")
dirs = ['output', 'output/debug']
for dirname in dirs:
    if os.path.exists(dirname):
        print(f"      ✓ {dirname} 目录存在")
    else:
        print(f"      ⚠ {dirname} 目录不存在（会自动创建）")
print()

# 测试6: 语法检查
print("[6/6] 检查代码语法...")
try:
    subprocess.check_call([sys.executable, '-m', 'py_compile', 'crawler_v4.py'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("      ✓ crawler_v4.py 语法正确")
except subprocess.CalledProcessError:
    print("      ✗ crawler_v4.py 语法错误")
    all_ok = False
except Exception as e:
    print(f"      ⚠ 检查失败: {e}")
print()

# 总结
print("=" * 60)
if all_ok:
    print("✓ 环境检查通过！可以运行爬虫")
    print()
    print("启动命令：")
    print("  python crawler_v4.py")
    print()
    print("或双击：start_v4.py")
else:
    print("✗ 环境检查失败，请修复上述问题")
    print()
    print("安装依赖：")
    print("  pip install -r requirements_refined.txt")
    print("  playwright install chromium")
print("=" * 60)
print()

# 询问是否直接运行
if all_ok:
    try:
        choice = input("是否现在运行爬虫？(y/n): ").strip().lower()
        if choice == 'y':
            print()
            print("启动爬虫...")
            print("=" * 60)
            subprocess.call([sys.executable, 'crawler_v4.py'])
        else:
            print("已取消")
    except KeyboardInterrupt:
        print("\n已取消")
    except Exception as e:
        print(f"询问时出错: {e}")
