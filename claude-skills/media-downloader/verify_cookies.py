#!/usr/bin/env python3
"""
YouTube Cookies 更新指南
========================

YouTube 会频繁轮换登录 cookies 作为安全措施。
必须按照以下步骤正确导出才能长期使用：

1. 打开浏览器的 **隐私窗口/无痕模式**
2. 在隐私窗口中登录 YouTube (https://www.youtube.com)
3. 登录成功后，在同一窗口访问: https://www.youtube.com/robots.txt
   - 重要: 确保只有这一个标签页打开！
4. 使用浏览器扩展导出 cookies:
   - Chrome: Get cookies.txt LOCALLY
   - Firefox: cookies.txt
5. 保存到: ~/.claude/skills/media-downloader/cookies.txt
6. **立即关闭隐私窗口** (永不再打开该会话)

为什么这样做？
- YouTube 在检测到 cookies 被使用时会轮换它们
- 隐私窗口的 cookies 与普通窗口隔离
- 关闭窗口后，该会话不会被触发轮换

运行此脚本验证 cookies 是否有效:
python verify_cookies.py
"""

import os
import subprocess
import sys

COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

def verify_cookies():
    """验证 cookies 是否有效"""
    if not os.path.exists(COOKIES_FILE):
        print("❌ cookies.txt 文件不存在")
        print("请按照上述步骤导出 cookies")
        return False
    
    # 检查文件修改时间
    import time
    mtime = os.path.getmtime(COOKIES_FILE)
    age_hours = (time.time() - mtime) / 3600
    print(f"📄 Cookies 文件年龄: {age_hours:.1f} 小时")
    
    if age_hours > 24:
        print("⚠️ Cookies 可能已过期 (超过 24 小时)")
    
    # 测试下载一个简短的公开视频
    print("\n🔍 测试 YouTube 连接...")
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Me at the zoo - 第一个 YouTube 视频
    
    cmd = [
        'yt-dlp',
        '--cookies', COOKIES_FILE,
        '--js-runtimes', 'node',
        '--dump-json',
        '--no-download',
        test_url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and '"title"' in result.stdout:
            print("✅ Cookies 有效！可以正常下载 YouTube 视频")
            return True
        elif "Sign in to confirm" in result.stderr:
            print("❌ Cookies 已失效，请重新导出")
            print("\n按照脚本顶部的步骤重新导出 cookies")
            return False
        else:
            print(f"⚠️ 未知状态: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except FileNotFoundError:
        print("❌ yt-dlp 未安装，请运行: pip install yt-dlp")
        return False

if __name__ == "__main__":
    print(__doc__)
    print("=" * 60)
    verify_cookies()
