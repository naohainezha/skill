---
name: advanced-video-downloader
description: Download and transcribe videos from YouTube, Bilibili, TikTok and 1000+ platforms. Use when user requests video download, transcription (转录/字幕提取), or converting video to text/markdown. Supports quality selection, audio extraction, playlist downloads, cookie-based authentication, and AI-powered transcription via SiliconFlow API (免费转录).
---

# Advanced Video Downloader

## Overview

This skill provides comprehensive video downloading and transcription capabilities from 1000+ platforms including YouTube, Bilibili, TikTok, Twitter, Instagram, and more. It combines:
- **yt-dlp**: Powerful video downloading tool
- **SiliconFlow API**: Free AI-powered transcription to convert videos to Markdown

## When to Use This Skill

Activate this skill when the user:
- Explicitly requests to download a video ("download this video", "下载视频")
- Provides video URLs from any platform
- Mentions saving videos for offline viewing
- Wants to extract audio from videos
- Needs to download multiple videos or playlists
- Asks about video quality options
- Requests video transcription ("转录视频", "提取字幕", "视频转文字")
- Wants to convert video/audio to text or Markdown
- Asks to download AND transcribe a video in one workflow
- **Requests to search and download videos from Twitter/X** ("在Twitter上搜XXX下载视频", "twitter下载视频")
- **Wants to batch download videos from social media platforms** (批量下载Twitter视频)
- **Needs to download Twitter videos using cookies** (requires cookies.txt for authentication)

## Core Capabilities

### 1. Single Video Download
Download individual videos from any supported platform with automatic quality selection.

**Example usage:**
```
User: "Download this YouTube video: https://youtube.com/watch?v=abc123"
User: "下载这个B站视频: https://bilibili.com/video/BV1xxx"
```

### 2. Batch & Playlist Download
Download multiple videos or entire playlists at once.

**Example usage:**
```
User: "Download all videos from this playlist"
User: "Download these 3 videos: [URL1], [URL2], [URL3]"
User: "在Twitter上搜wataa，下载3个视频"
```

**Twitter/X Search & Batch Download Workflow:**

Twitter/X **requires authentication (cookies)** to search and download videos. Follow these steps:

```bash
# 1. Get cookies.txt file (see "Getting Twitter Cookies" below)
# Required cookies: auth_token, ct0, twid

# 2. Use the bundled script to search and download
python scripts/twitter_video_downloader.py --search "KEYWORD" --count 5 --cookies cookies.txt

# Or with quality limit (recommended for large videos)
python scripts/twitter_video_downloader.py --search "KEYWORD" --count 5 --cookies cookies.txt --quality 720

# 3. Or manually batch download extracted URLs
yt-dlp --cookies cookies.txt \
  -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best" \
  --merge-output-format mp4 \
  -o "%(title)s.%(ext)s" \
  "URL1" "URL2" "URL3"
```

**Getting Twitter Cookies:**
1. Install browser extension "Get cookies.txt LOCALLY"
2. Log in to Twitter/X in your browser
3. Click the extension icon and export cookies
4. Save as `cookies.txt` in Netscape format

**Note:** Without valid cookies, Twitter/X search will return no results and downloads will fail.

### 3. Audio Extraction
Extract audio only from videos, saving as MP3 or M4A.

**Example usage:**
```
User: "Download only the audio from this video"
User: "Convert this video to MP3"
```

### 4. Quality Selection
Choose specific video quality (4K, 1080p, 720p, etc.).

**Example usage:**
```
User: "Download in 4K quality"
User: "Get the 720p version to save space"
```

### 5. Video/Audio Transcription
Convert video or audio files to Markdown text using SiliconFlow's free AI transcription API.

**Example usage:**
```
User: "Transcribe this video to text" / "转录这个视频"
User: "Download and transcribe this YouTube video"
User: "将这个音频转成文字"
User: "Extract transcript from this MP4 file"
```

**Supported formats:**
- Audio: MP3, WAV, M4A, FLAC, AAC, OGG, OPUS, WMA
- Video: MP4, AVI, MOV, MKV, FLV, WMV, WEBM, M4V

## Response Pattern

When a user requests video download:

### Step 1: Identify the Platform and URL(s)
```python
# Extract video URL(s) from user message
# Identify platform: YouTube, Bilibili, TikTok, etc.
```

### Step 2: Check Tool Availability
```bash
# Check if yt-dlp is installed
yt-dlp --version
```

### Step 3: Select Appropriate yt-dlp Command

Based on platform and requirements:
- **YouTube, Twitter, Instagram, TikTok**: Basic command works
- **Bilibili**: Basic command works for most videos
- **Quality selection**: Use `-f` with height filter
- **Audio only**: Use `-x --audio-format mp3`
- **Playlists**: Use playlist-specific output template

### Step 4: Execute Download

Use yt-dlp directly with appropriate options:

```bash
# Basic download (best quality MP4)
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --merge-output-format mp4 -o "%(title)s.%(ext)s" "VIDEO_URL"

# Specific quality (1080p)
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 -o "%(title)s.%(ext)s" "VIDEO_URL"

# Audio only (MP3)
yt-dlp -x --audio-format mp3 -o "%(title)s.%(ext)s" "VIDEO_URL"

# With cookies file (for protected content)
yt-dlp --cookies cookies.txt -o "%(title)s.%(ext)s" "VIDEO_URL"

# Playlist download
yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"
```

### Step 5: Report Results
After download completes, report:
- ✅ Video title and duration
- ✅ File size and format
- ✅ Save location
- ✅ Download speed and time taken
- ⚠️ Any warnings or quality limitations

**Example output:**
```
✅ Downloaded: "Video Title Here"
   Duration: 15:30
   Quality: 1080p MP4
   Size: 234 MB
   Location: ./Video Title Here.mp4
   Time: 45 seconds at 5.2 MB/s
```

## Transcription Response Pattern

When a user requests video/audio transcription:

### Step 1: Check Prerequisites
```bash
# Verify SiliconFlow API key is available
echo $SILICONFLOW_API_KEY
# Or user must provide via --api-key parameter
```

**API Key Setup:**
- Get free API key from: https://cloud.siliconflow.cn/account/ak
- Copy `.env.example` to `.env` and add your API key
- Or set environment variable: `SILICONFLOW_API_KEY=sk-xxx`

### Step 2: Validate File
Ensure the file exists and is a supported format (audio or video).

### Step 3: Execute Transcription
Use the bundled script `scripts/transcribe_siliconflow.py`:

```bash
# Basic transcription
python scripts/transcribe_siliconflow.py --file video.mp4 --api-key sk-xxx

# With custom output path
python scripts/transcribe_siliconflow.py --file audio.mp3 --output transcript.md --api-key sk-xxx

# Using environment variable for API key
python scripts/transcribe_siliconflow.py --file video.mp4
```

### Step 4: Report Transcription Results
```
✅ Transcription complete!
   File: video.mp4
   Output: 2025-01-15-video.md
   Size: 12.5 KB

   Preview:
   --------------------------------------------------
   [First 200 characters of transcription...]
   --------------------------------------------------
```

## Combined Workflow: Download + Transcribe

For requests like "Download and transcribe this video":

```bash
# Step 1: Download video
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" --merge-output-format mp4 -o "%(title)s.%(ext)s" "VIDEO_URL"

# Step 2: Transcribe the downloaded file
python scripts/transcribe_siliconflow.py --file "Downloaded Video Title.mp4" --api-key sk-xxx
```

## Platform-Specific Notes

### YouTube
- Fully supported by yt-dlp
- No authentication needed for public videos
- Supports all quality levels including 4K/8K

### Bilibili
- Supported by yt-dlp
- High-quality downloads may require login cookies
- Use `--cookies` with cookies.txt for member-only content

### Twitter/X
- **Search & Download Workflow**: For downloading multiple videos from search results
  1. Use Playwright to search with cookies authentication
  2. Extract video URLs from search results
  3. Batch download using yt-dlp with cookies

**Important**: Twitter/X requires authentication (cookies) to search videos. Without cookies, search will return no results.

**Quick Start - Using the bundled script:**
```bash
# Search and download 5 videos with cookies
python scripts/twitter_video_downloader.py --search "KEYWORD" --count 5 --cookies cookies.txt

# With quality limit (720p)
python scripts/twitter_video_downloader.py --search "KEYWORD" --count 5 --cookies cookies.txt --quality 720
```

**Manual Workflow Example:**
```python
# Step 1: Search and extract URLs using Playwright with cookies
from playwright.sync_api import sync_playwright

def search_twitter_videos(keyword, cookies_file, count=5):
    # Read cookies from Netscape format file
    cookies = []
    with open(cookies_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 7:
                cookies.append({
                    "domain": parts[0],
                    "path": parts[2],
                    "secure": parts[3] == "TRUE",
                    "expires": int(parts[4]) if parts[4].isdigit() else None,
                    "name": parts[5],
                    "value": parts[6],
                    "httpOnly": parts[0].startswith("#HttpOnly"),
                })

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(cookies)  # Add auth cookies
        
        page = context.new_page()
        page.goto(f"https://x.com/search?q={keyword}&f=video", wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        # Extract video URLs
        video_links = page.evaluate("""() => {
            const links = [];
            document.querySelectorAll('article').forEach(article => {
                const hasVideo = article.querySelector('[data-testid="videoPlayer"]') || 
                                 article.querySelector('video');
                if (hasVideo) {
                    const timeLink = article.querySelector('time');
                    if (timeLink) {
                        const link = timeLink.closest('a');
                        if (link && link.href) links.push(link.href);
                    }
                }
            });
            return links.slice(0, """ + str(count) + """);
        }""")
        
        browser.close()
        return video_links

# Step 2: Download with yt-dlp using cookies
# yt-dlp --cookies cookies.txt -f "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best" \
#   --merge-output-format mp4 -o "%(title)s.%(ext)s" "URL1" "URL2" ...
```

**Required Twitter Cookies:**
- `auth_token` - Authentication token
- `ct0` - CSRF token
- `twid` - User ID

Get these by exporting cookies from your browser after logging into Twitter/X.

### Other Platforms
- Most platforms work well with yt-dlp
- Check `references/supported_platforms.md` for full list

## Handling Cookies for Protected Content

For platforms requiring authentication (Bilibili VIP, member-only content, etc.):

### Method 1: Export Cookies File (Recommended)
```bash
# Use browser extension "Get cookies.txt LOCALLY"
# Export cookies.txt, then:
yt-dlp --cookies cookies.txt "VIDEO_URL"
```

### Method 2: Manual Cookies File
```bash
# Create cookies.txt in Netscape format
# Use browser extension "Get cookies.txt LOCALLY"
# Then use with yt-dlp
yt-dlp --cookies cookies.txt "VIDEO_URL"
```

## Troubleshooting

### Issue: Video quality lower than expected
**Solution:**
1. Check if platform requires login for HD
2. Use `--cookies cookies.txt` for authenticated access
3. Explicitly specify quality with `-f` parameter

### Issue: Download very slow
**Solution:**
1. Check internet connection
2. Try different time of day (peak hours affect speed)
3. Use `--concurrent-fragments` for faster downloads

### Issue: "Video unavailable" or geo-restricted
**Solution:**
1. Video may be region-locked
2. Use proxy/VPN if legally permitted
3. Check if video is still available on platform

### Issue: Transcription API key error
**Solution:**
1. Verify API key starts with `sk-`
2. Get free key from: https://cloud.siliconflow.cn/account/ak
3. Set environment variable: `SILICONFLOW_API_KEY=sk-xxx`

### Issue: Transcription returns empty text
**Solution:**
1. Check if audio/video has clear speech
2. Verify file format is supported
3. File may be too short or contain only music

## Common Commands

### Quality Presets

```bash
# 4K (2160p)
yt-dlp -f "bestvideo[height<=2160]+bestaudio/best[height<=2160]" --merge-output-format mp4 "VIDEO_URL"

# 1080p (Full HD)
yt-dlp -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" --merge-output-format mp4 "VIDEO_URL"

# 720p (HD)
yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]" --merge-output-format mp4 "VIDEO_URL"

# 480p (SD)
yt-dlp -f "bestvideo[height<=480]+bestaudio/best[height<=480]" --merge-output-format mp4 "VIDEO_URL"
```

### Audio Extraction

```bash
# Extract as MP3
yt-dlp -x --audio-format mp3 -o "%(title)s.%(ext)s" "VIDEO_URL"

# Extract as M4A (better quality)
yt-dlp -x --audio-format m4a -o "%(title)s.%(ext)s" "VIDEO_URL"
```

### Batch Downloads

```bash
# Download multiple URLs from file
yt-dlp -a urls.txt

# Download playlist with custom naming
yt-dlp -o "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" "PLAYLIST_URL"

# Download channel's videos
yt-dlp -o "%(uploader)s/%(title)s.%(ext)s" "CHANNEL_URL"
```

## Bundled Resources

### Configuration

#### `.env.example`
Template for environment variables. Copy to `.env` and add your SiliconFlow API key.

### Scripts

#### `scripts/transcribe_siliconflow.py`
AI-powered transcription script using SiliconFlow's free API.

**Usage:**
```bash
python scripts/transcribe_siliconflow.py --file <audio/video> [--api-key <key>] [--output <path>]
```

**Parameters:**
- `--file, -f`: Input audio/video file (required)
- `--api-key, -k`: SiliconFlow API key (or use `SILICONFLOW_API_KEY` env var)
- `--output, -o`: Output markdown file path (default: `YYYY-MM-DD-filename.md`)
- `--model, -m`: Model to use (default: `FunAudioLLM/SenseVoiceSmall`)

#### `scripts/twitter_video_downloader.py`
Search and download videos from Twitter/X in batch.

**Prerequisites:**
```bash
pip install playwright
playwright install chromium
```

**Usage:**
```bash
# Search and download videos
python scripts/twitter_video_downloader.py --search "KEYWORD" --count 3 --cookies cookies.txt

# Download specific URLs
python scripts/twitter_video_downloader.py --urls "URL1,URL2,URL3" --cookies cookies.txt
```

**Parameters:**
- `--search, -s`: Search keyword for Twitter/X videos
- `--urls, -u`: Comma-separated list of video URLs to download
- `--cookies, -c`: Path to cookies.txt file (required)
- `--count, -n`: Number of videos to download from search (default: 3)
- `--output, -o`: Output filename template (default: `%(title)s.%(ext)s`)
- `--quality, -q`: Maximum video height, e.g., 720 for 720p (optional)

**Getting Twitter Cookies:**
1. Install browser extension "Get cookies.txt LOCALLY"
2. Log in to Twitter/X in your browser
3. Click the extension icon and export cookies
4. Save as `cookies.txt` in Netscape format

**Example Workflow:**
```bash
# Download 5 videos from Twitter search with quality limit
python scripts/twitter_video_downloader.py --search "wataa" --count 5 --cookies cookies.txt --quality 720

# Download specific Twitter videos
python scripts/twitter_video_downloader.py --urls "https://x.com/user/status/123,https://x.com/user/status/456" --cookies cookies.txt
```

### References

#### `references/supported_platforms.md`
Comprehensive list of 1000+ supported platforms with platform-specific notes and requirements.

#### `references/quality_formats.md`
Detailed explanation of video formats, codecs, and quality selection strategies.

## Tips for Best Results

1. **Always specify quality if user has preference** - saves bandwidth and storage
2. **Batch downloads save time** - use playlist URLs when possible
3. **Audio extraction is faster** - recommend for podcast/music content
4. **Check file size before downloading** - warn user for very large files (>1GB)
5. **Transcription works best with clear audio** - consider extracting audio first for better results

## Sources

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [yt-dlp Installation Guide](https://github.com/yt-dlp/yt-dlp#installation)
- [SiliconFlow API Documentation](https://docs.siliconflow.cn/)
- [SiliconFlow Free API Key](https://cloud.siliconflow.cn/account/ak)
