# 小红书爬虫

从小红书搜索并采集眼镜相关笔记的标题和正文。

## 版本说明

- **V1.0**: 基础版本，直接从列表页提取
- **V2.0**: 改进版本，先收集链接再提取详情，更稳定
- **V3.0**: ⭐推荐版本，深度人工模拟，最强反爬能力

## 功能特性

- ✓ 模拟人工操作，使用Playwright自动化
- ✓ 支持扫码登录，自动保存cookies
- ✓ 自动滚动加载更多内容
- ✓ 提取笔记标题和正文
- ✓ 支持JSON和CSV格式导出
- ✓ 反爬虫检测规避
- ✓ 多种页面选择器，提高成功率
- ✓ 链接去重和数据验证

## 快速开始

### Windows用户

**V3推荐（深度人工模拟）：**
```bash
run_v3.bat
```

**V2标准版：**
```bash
run.bat
```

### Linux/Mac用户

```bash
# V3推荐
python crawler_v3.py

# V2标准版
python crawler_v2.py
```

## 版本选择

需要帮助选择版本？查看 [VERSIONS.md](VERSIONS.md) - 详细的版本对比和选择指南

## 手动安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

安装Playwright浏览器：

```bash
playwright install chromium
```

### 2. 修改配置

编辑 `config.py` 文件，修改以下参数：

```python
SEARCH_KEYWORD = "眼镜"  # 搜索关键词
TARGET_COUNT = 100       # 需要采集的笔记数量
HEADLESS = False         # 是否使用无头模式（False可以看到浏览器界面）
```

### 3. 运行爬虫（推荐V2版本）

```bash
python crawler_v2.py
```

V2版本特点：
- 先收集所有笔记链接
- 再逐个提取详情
- 支持断点续传（已采集的URL不会重复采集）
- 更好的错误恢复机制

### 3. 登录流程

如果是第一次运行，程序会：

1. 打开浏览器窗口（headless=False时）
2. 导航到小红书登录页面
3. 显示二维码
4. 等待你使用小红书APP扫码登录
5. 登录成功后自动保存cookies

之后运行时会自动使用保存的cookies，无需重复登录。

## 输出文件

采集的数据会保存在 `output` 目录下：

- `notes_YYYYMMDD_HHMMSS.json` - JSON格式
- `notes_YYYYMMDD_HHMMSS.csv` - CSV格式（推荐使用Excel打开）

## 数据格式

每条笔记包含以下字段：

```json
{
  "title": "笔记标题",
  "content": "笔记正文内容",
  "url": "笔记链接",
  "crawl_time": "2026-01-05 19:59:00"
}
```

## 使用技巧

### 1. 第一次使用

首次运行需要扫码登录：

```
1. 运行 python crawler_v2.py
2. 等待浏览器打开并显示登录页面
3. 使用小红书APP扫描二维码
4. 登录成功后自动保存cookies
5. 开始自动采集
```

### 2. 后续使用

cookies已保存，直接运行即可：

```bash
python crawler_v2.py
```

### 3. 遇到登录失效

如果出现未登录提示：

```bash
# 删除cookies.json文件
rm cookies.json  # Linux/Mac
del cookies.json  # Windows

# 重新运行，会提示扫码登录
python crawler_v2.py
```

### 4. 调整采集速度

如果采集过快被限制，修改 `config.py`：

```python
REQUEST_DELAY = 3  # 增加到3秒
SCROLL_DELAY = 2   # 增加到2秒
```

### 5. 更换关键词

修改 `config.py` 中的关键词：

```python
SEARCH_KEYWORD = "墨镜"  # 改为墨镜
SEARCH_KEYWORD = "近视眼镜"  # 改为近视眼镜
```

## 注意事项

1. **反爬机制**：小红书有反爬机制，请遵守以下规则：
   - 不要频繁请求，默认设置了2秒间隔
   - 使用真实的用户代理
   - 不要一次性采集过多数据

2. **登录状态**：
   - cookies会自动保存在 `cookies.json` 文件中
   - 如果cookies失效，需要重新登录
   - 建议定期更新cookies

3. **法律合规**：
   - 仅用于个人学习和研究
   - 不得用于商业用途
   - 请遵守小红书的使用条款

## 故障排除

### 问题：采集不到数据

**解决方案**：
- 检查是否已登录
- 检查关键词是否正确
- 尝试增加请求延迟（config.py中的REQUEST_DELAY）
- 尝试调整浏览器窗口大小

### 问题：登录失败

**解决方案**：
- 删除 `cookies.json` 文件重新登录
- 确保网络连接正常
- 尝试关闭VPN

### 问题：浏览器闪退

**解决方案**：
- 检查Playwright是否正确安装
- 尝试使用无头模式：HEADLESS = True
- 检查系统资源是否充足

## 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| SEARCH_KEYWORD | 搜索关键词 | "眼镜" |
| TARGET_COUNT | 目标采集数量 | 100 |
| OUTPUT_DIR | 输出目录 | ./output |
| COOKIE_FILE | Cookie保存路径 | ./cookies.json |
| REQUEST_DELAY | 请求延迟（秒） | 2 |
| SCROLL_DELAY | 滚动延迟（秒） | 1 |
| HEADLESS | 无头模式 | False |

## 技术栈

- **Playwright**: 浏览器自动化框架
- **Python 3.8+**: 编程语言
- **fake-useragent**: 用户代理生成

## 相关文档

- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [VERSIONS.md](VERSIONS.md) - 版本选择和对比
- [V3_GUIDE.md](V3_GUIDE.md) - V3版本详细说明
- [FILES.md](FILES.md) - 文件结构说明
- [SUMMARY.md](SUMMARY.md) - 项目总结

## 免责声明

本工具仅用于技术研究和学习目的。使用本工具采集数据时，请遵守目标网站的使用条款和相关法律法规。开发者不对使用本工具造成的任何后果负责。

---

*如有问题或建议，欢迎反馈*
