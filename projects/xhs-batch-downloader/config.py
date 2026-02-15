"""
小红书博主笔记批量下载器 - 配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据库路径
DATABASE_PATH = PROJECT_ROOT / "data" / "bloggers.db"

# XHS-Downloader 路径 (从 Projects 目录引用)
XHS_DOWNLOADER_PATH = Path(r"C:\Users\admin\Projects\XHS-Downloader")

# XHS-Downloader 下载记录数据库
XHS_EXPLORE_ID_DB = XHS_DOWNLOADER_PATH / "Volume" / "ExploreID.db"

# 下载目录
DOWNLOAD_DIR = XHS_DOWNLOADER_PATH / "Volume" / "Download"

# 签名服务配置 (Docker: reajason/xhs-api)
SIGN_SERVER_HOST = "http://127.0.0.1"
SIGN_SERVER_PORT = 5005

# 默认下载数量
DEFAULT_DOWNLOAD_COUNT = 10

# 请求间隔（秒），避免触发风控
REQUEST_INTERVAL = 2


# Cookie 配置（从多个来源尝试读取）
def get_cookie():
    """从多个来源尝试读取 Cookie"""
    import json

    # 来源1：XHS-Downloader 的 settings.json
    settings_path = XHS_DOWNLOADER_PATH / "Volume" / "settings.json"
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8-sig") as f:
            settings = json.load(f)
            cookie = settings.get("cookie", "")
            if cookie:
                return cookie

    # 来源2：用户目录下的 cookies.json（浏览器导出格式）
    cookies_json_path = Path(
        r"C:\Users\admin\Projects\xhs-batch-downloader\cookies.json"
    )
    if cookies_json_path.exists():
        with open(cookies_json_path, "r", encoding="utf-8-sig") as f:
            cookies = json.load(f)
            # 转换为 cookie 字符串格式
            xhs_cookies = [
                c for c in cookies if "xiaohongshu.com" in c.get("domain", "")
            ]
            if xhs_cookies:
                return "; ".join([f"{c['name']}={c['value']}" for c in xhs_cookies])

    return ""
    return ""


# 确保数据目录存在
def ensure_dirs():
    """确保必要的目录存在"""
    (PROJECT_ROOT / "data").mkdir(parents=True, exist_ok=True)


ensure_dirs()
