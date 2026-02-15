---
name: xiaohongshu-ai-workflow
description: 小红书端到端内容工作流：从数据采集到AI分析到内容生成，使用Kimi K2模型。支持爬虫、分析、笔记生成和AI配图提示词生成。
---

# 小红书AI工作流 Skill

你好！我是小红书内容创作工作流助手。

---

## 📋 工作流程

请严格按照以下步骤执行：

| 步骤 | 说明 | 详细指引 |
|:---:|:---:|:---|
| 1️⃣ | 数据采集 | [workflow/step1-数据采集.md](workflow/step1-数据采集.md) |
| 2️⃣ | 数据分析 | [workflow/step2-数据分析.md](workflow/step2-数据分析.md) |
| 3️⃣ | 笔记生成 | [workflow/step3-笔记生成.md](workflow/step3-笔记生成.md) |
| 4️⃣ | 保存笔记 | [workflow/step4-保存笔记.md](workflow/step4-保存笔记.md) |
| 5️⃣ | 配图提示词生成 | [workflow/step5-配图提示词.md](workflow/step5-配图提示词.md) |

---

## ⚠️ 执行前必读

**在开始任何步骤前，请务必阅读：**
- [rules/小红书风格配图要求.md](rules/小红书风格配图要求.md) - 配图提示词核心要求
- [rules/禁止事项.md](rules/禁止事项.md) - 文案和配图禁止项
- [rules/ComfyUI配置.md](rules/ComfyUI配置.md) - ComfyUI集成配置说明

---

## 📚 参考资料

**知识库（按需查阅）：**
- [references/配图提示词示例.md](references/配图提示词示例.md) - 6个生活感提示词示例
- [references/ComfyUI集成指南.md](references/ComfyUI集成指南.md) - ComfyUI工作流详解
- [references/版本历史.md](references/版本历史.md) - 更新日志和未来计划

**输出模板：**
- [templates/笔记输出格式.md](templates/笔记输出格式.md) - JSON和TXT输出格式
- [templates/配图提示词模板.md](templates/配图提示词模板.md) - 提示词输出格式

---

## 📁 输出位置

### 笔记输出
- **JSON格式**：`D:\xiaohongshu-crawler\output\kimi_generated_notes_关键词.json`
- **TXT格式**：`D:\xiaohongshu-crawler\output\kimi_generated_notes_关键词.txt`

### 配图提示词输出
- **TXT格式**：`D:\xiaohongshu-crawler\output\image_prompts_关键词.txt`

---

## 🚀 快速开始

### 完整工作流
```
用户：帮我生成"方圆脸眼镜"主题的小红书笔记
执行：数据采集 → 数据分析 → 笔记生成 → 保存笔记 → 配图提示词生成
```

### 仅生成笔记
```
用户：只生成笔记，不生成配图提示词
执行：数据采集 → 数据分析 → 笔记生成 → 保存笔记
```

### 仅生成配图提示词
```
用户：已有一批笔记，只生成配图提示词
执行：从笔记中提取信息 → 配图提示词生成
```

---

## ⭐ 重要提醒

**配图提示词生成注意事项**：
- ✅ 一篇笔记生成1个提示词
- ✅ 强调真实生活感、iPhone直出质感
- ✅ 穿搭必须与笔记描述一致
- ❌ **绝对禁止**在提示词中描述眼镜
- ❌ 避免摆拍感、关键词堆砌

**ComfyUI配置注意事项**：
- ✅ 初始分辨率必须为 `960x1280`
- ✅ 使用 `largest_size` 参数（不是 `max_dimension`）
- ✅ 确保放大修复链路正常工作

---

**准备就绪！告诉我你要生成的小红书笔记主题或关键词。**
