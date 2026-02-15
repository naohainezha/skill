---
name: video-reader
description: Read, watch, and listen to video/audio files. Extract key frames to "see" videos, extract audio to "hear" them via Whisper transcription. Use when a user sends a video/audio and asks about its content, what's in it, what someone said, etc.
tools: [Bash]
---

# Video Reader Skill

Extract key frames to "see" videos, and extract + transcribe audio to "hear" them.

## Quick Start

```bash
# Get video info (duration, resolution, codec)
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of json "$VIDEO_PATH"

# Extract key frames (1 per second, max 12 frames)
OUTDIR=/tmp/alma-frames-$(date +%s)
mkdir -p "$OUTDIR"
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO_PATH" | cut -d. -f1)
FPS_RATE=$(echo "scale=2; 12 / $DURATION" | bc 2>/dev/null || echo "1")
# Cap at 1fps for short videos
if (( $(echo "$FPS_RATE > 1" | bc -l 2>/dev/null || echo 0) )); then FPS_RATE=1; fi
ffmpeg -hide_banner -loglevel error -i "$VIDEO_PATH" -vf "fps=$FPS_RATE,scale=720:-1" -frames:v 12 "$OUTDIR/frame_%02d.jpg"
ls "$OUTDIR"
```

## How to Use

1. Get video info first to know the duration
2. For short videos (<15s): extract 1 frame per second
3. For medium videos (15-60s): extract ~8-12 frames evenly spread
4. For long videos (>60s): extract 12 frames at key intervals
5. Look at the extracted frames (they're image files) to describe the video content

## Frame Extraction Patterns

```bash
# Even spread: N frames across entire video
ffmpeg -hide_banner -loglevel error -i "$VIDEO_PATH" \
  -vf "select='not(mod(n\,$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$VIDEO_PATH" | awk -v n=8 '{printf "%d", $1/n}')))'" \
  -vsync vfr -frames:v 8 "$OUTDIR/frame_%02d.jpg"

# Specific timestamp
ffmpeg -hide_banner -loglevel error -ss 5.0 -i "$VIDEO_PATH" -frames:v 1 "$OUTDIR/at_5s.jpg"

# Thumbnail grid (single image overview)
ffmpeg -hide_banner -loglevel error -i "$VIDEO_PATH" \
  -vf "fps=1/$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEO_PATH" | awk '{printf "%.1f", $1/9}'),scale=320:-1,tile=3x3" \
  -frames:v 1 "$OUTDIR/grid.jpg"
```

## Tips

- Always use `-hide_banner -loglevel error` to keep output clean
- Scale down to 720px width (`scale=720:-1`) to save tokens when sending to AI
- Clean up frames after analysis: `rm -rf "$OUTDIR"`
- The extracted frames are regular image files — include their paths in your reply and they'll be auto-sent to Telegram

## Audio: "Hearing" Videos

```bash
# Extract audio from video
ffmpeg -hide_banner -loglevel error -i "$VIDEO_PATH" -vn -acodec pcm_s16le -ar 16000 -ac 1 "/tmp/alma-audio-$(date +%s).wav"

# Transcribe with Whisper (auto-detect language)
whisper "/tmp/alma-audio.wav" --model turbo --output_format txt --output_dir /tmp/alma-whisper

# Transcribe with specific language
whisper "/tmp/alma-audio.wav" --model turbo --language zh --output_format txt --output_dir /tmp/alma-whisper

# Read transcription
cat /tmp/alma-whisper/*.txt
```

## When to See vs Hear

- **"这个视频里有啥"** → Extract frames (see) + transcribe audio (hear) for full picture
- **"他说了什么"** → Transcribe audio only
- **"这个视频好看吗"** → Extract frames to see the visuals
- **"好听"** → The user is commenting on audio content, transcribe to understand
- **Music/street performance** → Mention what you see in frames + note the audio content
- When in doubt, do BOTH — extract a few frames AND transcribe the audio

## Cleanup

Always clean up temp files after analysis:
```bash
rm -rf "$OUTDIR" /tmp/alma-whisper /tmp/alma-audio*.wav
```
