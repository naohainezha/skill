#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram 图片批量下载脚本 - 用于Playwright方案
配合浏览器提取的图片URL进行下载
"""

import requests
import os
import sys
import time


def download_image(url, filepath):
    """Download an image from URL to filepath."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(
                f"  Downloaded: {os.path.basename(filepath)} ({len(resp.content)} bytes)"
            )
            return True
        else:
            print(f"  Failed: {resp.status_code} for {url[:60]}...")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_download_ig.py <shortcode> <url1> [url2] ...")
        print(
            "       python batch_download_ig.py <shortcode> --output-dir <dir> <url1> [url2] ..."
        )
        print()
        print("Example:")
        print(
            "  python batch_download_ig.py DTkbATXkwCh https://scontent... https://scontent..."
        )
        print(
            "  python batch_download_ig.py DTkbATXkwCh --output-dir ./downloads https://scontent..."
        )
        sys.exit(1)

    shortcode = sys.argv[1]

    # Parse arguments
    output_dir = os.getcwd()
    urls = []

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--output-dir" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        else:
            urls.append(args[i])
            i += 1

    if not urls:
        print(f"No URLs provided for {shortcode}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Downloading {len(urls)} images for post {shortcode}...")
    print(f"Output directory: {output_dir}")

    success = 0
    for i, url in enumerate(urls, 1):
        filepath = os.path.join(output_dir, f"{shortcode}_{i}.jpg")
        if download_image(url, filepath):
            success += 1
        time.sleep(0.5)  # Small delay between downloads

    print(f"Downloaded {success}/{len(urls)} images for {shortcode}")
    return success


if __name__ == "__main__":
    main()
