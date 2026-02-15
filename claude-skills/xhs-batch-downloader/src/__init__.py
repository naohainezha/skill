"""
小红书博主笔记批量下载器
XHS Batch Downloader
"""

__version__ = "1.0.0"
__author__ = "OpenCode"
__description__ = "小红书博主笔记批量下载器"

from .cli import cli
from .xhs_client import xhs_client, SignServerError
from .database import db, Blogger

__all__ = [
    "cli",
    "xhs_client",
    "SignServerError",
    "db",
    "Blogger",
]
