# XHS Workflow Execution Report

## 1. Download
- **Source**: User ID `5ed32c870000000001002c48`
- **Count**: 10 posts
- **Total Images**: 48
- **Location**: `C:\Users\admin\Projects\XHS-Downloader\Volume\Download`

## 2. Filter
- **Tool**: `xhs-image-filter`
- **Criteria**: Face ratio >= 2%
- **Results**:
  - Total: 48
  - Passed: 33 (68.8%)
  - Rejected: 15
- **Location**: `C:\Users\admin\Projects\xhs-image-filter\output\filtered`

## 3. Wash (ComfyUI)
- **Tool**: `xhs-comfyui-wash`
- **Model**: `xiaolian1214_000005250.safetensors` (Small Face Lora)
- **Status**: 33 tasks submitted to ComfyUI queue
- **ComfyUI Port**: 8192 (Custom port due to conflicts)
- **Output Location**: `D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\output`

## Notes
- ComfyUI was started on port 8192 to avoid port conflicts and encoding issues.
- A patch was applied to `ComfyUI/app/logger.py` to fix encoding errors on Windows.
- A patch was applied to `Comfyui-zhenzhen/AiHelper.py` to fix port binding errors.
- Images are currently being processed by ComfyUI. Please check the output folder for results.
