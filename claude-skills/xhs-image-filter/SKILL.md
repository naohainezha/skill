# XHS Image Filter

人脸检测筛选工具，自动筛选适合眼镜融图的清晰人脸素材。

## CONSTANTS

| Key | Value |
|-----|-------|
| **workdir** | `C:\Users\admin\Projects\xhs-image-filter` |
| **entry** | `python cli.py filter <input> --output <output>` |
| **default input** | `C:\Users\admin\Projects\XHS-Downloader\Volume\Download` |
| **default output** | `./output` (relative to workdir) |

> WARNING: Default mode is MOVE (deletes source files). Add `--copy` to preserve originals.

## QUICK START

```bash
# workdir: C:\Users\admin\Projects\xhs-image-filter

# Standard usage: filter with copy mode + recommended threshold
python cli.py filter "C:\Users\admin\Projects\XHS-Downloader\Volume\Download" --output "./output" --min-ratio 0.02 --copy
```

## PARAMETERS

| Param | Default | Recommended | Description |
|-------|---------|-------------|-------------|
| `--min-ratio` | 0.30 | **0.02** | Min face-to-image ratio. Use 0.02 for full-body, 0.10 for selfies |
| `--max-ratio` | 0.90 | 0.90 | Max face ratio (filters extreme close-ups) |
| `--output` | ./output | ./output | Output directory |
| `--copy` | OFF | **ON** | Copy mode. Without this flag, source files are DELETED after move |

### Threshold Guide

| min-ratio | Pass Rate | Best For |
|-----------|-----------|----------|
| 0.02 | ~60-80% | Full-body / fashion bloggers (recommended default) |
| 0.05 | ~50% | Mixed content |
| 0.10 | ~45% | Selfies / close-up bloggers |

## OUTPUT STRUCTURE

```
output/
  filtered/      <- Passed images (input for wash step)
  rejected/
    no_face/     <- No face detected
    small_face/  <- Face ratio below min threshold
    large_face/  <- Face ratio above max threshold
    error/       <- Processing errors
```

## PIPELINE POSITION

Step 2 of 3:
1. Download (xhs-batch-downloader) -> `C:\Users\admin\Projects\XHS-Downloader\Volume\Download\`
2. **[THIS] Filter** -> input: download dir, output: `./output/filtered/`
3. Wash (xhs-comfyui-wash) -> input: `C:\Users\admin\Projects\xhs-image-filter\output\filtered\`

## OTHER COMMANDS

```bash
# Merge multiple folders then filter in one step
python cli.py process ./folder1 ./folder2 --output ./final

# Merge only (no filtering)
python cli.py merge ./folder1 ./folder2 --output ./merged
```

## TROUBLESHOOTING

| Error | Fix |
|-------|-----|
| Pass rate too low (<10%) | Lower `--min-ratio` to 0.02 |
| Pass rate too high (>90%) | Raise `--min-ratio` to 0.10 |
| No face detected on clear photos | OpenCV limitation with side profiles; lower ratio |
| Source files disappeared | Default is MOVE mode. Use `--copy` next time |
