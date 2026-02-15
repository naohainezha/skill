# 第一步：前置条件检查

## ⚠️ 重要：先确认使用场景

**本工具只支持单条作品链接下载。**

如果你需要**批量下载博主的多篇笔记**，请直接使用 **xhs-batch-downloader**：
```bash
cd C:\Users\admin\Projects\xhs-batch-downloader
python cli.py download <博主ID> --count 10
```

详细指引：[批量下载指引.md](./批量下载指引.md)

---

## 你的任务

在执行下载前，确认环境配置正确。

## 检查清单

### 1. 项目位置
确认 XHS-Downloader 项目存在于：
```
C:\Users\admin\Projects\XHS-Downloader\
```

### 2. 依赖安装
确认以下依赖已安装：
- aiofiles
- aiosqlite
- click
- emoji
- fastapi
- fastmcp
- httpx
- lxml
- pyperclip
- pyyaml
- textual
- uvicorn
- websockets

**注意**：`rookiepy` 模块为可选依赖，不影响下载功能。

### 3. 工作目录
确认工作目录存在：
```
C:\Users\admin\Projects\XHS-Downloader\Volume\
```

## 完成标志

当所有检查项通过后，进入下一步。

## 参考资源

- 配置说明：[rules/配置说明.md](../rules/配置说明.md)
- 常见问题：[references/常见问题.md](../references/常见问题.md)
