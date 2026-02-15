# AI驱动的小红书采集与生成 - 使用指南

## 概述

本系统支持在不同阶段使用不同的AI模型：

- **采集阶段**：使用 GLM-4（智谱AI）进行智能辅助
- **分析阶段**：使用 Kimi K2（Moonshot AI）分析数据
- **生成阶段**：使用 Kimi K2（Moonshot AI）生成笔记

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置API密钥

#### 方法1：使用环境变量（推荐）

**Windows (PowerShell):**
```powershell
# 设置GLM-4密钥
$env:ZHIPU_API_KEY="your_zhipu_api_key_here"

# 设置Kimi K2密钥
$env:MOONSHOT_API_KEY="your_moonshot_api_key_here"

# 永久设置（需管理员权限）
[System.Environment]::SetEnvironmentVariable("ZHIPU_API_KEY", "your_key", "User")
[System.Environment]::SetEnvironmentVariable("MOONSHOT_API_KEY", "your_key", "User")
```

**Windows (CMD):**
```cmd
set ZHIPU_API_KEY=your_zhipu_api_key_here
set MOONSHOT_API_KEY=your_moonshot_api_key_here
```

**Linux/Mac:**
```bash
export ZHIPU_API_KEY=your_zhipu_api_key_here
export MOONSHOT_API_KEY=your_moonshot_api_key_here

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export ZHIPU_API_KEY="your_key"' >> ~/.bashrc
echo 'export MOONSHOT_API_KEY="your_key"' >> ~/.bashrc
```

#### 方法2：创建 .env 文件

```bash
cd D:\xiaohongshu-crawler
cp .env.ai.example .env
# 编辑 .env 文件，填入实际的API密钥
```

### 3. 获取API密钥

#### GLM-4 API（智谱AI）
1. 访问：https://open.bigmodel.cn/
2. 注册/登录账号
3. 创建应用，获取API Key
4. 首次使用可能有免费额度

#### Kimi K2 API（Moonshot AI）
1. 访问：https://platform.moonshot.cn/
2. 注册/登录账号
3. 在控制台获取API Key
4. 新用户通常有免费额度

## 使用方法

### 方法1：完整工作流（推荐）

运行完整的采集+分析+生成流程：

```bash
cd D:\xiaohongshu-crawler
python ai_workflow.py "眼镜框推荐女"
```

指定采集和生成数量：

```bash
python ai_workflow.py "眼镜框推荐女" --crawl 10 --generate 5
```

交互模式（运行后按提示输入）：

```bash
python ai_workflow.py
```

### 方法2：分步执行

#### 步骤1：运行爬虫（采集阶段）

```bash
cd D:\xiaohongshu-crawler
python search_xhs.py "眼镜框推荐女" 10
```

#### 步骤2：使用AI生成笔记（分析和生成阶段）

```bash
python ai_note_generator.py
```

### 方法3：单独测试AI功能

#### 测试GLM-4（采集阶段）

```python
from ai_config import AIModelConfig

config = AIModelConfig.get_full_config("采集阶段")
print(f"模型: {config['model']}")
print(f"说明: {config['description']}")
```

#### 测试Kimi K2（分析和生成）

```python
from ai_note_generator import AIXHSNoteGenerator

# 创建生成器
generator = AIXHSNoteGenerator("眼镜框推荐女", use_ai=True)

# 生成笔记（需要已有数据）
notes = generator.generate_batch(notes_data, count=5)
```

## 文件说明

### 核心文件

- **ai_config.py** - AI模型配置管理
  - 定义GLM-4和Kimi K2的配置
  - 管理不同阶段使用哪个模型
  - API密钥管理

- **ai_note_generator.py** - AI驱动的笔记生成器
  - 使用Kimi K2分析采集的数据
  - 使用Kimi K2生成新笔记
  - 支持批量生成

- **ai_workflow.py** - 完整工作流脚本
  - 整合采集、分析、生成三个阶段
  - 自动选择合适的模型
  - 提供交互式命令行界面

- **generate_notes.py** - 模板生成器（原有）
  - 基于预设模板生成笔记
  - 不需要AI模型
  - 快速生成基础内容

### 配置文件

- **.env.ai.example** - API密钥配置示例
- **.env** - 实际使用的环境变量（需要自己创建）

### 输出文件

- **output/notes_*.json** - 采集的原始数据
- **output/ai_generated_*.json** - AI生成的笔记
- **output/ai_generated_*.txt** - AI生成的笔记（可读格式）

## 模型配置详解

### GLM-4配置（采集阶段）

```python
GLM4_CONFIG = {
    "model": "glm-4-plus",  # glm-4-plus, glm-4-flash, glm-4-air
    "temperature": 0.3,    # 低温度，保持准确性
    "max_tokens": 2000,     # 响应长度
    "timeout": 30          # 超时时间
}
```

**用途：**
- 优化搜索关键词
- 识别热门笔记
- 智能筛选数据

### Kimi K2配置（分析和生成阶段）

```python
KIMI_K2_CONFIG = {
    "model": "kimi-k2",    # Moonshot最新模型
    "temperature": 0.8,    # 较高温度，增加创意性
    "max_tokens": 4000,     # 响应长度
    "timeout": 60          # 超时时间
}
```

**用途：**
- 分析采集数据的趋势和特点
- 提取热门标签和话题
- 生成高质量的笔记内容

## 工作流程

```
用户输入关键词
      ↓
【阶段1】数据采集（GLM-4辅助）
      ↓
调用小红书爬虫
      ↓
保存采集数据（notes_*.json）
      ↓
【阶段2】数据分析（Kimi K2）
      ↓
分析热门标签、主题、语气
      ↓
提取关键特点和痛点
      ↓
【阶段3】笔记生成（Kimi K2）
      ↓
生成多篇笔记内容
      ↓
保存生成结果（ai_generated_*.json）
      ↓
完成
```

## 示例输出

### 采集数据示例 (notes_*.json)

```json
[
  {
    "keyword": "眼镜框推荐女",
    "title": "方圆脸女生必看！这3款眼镜框绝了",
    "content": "玳瑁色方圆框，韩系文艺范...",
    "likes": 5000,
    "author": "小红书达人",
    "collected_at": "2026-01-06 18:37:24"
  }
]
```

### AI生成结果示例 (ai_generated_*.json)

```json
[
  {
    "type": "经验分享",
    "title": "方圆脸姐妹必看！这3款眼镜框绝了✨",
    "content": "方圆脸选眼镜真的太难了😭但我也终于找到了！\n\n🔸玳瑁色方圆框：韩系文艺范...",
    "tags": ["#方圆脸", "#眼镜推荐", "#显脸小眼镜框"],
    "generated_at": "2026-01-06 18:50:00",
    "model": "kimi-k2"
  }
]
```

## 常见问题

### Q1: 为什么采集阶段用GLM-4，生成阶段用Kimi K2？

**A:** 不同模型有不同优势：
- GLM-4：准确性和稳定性好，适合数据处理和筛选
- Kimi K2：创意和语言表达能力强，适合内容创作

### Q2: 可以只使用其中一个模型吗？

**A:** 可以。系统支持灵活配置：
- 只配置GLM-4：可运行采集阶段
- 只配置Kimi K2：可运行分析和生成阶段（需提供已有数据）

### Q3: API调用失败怎么办？

**A:** 检查以下几点：
1. API密钥是否正确
2. 网络连接是否正常
3. API账户是否有足够额度
4. 查看控制台错误信息

### Q4: 如何降低API调用成本？

**A:**
1. 使用模板生成器（generate_notes.py）不消耗API
2. 调整temperature参数减少调用次数
3. 批量生成而非单次生成
4. 使用免费额度和新用户优惠

### Q5: 生成的笔记质量如何提升？

**A:**
1. 采集更多高质量样本数据
2. 调整temperature参数（0.7-0.9更创意，0.3-0.5更稳定）
3. 优化prompt提示词
4. 提供更详细的分析数据

## 进阶用法

### 自定义模型配置

编辑 `ai_config.py` 修改模型参数：

```python
GLM4_CONFIG = {
    "model": "glm-4-plus",  # 改为其他模型
    "temperature": 0.5,     # 调整温度
    "max_tokens": 3000,     # 调整长度
    # ...
}
```

### 扩展功能

- 添加更多分析维度
- 支持多语言生成
- 集成图像生成模型
- 添加内容审核功能

## 技术支持

遇到问题？

1. 查看本文档的常见问题部分
2. 检查输出日志中的错误信息
3. 确认API密钥配置正确
4. 测试网络连接和API可用性

## 更新日志

- **v1.0** (2026-01-06)
  - 初始版本
  - 支持GLM-4和Kimi K2模型
  - 实现完整工作流

---

*最后更新: 2026-01-06*
