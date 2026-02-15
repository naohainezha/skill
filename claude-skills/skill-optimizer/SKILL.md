---
name: skill-optimizer
description: Skill 2.0 优化工具：将单文件 SKILL.md 优化为模块化架构，包含分析、设计、创建、重写和验证的完整工作流。使用场景：用户请求优化现有 skill，或将这个优化方法打包为可复用的 skill。
---

# Skill 2.0 优化器

你好！我是 Skill 2.0 架构优化助手。

---

## 📋 工作流程

请严格按照以下步骤执行：

| 步骤 | 说明 | 详细指引 |
|:---:|:---:|:---|
| 1️⃣ | 分析当前结构 | [workflow/step1-分析当前结构.md](workflow/step1-分析当前结构.md) |
| 2️⃣ | 识别问题和设计架构 | [workflow/step2-识别问题和设计架构.md](workflow/step2-识别问题和设计架构.md) |
| 3️⃣ | 创建目录结构 | [workflow/step3-创建目录结构.md](workflow/step3-创建目录结构.md) |
| 4️⃣ | 拆分内容 | [workflow/step4-拆分内容.md](workflow/step4-拆分内容.md) |
| 5️⃣ | 重写 SKILL.md | [workflow/step5-重写SKILL.md.md](workflow/step5-重写SKILL.md) |
| 6️⃣ | 验证功能 | [workflow/step6-验证功能.md](workflow/step6-验证功能.md) |

---

## ⚠️ 执行前必读

**在开始任何步骤前，请务必阅读：**
- [rules/架构模式.md](rules/架构模式.md) - Skill 2.0 架构类型和选择指南
- [rules/优化最佳实践.md](rules/优化最佳实践.md) - 优化原则和成功标准

---

## 📚 参考资料

**知识库（按需查阅）：**
- [templates/架构模板.md](templates/架构模板.md) - 工作流型/工具型 SKILL 模板

---

## 🚀 快速开始

### 场景一：优化现有 skill
```
用户：优化这个 skill C:\Users\admin\.claude\skills\my-skill
执行：步骤1 → 步骤2 → 步骤3 → 步骤4 → 步骤5 → 步骤6
```

### 场景二：创建新 skill 结构
```
用户：为新 skill 创建标准结构
执行：运行 scripts/init_skill_structure.py <skill-path>
```

---

## 📊 Skill 2.0 核心原则

### ✅ 六大原则

1. **轻量级总控**：SKILL.md 50-80 行
2. **显式工作流**：每个步骤独立文件（workflow/stepN-步骤名.md）
3. **规则集中化**：所有规则在 rules/ 目录集中管理
4. **参考资料独立**：详细文档在 references/ 按需加载
5. **模板系统化**：输出格式、脚本模板独立
6. **脚本可执行**：工具脚本可直接执行

### 📈 优化收益

- **上下文效率**：减少 50-70% 的初始加载
- **维护便利性**：小文件独立编辑，无需改大文件
- **可扩展性**：新增功能只需新增文件
- **错误防护**：规则集中 + 质量自检

---

## 📋 优化结果模板

优化完成后，生成以下报告：

```
✅ Skill 优化验证报告

优化结果：
- SKILL.md：[原行数] → [新行数]（↓[减少比例%]）
- 总文件数：[原文件数] → [新文件数]
- 上下文效率：↑[提升比例%]

文件清单：
- ✅ SKILL.md
- ✅ workflow/ ([数量] 个文件)
- ✅ rules/ ([数量] 个文件)
- ✅ references/ ([数量] 个文件)
- ✅ templates/ ([数量] 个文件)
- ✅ scripts/ ([数量] 个文件)

验证状态：
- ✅ 结构验证通过
- ✅ 链接验证通过
- ✅ 功能完整性验证通过

优化完成！
```

---

**准备就绪！告诉我你要优化的 skill 路径，或提供 SKILL.md 内容。**
