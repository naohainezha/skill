# XHS ComfyUI Wash

ComfyUI批量洗图工具。一次性提交所有任务到队列，ComfyUI自动依次处理。

## CONSTANTS

| Key | Value |
|-----|-------|
| **workdir** | `C:\Users\admin\Projects\xhs-comfyui-wash` |
| **entry** | `python wash_submit_only.py [lora_file] [strength]` |
| **ComfyUI API** | `http://192.168.11.158:8188` |
| **ComfyUI dir** | `D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI` |
| **input dir** | `C:\Users\admin\Projects\xhs-image-filter\output\filtered\` |
| **output dir** | `D:\output\xitu\` |
| **workflow** | `...\ComfyUI\user\default\workflows\z洗图1222api.json` |
| **LORA dir** | `...\ComfyUI\models\loras\` |
| **default LORA** | `xiaolian1214_000005250.safetensors` (小脸, strength 0.8) |

> CRITICAL: Verify `self.api_url` in `wash_submit_only.py` is `http://192.168.11.158:8188`.
> Known bug: value may revert to `127.0.0.1:8192`. Check and fix before running.

## QUICK START

```bash
# workdir: C:\Users\admin\Projects\xhs-comfyui-wash

# Step 1: Start ComfyUI (skip if already running, ~80s startup)
python start_comfyui.py

# Step 2: Verify running
curl http://192.168.11.158:8188/system_stats

# Step 3: Submit wash tasks
python wash_submit_only.py                                      # default LORA (小脸)
python wash_submit_only.py "duanfa1_000008750.safetensors" 0.8  # 短发 LORA
```

After submission, check progress at `http://192.168.11.158:8188`.

## LORA MODELS

### Alias Mapping (Chinese Name -> Filename)

| User Says | Filename | Description |
|-----------|----------|-------------|
| 短发 | `duanfa1_000008750.safetensors` | Short hair style |
| 小脸 (default) | `xiaolian1214_000005250.safetensors` | Slim face |
| 小脸2 | `xiaolian2.safetensors` | Slim face v2 |
| 宽脸 | `Z_kuanlian_000001140.safetensors` | Wide face |

> Config file: `C:\Users\admin\.claude\skills\xhs-comfyui-wash\config\lora_aliases.json`

### All Available LORAs

```
xiaolian1214_000005250.safetensors  <- 小脸 (DEFAULT)
duanfa1_000008750.safetensors       <- 短发
xiaolian2.safetensors               <- 小脸2
xiaolian2_000008250.safetensors
xiaolian_000001800.safetensors      <- 小脸旧版
Z_kuanlian_000001140.safetensors    <- 宽脸
Z_kuanlian_000000540.safetensors
```

## SCRIPTS

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `wash_submit_only.py` | Batch submit to queue, return immediately | **Default for all wash tasks** |
| `start_comfyui.py` | Start ComfyUI service (~80s) | When ComfyUI is not running |
| `scripts/wash_lora.py` | Sequential single-image processing | Debug only |
| `scripts/lora_manager.py` | List available LORAs | Query available models |

## PIPELINE POSITION

Step 3 of 3:
1. Download (xhs-batch-downloader) -> `XHS-Downloader/Volume/Download/`
2. Filter (xhs-image-filter) -> `xhs-image-filter/output/filtered/`
3. **[THIS] Wash** -> input: filtered dir, output: ComfyUI output dir

## VERIFY STATUS

```bash
# Is ComfyUI running?
curl -s http://192.168.11.158:8188/system_stats

# Check queue progress
curl -s http://192.168.11.158:8188/queue

# List output files
ls "D:/output/xitu/"
```

## TROUBLESHOOTING

| Error | Fix |
|-------|-----|
| ComfyUI not running | `python start_comfyui.py` (wait ~80s) |
| Connection refused / empty response | Wrong API URL. Fix `self.api_url` to `http://192.168.11.158:8188` |
| filtered dir empty | Run xhs-image-filter first |
| UnicodeEncodeError on print | Cosmetic (Windows GBK), tasks submitted successfully |
| LORA not found | Check exact filename (case-sensitive) in LORA dir |
