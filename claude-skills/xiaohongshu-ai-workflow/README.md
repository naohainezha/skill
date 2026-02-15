# 小红书AI工作流 Skill

## 📖 简介

这是一个完整的小红书内容创作自动化skill，集成了数据采集、AI分析和内容生成三大功能。

### 核心特点

✅ **完整流程**: 采集 → 分析 → 生成，一站式解决方案
✅ **多模型协同**: 使用Kimi K2进行数据分析和内容创作
✅ **高质量输出**: 基于真实数据分析，生成符合小红书风格的笔记
✅ **可复用性**: 结构化输出，方便后续使用

## 🚀 快速开始

### 基础用法

用户请求示例：
> "在小红书搜索眼镜框推荐女 采集10篇 然后生成3篇笔记"

系统会自动执行：
1. 采集10篇笔记数据
2. 使用Kimi K2分析数据
3. 使用Kimi K2生成3篇笔记
4. 保存所有结果

### 扩展用法：生成AI绘画提示词 [NEW - Flux/QwenImage风格]

用户请求示例：
> "为刚才生成的小红书笔记生成AI绘画提示词"

系统会自动执行：
1. 读取生成的笔记文件
2. 使用Kimi K2为每篇笔记生成3-5个AI绘画提示词
3. 保存提示词到JSON和TXT文件
4. 提示词适用于Flux/QwenImage/Midjourney等AI绘画工具

### Flux/QwenImage风格特点

**【自然语言段落式】**
- ✅ 不是关键词列表，而是完整的段落描述
- ✅ 细节丰富：包含场景、人物动作、情绪、光影
- ✅ 中英文双版本：方便不同AI工具使用

**【小红书风格优化】**
- 🌟 温暖柔和的光线（避免强烈对比）
- 💄 自然清新的妆容（不过度夸张）
- 👔 日常精致的穿搭（不张扬）
- 🏠️ 生活化的场景（咖啡店、图书馆等）
- 😊 温暖治愈的笑容和氛围
- 🎨 "生活美学"的整体感觉

**【适用工具】**
- 🎨 **Flux**（推荐）：优秀国产AI绘画工具
- 🎨 **QwenImage**：优秀国产AI绘画工具  
- Midjourney v6
- Stable Diffusion
- DALL-E 3

### 支持的触发词

- "在小红书搜索XXX并生成笔记"
- "采集小红书XXX并分析生成"
- "小红书AI工作流XXX"
- "小红书数据分析XXX"
- "为小红书笔记生成配图提示词"

## 📊 工作流程

```
用户输入关键词和数量
       ↓
【阶段1】数据采集
       ↓
使用小红书爬虫采集数据
       ↓
输出: notes_*.json
       ↓
【阶段2】AI数据分析
       ↓
使用Kimi K2分析数据
       ↓
提取: 热门标签、内容风格、语气特点
       ↓
【阶段3】内容生成
       ↓
使用Kimi K2生成笔记
       ↓
输出: kimi_generated_notes.json/.txt
       ↓
【阶段4】AI绘画提示词（NEW）
       ↓
使用Kimi K2生成AI绘画提示词
       ↓
输出: image_prompts_*.json/.txt
       ↓
完成
```

## 📁 文件结构

```
D:\xiaohongshu-crawler\
├── crawler_v4.py              # 主爬虫脚本
├── image_prompt_generator.py   # AI绘画提示词生成器（NEW）
└── output/
    ├── notes_*.json            # 采集的原始数据
    ├── kimi_generated_notes*.json  # AI生成的笔记
    ├── kimi_generated_notes*.txt   # AI生成的笔记（可读格式）
    └── image_prompts_*.json     # AI绘画提示词（NEW）
```

```
D:\skills\xiaohongshu-ai-workflow\
├── SKILL.md                    # Skill说明文档
├── README.md                   # 本文件
└── examples/                   # 示例输出
    ├── 眼镜镜片的选择/
    │   ├── analysis.md         # AI分析报告
    │   ├── notes.json          # 生成的笔记（JSON格式）
    │   ├── notes.txt           # 生成的笔记（可读格式）
    │   └── image_prompts.json  # AI绘画提示词（NEW）
    └── 眼镜穿搭/
        ├── analysis.md         # AI分析报告
        ├── notes.json          # 生成的笔记（JSON格式）
        └── notes.txt           # 生成的笔记（可读格式）
```
D:\skills\xiaohongshu-ai-workflow\
├── SKILL.md                    # Skill说明文档
├── README.md                   # 本文件
└── examples/                   # 示例输出
    └── 眼镜镜片的选择/
        ├── analysis.md         # AI分析报告
        ├── notes.json          # 生成的笔记（JSON格式）
        └── notes.txt           # 生成的笔记（可读格式）
```

## 🎯 使用场景

### 1. 品牌营销

**场景**: 推广某个眼镜品牌

**输入**: "在小红书搜索XXX品牌眼镜 采集15篇并生成5篇笔记"

**输出**: 基于竞品分析，生成5篇推广笔记

### 2. 内容创作

**场景**: 需要定期发布小红书内容

**输入**: "小红书AI工作流：秋季护肤 采集10篇生成3篇"

**输出**: 3篇符合秋季护肤主题的高质量笔记

### 3. 市场调研

**场景**: 了解某个话题的热门内容和趋势

**输入**: "采集小红书关于XXX的笔记并分析"

**输出**: 详细的AI分析报告（热门标签、内容风格等）

## 🔧 配置说明

### 模型配置

| 阶段 | 模型 | API密钥 | 参数 |
|------|------|---------|------|
| 采集 | 爬虫 | 无 | - |
| 分析 | Kimi K2 | MOONSHOT_API_KEY | temperature: 0.8 |
| 生成 | Kimi K2 | MOONSHOT_API_KEY | temperature: 0.8 |

### API密钥配置

Kimi K2的API密钥已在opencode中配置，无需手动设置。

## 📝 输出格式

### 分析报告 (analysis.md)

包含以下信息：
- 采集数据概况
- 热门标签汇总
- 内容风格分析
- 语气特点
- 目标人群画像
- 生成内容建议

### 生成的笔记 (notes.json)

JSON格式，每篇笔记包含：
```json
{
  "type": "笔记类型",
  "title": "笔记标题",
  "content": "笔记内容",
  "tags": ["#标签1", "#标签2"],
  "generated_at": "生成时间",
  "model": "Kimi K2"
}
```

### 可读格式 (notes.txt)

纯文本格式，便于直接复制使用。

### AI绘画提示词 (image_prompts.json) [NEW]

JSON格式，每篇笔记包含3-5个AI绘画提示词：

```json
{
  "note_index": 1,
  "note_title": "笔记标题",
  "prompts": [
    "Asian young woman, white shirt, black wide frame glasses, professional business style, office background, natural lighting, high quality, 8k, detailed, photorealistic",
    "Young woman, beige knitwear, round metal glasses, soft lighting, coffee shop background, gentle smile, portrait, 4k, detailed"
  ],
  "model": "Kimi K2"
}
```

**提示词特点**:
- 包含人物描述（年轻女性、气质）
- 眼镜描述（形状、颜色、材质）
- 穿搭描述（服装、颜色、风格）
- 场景描述（环境、光线、氛围）
- 拍摄角度（正面、侧颜、半身）
- 风格描述（高智感、韩系、清新、复古）
- 画质要求（高清、光线柔和、细节丰富）

**适用工具**:
- Midjourney
- Stable Diffusion
- DALL-E 3
- 其他AI绘画工具

### AI绘画提示词 (image_prompts.txt) [NEW]

纯文本格式，便于直接复制到AI绘画工具。

## 💡 最佳实践

### 1. 关键词选择

✅ **好的关键词**:
- 具体的产品类别（如"蔡司镜片"）
- 明确的使用场景（如"学生党配镜"）
- 热门的话题标签（如"显脸小眼镜"）

❌ **避免的关键词**:
- 过于宽泛（如"眼镜"）
- 包含敏感词
- 不符合小红书话题风格

### 2. 采集数量建议

- **初次使用**: 10-15篇
- **深度分析**: 20-30篇
- **快速生成**: 5-10篇

### 3. 生成数量建议

- **日常内容**: 3-5篇
- **营销活动**: 5-10篇
- **内容库建设**: 10-20篇

### 4. 质量控制

生成后建议人工检查：
- 内容准确性
- 品牌合规性
- 风格一致性
- 标签相关性

## 🔄 与其他Skill的配合

### 配合 xiaohongshu-crawler

本skill内部使用xiaohongshu-crawler进行数据采集，无需额外调用。

### 配合 内容发布工具

生成的JSON格式可轻松导入内容管理系统：
```python
import json

with open('kimi_generated_notes.json', 'r', encoding='utf-8') as f:
    notes = json.load(f)

for note in notes:
    # 发布到小红书平台
    publish_to_xiaohongshu(note)
```

## 🐛 故障排除

### 问题1: 采集失败

**症状**: 爬虫报错或无法登录

**解决方案**:
1. 检查cookies.json是否过期
2. 删除cookies.json重新登录
3. 检查网络连接

### 问题2: 分析结果为空

**症状**: AI分析没有输出或质量差

**解决方案**:
1. 确认采集数据有足够内容
2. 检查API密钥是否配置
3. 调整prompt提示词

### 问题3: 生成质量不满意

**症状**: 生成的笔记不符合预期

**解决方案**:
1. 增加采集数量（更多数据=更好分析）
2. 调整temperature参数（0.7-0.9更创意）
3. 提供更详细的生成要求
4. 人工修改和优化

## 📊 性能指标

基于实际使用测试：

- **采集速度**: 约2-3秒/篇
- **分析时间**: 约10-20秒
- **生成时间**: 约15-30秒/篇
- **总耗时**: 约2-3分钟（10篇采集+3篇生成）

## 📈 版本历史

### V1.0 (2026-01-06)
- ✅ 初始版本
- ✅ 集成Kimi K2模型
- ✅ 实现完整工作流
- ✅ 提供示例输出

## 🔗 相关资源

- **小红书爬虫**: `D:\skills\xiaohongshu-crawler`
- **AI配置**: `D:\xiaohongshu-crawler\ai_config.py`
- **使用指南**: `D:\xiaohongshu-crawler\AI使用指南.md`

## 💬 反馈与支持

如有问题或建议，请：
1. 查看本文档的故障排除部分
2. 参考示例输出了解预期格式
3. 检查SKILL.md中的详细说明

## 📈 版本历史

### V1.1 (2026-01-06) - NEW FEATURE
- ✅ 新增：AI绘画提示词生成功能（Stage 4）
- ✅ 新增：image_prompt_generator.py脚本
- ✅ 支持为每篇笔记生成3-5个AI绘画提示词
- ✅ 提示词适用于Midjourney/Stable Diffusion等工具
- ✅ 输出JSON和TXT双格式

### V1.0 (2026-01-06)
- ✅ 初始版本
- ✅ 集成Kimi K2模型
- ✅ 实现完整工作流
- ✅ 提供示例输出

---

*Skill创建时间: 2026-01-06*
*最后更新: 2026-01-06*
*维护者: opencode*
