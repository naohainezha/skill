#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 图片批量下载脚本
支持断点续传、限流处理、延迟控制
"""

import subprocess
import time
import os
import sys
import argparse
from pathlib import Path

# 设置UTF-8编码
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def check_instaloader():
    """检查 instaloader 是否已安装"""
    try:
        result = subprocess.run(
            ["instaloader", "--version"], capture_output=True, text=True, check=True
        )
        print(f"✓ instaloader 已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ instaloader 未安装，正在安装...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "instaloader"], check=True
            )
            print("✓ instaloader 安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ 安装失败: {e}")
            return False


def download_instagram(
    username, use_login=False, delay_mode=False, login_username=None, max_posts=None
):
    """
    下载Instagram用户图片

    Args:
        username: Instagram 用户名
        use_login: 是否使用登录模式
        delay_mode: 是否启用延迟模式（每10篇休息2分钟）
        login_username: 登录用户名（如使用登录模式）
        max_posts: 最大下载帖子数量（None表示不限制）
    """

    # 检查 instaloader
    if not check_instaloader():
        print("错误：无法安装 instaloader")
        return False

    # 创建下载目录
    download_dir = f"{username}_instagram"
    os.makedirs(download_dir, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"开始下载 Instagram 用户: {username}")
    if max_posts:
        print(f"下载数量: 最近 {max_posts} 篇帖子")
    print(f"保存位置: {os.path.abspath(download_dir)}")
    print(f"{'=' * 60}\n")

    # 构建命令
    cmd = [
        "instaloader",
        "--no-videos",
        "--no-captions",
        "--no-metadata-json",
        "--fast-update",
        "--dirname-pattern",
        download_dir,
    ]

    if use_login and login_username:
        cmd.extend(["--login", login_username])

    # 如果设置了最大帖子数，使用 --count 参数
    if max_posts:
        cmd.extend(["--count", str(max_posts)])

    cmd.append(username)

    # 执行下载
    try:
        if delay_mode:
            # 延迟模式：分批下载
            result = download_with_delay(cmd, username, download_dir, max_posts)
        else:
            # 普通模式：一次性下载
            result = download_normal(cmd, username, download_dir)

        return result

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断下载")
        print(f"已下载的文件保存在: {os.path.abspath(download_dir)}")
        return False
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        return False


def download_normal(cmd, username, download_dir):
    """普通下载模式"""
    print("执行普通下载模式...\n")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    error_count = 0
    stdout_data = process.stdout
    if stdout_data is not None:
        for line in stdout_data:
            print(line, end="")

            # 检测限流错误
            if "403 Forbidden" in line or "401 Unauthorized" in line:
                error_count += 1
                if error_count >= 3:
                    print("\n" + "=" * 60)
                    print("⚠️  Instagram 已触发限流保护")
                    print("=" * 60)
                    print("建议:")
                    print("  1. 等待 30-60 分钟后重试")
                    print("  2. 使用登录模式: --login 你的用户名")
                    print("=" * 60 + "\n")

    process.wait()

    # 统计结果
    show_download_stats(download_dir, username)

    return process.returncode == 0


def download_with_delay(cmd, username, download_dir, max_posts=None):
    """延迟下载模式（每10篇休息2分钟）"""
    print("执行延迟下载模式（每10篇休息2分钟）...\n")

    # 由于 instaloader 不支持在下载过程中插入延迟，
    # 我们使用普通模式，但在遇到限流时给出更详细的提示

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    downloaded_posts = 0
    last_batch_time = time.time()

    stdout_data = process.stdout
    if stdout_data is not None:
        for line in stdout_data:
            print(line, end="")

            # 统计已下载帖子数
            if "/" in line and "]" in line and "exists" not in line.lower():
                try:
                    # 解析进度 [ xx/xxx]
                    progress = line.split("]")[0].split("[")[1].strip()
                    current = int(progress.split("/")[0])
                    if current > downloaded_posts:
                        downloaded_posts = current

                        # 每10篇检查一次
                        if downloaded_posts % 10 == 0:
                            elapsed = time.time() - last_batch_time
                            if elapsed < 120:  # 如果不到2分钟
                                sleep_time = 120 - elapsed
                                print(f"\n⏸️  已下载 {downloaded_posts} 篇帖子")
                                print(f"⏰  休息 {sleep_time:.0f} 秒以避免限流...")
                                time.sleep(sleep_time)
                                last_batch_time = time.time()
                                print("✓ 继续下载\n")
                except:
                    pass

    process.wait()

    # 统计结果
    show_download_stats(download_dir, username)

    return process.returncode == 0


def show_download_stats(download_dir, username):
    """显示下载统计"""
    print("\n" + "=" * 60)
    print("下载统计")
    print("=" * 60)

    # 统计文件
    if os.path.exists(download_dir):
        jpg_files = list(Path(download_dir).glob("*.jpg"))
        txt_files = list(Path(download_dir).glob("*.txt"))

        print(f"📁 保存位置: {os.path.abspath(download_dir)}")
        print(f"📸 图片数量: {len(jpg_files)} 张")
        print(f"📝 说明文件: {len(txt_files)} 个")

        if len(jpg_files) > 0:
            print(f"\n✅ 下载完成！")
            print(f"\n提示: 如未下载完整，可再次运行命令继续下载")
            print(f"      (已下载的文件会自动跳过)")
    else:
        print(f"✗ 下载目录未创建")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Instagram 图片批量下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python download_instagram.py moyuka_
  python download_instagram.py moyuka_ --login myusername
  python download_instagram.py moyuka_ --delay
  python download_instagram.py moyuka_ --max-posts 50
        """,
    )

    parser.add_argument("username", help="Instagram 用户名")
    parser.add_argument("--login", dest="login_user", help="登录用户名（可选）")
    parser.add_argument("--delay", action="store_true", help="启用延迟模式")
    parser.add_argument("--max-posts", type=int, help="最大下载帖子数量（如：50）")

    args = parser.parse_args()

    # 执行下载
    success = download_instagram(
        username=args.username,
        use_login=bool(args.login_user),
        delay_mode=args.delay,
        login_username=args.login_user,
        max_posts=args.max_posts,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
