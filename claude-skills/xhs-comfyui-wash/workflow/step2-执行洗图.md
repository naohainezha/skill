# Step 2: Execute Batch Wash

## Command

```bash
# workdir: C:\Users\admin\Projects\xhs-comfyui-wash

# Default LORA (小脸)
python wash_submit_only.py

# Specify LORA
python wash_submit_only.py "duanfa1_000008750.safetensors" 0.8
```

## How It Works

1. Reads all images from `C:\Users\admin\Projects\xhs-image-filter\output\filtered\`
2. Submits N tasks to ComfyUI queue (one per image)
3. Script exits immediately after submission
4. ComfyUI processes queue automatically

## Output

Results saved to: `D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\output\`

## Timing

- Submit: ~0.3s per image
- Process: 10-30s per image (GPU dependent)
- 22 images: ~10 min total processing
