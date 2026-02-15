"""
XHS-Downloader 下载脚本模板

使用说明：
1. 将此脚本复制到 C:\Users\admin\download_xhs.py
2. 修改 URL 参数为目标作品链接
3. 运行：python C:\Users\admin\download_xhs.py
"""

import asyncio
import sys

# 添加 XHS-Downloader 路径
sys.path.insert(0, r"C:\Users\admin\Projects\XHS-Downloader")

from source import XHS


async def download_post(url: str, download: bool = True, index=None):
    """
    下载小红书作品

    Args:
        url: 小红书作品链接
        download: 是否下载文件（默认 True）
        index: 指定下载的图片序号列表（可选）

    Returns:
        作品信息字典
    """
    async with XHS() as xhs:
        result = await xhs.extract(url, download=download, index=index)
        return result


if __name__ == "__main__":
    # 配置参数
    URL = ""  # TODO: 在这里填入小红书作品URL

    # 解析命令行参数
    if len(sys.argv) > 1:
        URL = sys.argv[1]

    if not URL:
        print("请提供小红书作品URL")
        print("用法：python download_xhs.py <URL>")
        sys.exit(1)

    # 执行下载
    try:
        print(f"正在下载：{URL}")
        result = asyncio.run(download_post(URL, download=True))
        print("下载完成！")
        print(f"结果：{result}")
    except Exception as e:
        print(f"下载失败：{e}")
        sys.exit(1)
