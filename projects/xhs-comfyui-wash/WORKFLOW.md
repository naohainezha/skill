# 筛选素材洗图工作流程文档

## 📋 新工作流程说明

### 流程图

```
筛选素材库 (filtered/)
    ↓
[ComfyUI + 小脸LoRA]
    ↓
已处理素材库 (processed/)
```

---

## 📁 目录结构

```
C:\Users\admin\Projects\xhs-image-filter\output\
├── filtered/       ← 筛选通过的素材（待处理）
│   ├── 图片1.png
│   ├── 图片2.png
│   └── ...
├── processed/      ← 处理后的素材（已处理）
│   ├── 图片1_washed.png
│   ├── 图片2_washed.png
│   └── ...
└── rejected/       ← 未通过筛选的素材
```

---

## 🚀 使用方法

### 方法1：使用新的洗图脚本（推荐）

```bash
cd C:\Users\admin\projects\xhs-comfyui-wash

# 使用默认小脸 LoRA
python wash_and_move.py

# 指定 LoRA 和强度
python wash_and_move.py "xiaolian_000001800.safetensors" 0.8
python wash_and_move.py "xiaolian2.safetensors" 0.8
```

**功能**：
- ✅ 自动从 `filtered/` 读取图片
- ✅ 使用 ComfyUI + 小脸 LoRA 处理
- ✅ 处理后保存到 `processed/`
- ✅ 自动从 `filtered/` 移除已处理的文件
- ✅ 实时显示进度

### 方法2：手动使用原脚本 + 手动移动

```bash
# 步骤1: 洗图
cd C:\Users\admin\projects\xhs-comfyui-wash
python wash_lora.py "C:\Users\admin\Projects\xhs-image-filter\output\filtered" "xiaolian_000001800.safetensors" 0.8

# 步骤2: 手动移动
mv /d/output/xitu/*.png "C:\Users\admin\Projects\xhs-image-filter\output\processed/"
rm C:\Users\admin\Projects\xhs-image-filter\output\filtered/*.png
```

---

## ⚙️ 配置说明

### 输入目录（自动读取）
```
C:\Users\admin\Projects\xhs-image-filter\output\filtered
```

### 输出目录（自动保存）
```
C:\Users\admin\Projects\xhs-image-filter\output\processed
```

### ComfyUI 配置
- **API地址**: http://192.168.11.158:8188
- **工作流**: z洗图1222api.json
- **ComfyUI输出**: D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\output\

---

## 📊 工作流程对比

### 旧流程
```
下载 → 筛选 → 洗图 → 保存到 D:\output\xitu\
                    ↑
                手动移动文件
```

### 新流程 ✨
```
下载 → 筛选(filtered/) → 洗图 → 自动保存到 processed/
                         ↑
                    自动移除原文件
```

---

## 🎯 优势

1. **自动化**: 一键完成洗图+移动
2. **清理有序**: filtered/ 自动清空，只保留未处理的
3. **集中管理**: 所有素材统一在 `xhs-image-filter/output/` 目录
4. **进度可见**: 实时显示每张图片的处理状态
5. **防重复**: 处理过的图片自动移除，不会重复处理

---

## 💡 使用示例

### 示例1：处理所有筛选素材

```bash
cd C:\Users\admin\projects\xhs-comfyui-wash
python wash_and_move.py
```

**输出**：
```
============================================================
ComfyUI洗图 - 筛选素材工作流
============================================================
输入目录: C:\Users\admin\Projects\xhs-image-filter\output\filtered
输出目录: C:\Users\admin\Projects\xhs-image-filter\output\processed
待处理图片: 44 张
LoRA: xiaolian_000001800.safetensors (强度: 0.8)
============================================================

[1/44] 2025-12-24_15.06.51_nonokiti_694b910b000000000d00c626_1.png
  [加载图片] ...
  [LoRA] xiaolian_000001800.safetensors (强度: 0.8)
  任务ID: 12345678...
  ✅ 已保存: 2025-12-24_15.06.51_nonokiti_694b910b000000000d00c626_1.png
  ✅ 原文件已移除

[2/44] ...
```

---

## 🔧 故障排除

**问题1: filtered 目录为空**
- 检查筛选是否完成
- 运行: `python xhs-filter filter <下载目录> --min-ratio 0.02`

**问题2: ComfyUI 未运行**
- 启动: `python start_comfyui.py`
- 等待启动完成

**问题3: 处理后找不到文件**
- 检查: `C:\Users\admin\Projects\xhs-image-filter\output\processed\`
- 应该包含处理后的图片

---

## 📈 进度跟踪

**处理前**:
```
filtered/: 44 张 ✅
processed/: 0 张
```

**处理中**:
```
filtered/: 30 张 ⏳
processed/: 14 张 ✅
```

**处理后**:
```
filtered/: 0 张 ✅
processed/: 44 张 ✅
```

---

**准备就绪！使用新工作流处理筛选后的素材。**
