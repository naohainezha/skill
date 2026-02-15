#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XHS-Downloader 快速下载脚本

使用方法：
    python quick_download.py "小红书作品URL"
    python quick_download.py "小红书作品URL" --info-only    # 仅获取信息
    python quick_download.py "小红书作品URL" --index 1 3 5  # 下载指定图片
"""
import asyncio
import argparse
import sys
import io
from pathlib import Path

# 设置 Windows 终端 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 XHS-Downloader 到路径
XHS_PATH = r"C:\Users\admin\Projects\XHS-Downloader"
sys.path.insert(0, XHS_PATH)

try:
    from source import XHS
except ImportError:
    print(f"错误：无法导入 XHS 模块")
    print(f"请确保 XHS-Downloader 位于：{XHS_PATH}")
    sys.exit(1)


async def download_post(url: str, download: bool = True, index=None):
    """下载小红书作品"""
    print(f"{'='*60}")
    print(f"开始处理：{url}")
    print(f"{'='*60}")

    async with XHS() as xhs:
        try:
            result = await xhs.extract(url, download=download, index=index)

            if result:
                print(f"\n✓ 成功获取 {len(result)} 个作品数据")

                for i, data in enumerate(result, 1):
                    print(f"\n{'─'*60}")
                    print(f"作品 {i}")
                    print(f"{'─'*60}")
                    print(f"标题：{data.get('作品标题', 'N/A')}")
                    print(f"作者：{data.get('作者昵称', 'N/A')}")
                    print(f"发布时间：{data.get('发布时间', 'N/A')}")
                    print(f"类型：{data.get('作品类型', 'N/A')}")
                    print(f"点赞：{data.get('点赞数量', 'N/A')}")
                    print(f"收藏：{data.get('收藏数量', 'N/A')}")
                    print(f"评论：{data.get('评论数量', 'N/A')}")
                    print(f"标签：{data.get('作品标签', 'N/A')}")

                    if download and data.get('下载地址'):
                        urls = data['下载地址']
                        print(f"\n文件数：{len([u for u in urls if u])} 个")

                print(f"\n{'='*60}")
                print(f"处理完成！")
                print(f"下载位置：{XHS_PATH}\\Volume\\Download")
                print(f"{'='*60}")

                return result
            else:
                print("\n✗ 未能获取作品数据")
                return None

        except Exception as e:
            print(f"\n✗ 错误：{e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="XHS-Downloader 快速下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python quick_download.py "https://www.xiaohongshu.com/discovery/item/xxx"
  python quick_download.py "https://www.xiaohongshu.com/explore/xxx" --info-only
  python quick_download.py "https://www.xiaohongshu.com/discovery/item/xxx" --index 1 3 5
        """
    )

    parser.add_argument("url", help="小红书作品链接")
    parser.add_argument("--info-only", action="store_true", help="仅获取信息，不下载文件")
    parser.add_argument("--index", nargs="+", type=int, help="指定下载的图片序号（仅图文作品）")

    args = parser.parse_args()

    if not args.url:
        print("错误：请提供小红书作品链接")
        parser.print_help()
        sys.exit(1)

    # 执行下载
    asyncio.run(download_post(
        url=args.url,
        download=not args.info_only,
        index=args.index
    ))


if __name__ == "__main__":
    main()
