# ComfyUI 集成指南

## 工作流配置

### 工作流文件
```
D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\zimage文生图0106.json
```

### 生成器脚本
```
D:\xiaohongshu-crawler\comfyui_generator.py
```

### 输出目录
```
D:\output\xitu
```

## 分辨率设置（关键）

### 问题
如果直接生成高分辨率（如1440x1920）图片，放大（Upscale）节点将不起作用，导致第三次采样（High-res fix）失效，画质细节不足。

### 解决方案

#### 初始生成分辨率
- **强制设置为**：`960x1280` (EmptyLatentImage)
- **节点名称**：`EmptyLatentImage`
- **参数**：`resolution: "960x1280"`

#### 放大目标
- **放大到**：`1920` (ImageScaleToMaxDimension)
- **节点名称**：`ImageScaleToMaxDimension`
- **参数**：
  - `upscale_method: "nearest-exact"`
  - `largest_size: 1920`

#### 完整流程
```
960x1280 (初步生成) 
  → Upscale 
  → 1440x1920 (高清修复)
```

## 节点参数映射

### ImageScaleToMaxDimension

#### 正确参数
```json
{
  "upscale_method": "nearest-exact",
  "largest_size": 1920
}
```

#### 错误参数（不要使用）
```json
{
  "interpolation_mode": "...",  // ❌ 错误
  "max_dimension": "..."     // ❌ 错误
}
```

## 自动化逻辑

`comfyui_generator.py` 脚本已集成此逻辑：
1. 检测 EmptyLatentImage 节点的 resolution 参数
2. 如不是 `960x1280`，自动调整为 `960x1280`
3. 确保 ImageScaleToMaxDimension 节点使用正确参数名

## 注意事项

### 1. 工作流路径
- 确保工作流 JSON 文件存在
- 路径：`D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\zimage文生图0106.json`

### 2. 输出目录
- 确保 `D:\output\xitu` 目录已创建
- 脚本会在该目录保存生成的图片

### 3. 分辨率必须正确
- 必须是 `960x1280`，不能是 `1440x1920` 或更高
- 否则放大修复链路不工作

### 4. 参数名必须正确
- 使用 `largest_size`，不是 `max_dimension`
- 使用 `upscale_method`，不是 `interpolation_mode`

## 故障排除

### 图片细节不足
**可能原因**：
- 初始分辨率太高（超过960x1280）
- 放大节点参数错误

**解决方案**：
- 检查 EmptyLatentImage 的 resolution 参数
- 确认是 `960x1280`
- 检查 ImageScaleToMaxDimension 的参数名

### 脚本运行失败
**可能原因**：
- 工作流文件路径错误
- ComfyUI 未运行

**解决方案**：
- 确认 ComfyUI 正在运行
- 检查工作流文件路径
- 查看脚本错误日志

## 完整示例

### 工作流 JSON 片段
```json
{
  "1": {
    "class_type": "EmptyLatentImage",
    "inputs": {
      "resolution": "960x1280",
      "batch_size": 1
    },
    "pos": [0, 0]
  },
  "2": {
    "class_type": "ImageScaleToMaxDimension",
    "inputs": {
      "upscale_method": "nearest-exact",
      "largest_size": 1920,
      "image": ["1", 0]
    },
    "pos": [0, 150]
  }
}
```

此配置确保了初始分辨率为 960x1280，放大到 1920，激活完整的放大修复链路。
