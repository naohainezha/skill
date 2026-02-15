#!/usr/bin/env python3
"""
Twitter/X Video Search and Downloader
Search for videos on Twitter/X and download them in batch

Usage:
    python twitter_video_downloader.py --search "KEYWORD" --count 3 --cookies cookies.txt
    python twitter_video_downloader.py --urls "URL1,URL2,URL3" --cookies cookies.txt
    python twitter_video_downloader.py --search "wataa" --count 5 --cookies cookies.txt --quality 720
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_yt_dlp():
    """Check if yt-dlp is installed"""
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def download_videos(
    urls, cookies_file, output_template="%(title)s.%(ext)s", max_height=None
):
    """Download videos using yt-dlp"""
    if not check_yt_dlp():
        print("Error: yt-dlp is not installed. Install it with: pip install yt-dlp")
        sys.exit(1)

    # Build format string based on quality preference
    if max_height:
        format_str = f"bestvideo[height<={max_height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={max_height}][ext=mp4]/best"
    else:
        format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

    cmd = [
        "yt-dlp",
        "--cookies",
        cookies_file,
        "-f",
        format_str,
        "--merge-output-format",
        "mp4",
        "--no-warnings",
        "-o",
        output_template,
    ] + urls

    print(f"Downloading {len(urls)} video(s)...")
    result = subprocess.run(cmd)
    return result.returncode == 0


def search_and_extract_urls(keyword, cookies_file, count=3):
    """Search Twitter/X and extract video URLs using Playwright with cookies authentication"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "Error: Playwright is not installed. Install it with: pip install playwright"
        )
        print("Then install browser: playwright install chromium")
        sys.exit(1)

    # Read cookies from file (Netscape format)
    cookies = []
    with open(cookies_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies.append(
                    {
                        "domain": parts[0],
                        "path": parts[2],
                        "secure": parts[3] == "TRUE",
                        "expires": int(parts[4]) if parts[4].isdigit() else None,
                        "name": parts[5],
                        "value": parts[6],
                        "httpOnly": parts[0].startswith("#HttpOnly"),
                    }
                )

    print(f"Searching Twitter/X for '{keyword}'...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Add cookies for authentication
        context.add_cookies(cookies)

        page = context.new_page()
        page.goto(
            f"https://x.com/search?q={keyword}&f=video", wait_until="domcontentloaded"
        )
        page.wait_for_timeout(8000)  # Wait for content to load

        # Extract video URLs
        video_links = page.evaluate(
            """() => {
            const links = [];
            const articles = document.querySelectorAll('article');
            
            articles.forEach(article => {
                // Check for video indicators
                const hasVideo = article.querySelector('[data-testid="videoPlayer"]') || 
                                 article.querySelector('video') ||
                                 article.querySelector('[aria-label*="video" i]') ||
                                 article.querySelector('[aria-label*="Video" i]');
                
                if (hasVideo) {
                    const timeLink = article.querySelector('time');
                    if (timeLink) {
                        const link = timeLink.closest('a');
                        if (link && link.href) {
                            links.push(link.href);
                        }
                    }
                }
            });
            
            return links;
        }"""
        )

        browser.close()

        # Remove duplicates and limit to count
        unique_links = list(dict.fromkeys(video_links))[:count]
        return unique_links


def main():
    parser = argparse.ArgumentParser(description="Twitter/X Video Downloader")
    parser.add_argument("--search", "-s", help="Search keyword for Twitter/X videos")
    parser.add_argument("--urls", "-u", help="Comma-separated list of video URLs")
    parser.add_argument(
        "--cookies", "-c", required=True, help="Path to cookies.txt file"
    )
    parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=3,
        help="Number of videos to download from search (default: 3)",
    )
    parser.add_argument(
        "--output", "-o", default="%(title)s.%(ext)s", help="Output filename template"
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        help="Maximum video height (e.g., 720 for 720p)",
    )

    args = parser.parse_args()

    if not args.search and not args.urls:
        parser.error("Either --search or --urls must be provided")

    # Get URLs
    if args.search:
        urls = search_and_extract_urls(args.search, args.cookies, args.count)
        if not urls:
            print("No videos found!")
            sys.exit(1)
        print(f"Found {len(urls)} video(s):")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url}")
    else:
        urls = [url.strip() for url in args.urls.split(",")]

    # Download videos
    if download_videos(urls, args.cookies, args.output, args.quality):
        print("\nAll videos downloaded successfully!")
    else:
        print("\nSome downloads failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
