# ComfyUI 配置

## 工作流配置

### 1. 分辨率设置（关键）

**问题**：如果直接生成高分辨率（如1440x1920）图片，放大（Upscale）节点将不起作用，导致第三次采样（High-res fix）失效，画质细节不足。

**解决方案**：
- **初始生成分辨率**：强制设置为 `960x1280` (EmptyLatentImage)
- **放大目标**：放大到 `1920` (ImageScaleToMaxDimension)
- **流程**：`960x1280` (初步生成) -> `Upscale` -> `1440x1920` (高清修复)

### 2. EmptyLatentImage 节点

```
resolution: "960x1280"
```

**注意**：必须设置为 960x1280，不能是 1440x1920 或更高。

### 3. ImageScaleToMaxDimension 节点

```
upscale_method: "nearest-exact"
largest_size: 1920
```

**参数说明**：
- `upscale_method`：放大方法（推荐 `nearest-exact`）
- `largest_size`：放大后的最大尺寸

**⚠️ 重要**：参数名是 `largest_size`，不是 `max_dimension`。

## 脚本集成

此逻辑已集成在 `comfyui_generator.py` 中，脚本会自动检测并调整 EmptyLatentImage 节点的 resolution。

## 节点参数映射

### 正确参数
```
ImageScaleToMaxDimension:
- upscale_method
- largest_size
```

### 错误参数
```
ImageScaleToMaxDimension:
- interpolation_mode  # ❌ 错误
- max_dimension      # ❌ 错误
```

## 文件位置

### 生成器脚本
```
D:\xiaohongshu-crawler\comfyui_generator.py
```

### 工作流配置
```
D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\zimage文生图0106.json
```

### 输出目录
```
D:\output\xitu
```

## 注意事项

1. **分辨率必须为 960x1280**：否则放大修复链路不工作
2. **参数名必须正确**：`largest_size` 而非 `max_dimension`
3. **工作流路径要正确**：确保 JSON 文件存在
4. **输出目录要存在**：确保 `D:\output\xitu` 目录已创建
