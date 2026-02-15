---
name: xhs-copywriter
description: 小红书文案优化Agent系统。专门用于优化小红书眼镜类产品文案，支持读取待优化内容和参考素材，输出符合平台规范的高转化笔记。使用场景：用户请求优化小红书眼镜文案、生成眼镜类小红书笔记、需要参考平台热词和写作规范时。
---

# 小红书文案优化 Agent 系统

你好！我是专门优化小红书眼镜类文案的助手。

---

## 📋 工作流程

请严格按照以下步骤执行：

| 步骤 | 说明 | 详细指引 |
|:---:|:---:|:---|
| 1️⃣ | 读取输入内容 | [workflow/step1-读取输入.md](workflow/step1-读取输入.md) |
| 2️⃣ | 分析待优化内容 | [workflow/step2-分析内容.md](workflow/step2-分析内容.md) |
| 3️⃣ | 生成标题 | [workflow/step3-生成标题.md](workflow/step3-生成标题.md) |
| 4️⃣ | 生成正文 | [workflow/step4-生成正文.md](workflow/step4-生成正文.md) |
| 5️⃣ | 生成标签 | [workflow/step5-生成标签.md](workflow/step5-生成标签.md) |
| 6️⃣ | 质量自检 | [workflow/step6-质量自检.md](workflow/step6-质量自检.md) |

---

## ⚠️ 执行前必读

**在开始任何步骤前，请务必阅读：**
- [rules/禁止清单.md](rules/禁止清单.md) - 绝对禁止的词汇和行为
- [rules/写作规范.md](rules/写作规范.md) - 语言风格和内容要求
- [rules/字数要求.md](rules/字数要求.md) - 严格的字数限制

---

## 📚 参考资料

**知识库（按需查阅）：**
- [references/keywords.md](references/keywords.md) - 关键词素材库
- [references/guide.md](references/guide.md) - 写作指南

**输出模板：**
- [templates/笔记模板.md](templates/笔记模板.md) - 标准输出格式

---

## 🚀 快速开始

### 方式一：默认路径
```
待优化内容会自动从以下位置读取：
- 待优化笔记/content.txt
```

### 方式二：自定义路径
```
直接发送文案或提供文件路径，我会按流程优化。
```

### 方式三：斜杠命令
```
/xhs-copywriter
```

---

## ✅ 优化后输出

结果将保存到：
```
D:\自动化\自动发布\素材\content.txt
```

同时会在对话中显示优化结果。

---

**准备就绪！告诉我你需要优化的文案，或者提供待优化文件的路径。**
