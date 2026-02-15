#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速测试脚本 - 验证修复"""
import sys
import io

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("  V4.0 修复验证")
print("=" * 60)
print()

# 测试1: 导入模块
print("[1/3] 导入模块...")
try:
    import crawler_v4
    print("      ✓ 导入成功")
except NameError as e:
    print(f"      ✗ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"      ✗ 其他错误: {e}")
    sys.exit(1)

# 测试2: 检查SETTINGS
print("[2/3] 检查SETTINGS...")
try:
    print(f"      SETTINGS.keywords = {crawler_v4.SETTINGS.keywords}")
    print(f"      SETTINGS.target_count = {crawler_v4.SETTINGS.target_count}")
    print(f"      SETTINGS.cookies_file = {crawler_v4.SETTINGS.cookies_file}")
except Exception as e:
    print(f"      ✗ 错误: {e}")
    sys.exit(1)

# 测试3: 检查get_cookies_path
print("[3/3] 检查get_cookies_path...")
try:
    cookies_path = crawler_v4.get_cookies_path()
    print(f"      get_cookies_path() = {cookies_path}")
except Exception as e:
    print(f"      ✗ 错误: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✓ 所有测试通过！可以运行爬虫")
print("=" * 60)
print()
print("启动命令：")
print("  python crawler_v4.py")
print()
print("或双击：start_v4.py")
