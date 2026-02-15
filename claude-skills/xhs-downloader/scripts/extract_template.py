"""
XHS-Downloader 作品信息提取脚本模板

使用说明：
1. 将此脚本复制到 C:\Users\admin\extract_xhs.py
2. 修改 URL 参数为目标作品链接
3. 运行：python C:\Users\admin\extract_xhs.py
"""

import asyncio
import sys

# 添加 XHS-Downloader 路径
sys.path.insert(0, r"C:\Users\admin\Projects\XHS-Downloader")

from source import XHS


async def extract_post(url: str):
    """
    提取小红书作品信息（不下载文件）

    Args:
        url: 小红书作品链接

    Returns:
        作品信息字典
    """
    async with XHS() as xhs:
        result = await xhs.extract(url, download=False)
        return result


if __name__ == "__main__":
    # 配置参数
    URL = ""  # TODO: 在这里填入小红书作品URL

    # 解析命令行参数
    if len(sys.argv) > 1:
        URL = sys.argv[1]

    if not URL:
        print("请提供小红书作品URL")
        print("用法：python extract_xhs.py <URL>")
        sys.exit(1)

    # 执行提取
    try:
        print(f"正在提取：{URL}")
        result = asyncio.run(extract_post(URL))
        print("提取完成！")
        print(f"作品信息：")
        for key, value in result[0].items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"提取失败：{e}")
        sys.exit(1)
