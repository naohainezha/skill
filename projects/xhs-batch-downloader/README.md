# 小红书博主笔记批量下载器

🍰 通过博主ID批量下载小红书笔记，支持自动去重和博主管理。

## 功能特点

- ✅ **博主管理**：添加、删除、查看博主列表
- ✅ **批量下载**：一键下载博主的所有笔记
- ✅ **自动去重**：已下载的笔记自动跳过
- ✅ **下载数量控制**：可设置下载数量，有默认值
- ✅ **持久化存储**：下载记录和博主信息持久保存

## 系统要求

- Python 3.12+
- 已安装 XHS-Downloader
- 有效的小红书 Cookie

## 安装步骤

### 1. 安装依赖

```bash
cd C:\Users\admin\Projects\xhs-batch-downloader
pip install -r requirements.txt
```

### 2. 配置 Cookie（重要！）

有两种方式配置 Cookie：

**方式一**：更新 XHS-Downloader 的配置文件
```
C:\Users\admin\Projects\XHS-Downloader\Volume\settings.json
```
将 `"cookie": ""` 替换为你的小红书 Cookie。

**方式二**：更新浏览器导出的 cookies.json
```
C:\Users\admin\Projects\xhs-batch-downloader\cookies.json
```
使用浏览器扩展（如 EditThisCookie）导出小红书网站的 Cookie。

#### 如何获取 Cookie

1. 用 Chrome 打开 https://www.xiaohongshu.com 并登录
2. 按 F12 打开开发者工具
3. 切换到 Network（网络）标签
4. 刷新页面，点击任意一个请求
5. 在 Headers 中找到 `Cookie:` 字段，复制完整内容

### 3. 验证安装

```bash
python cli.py status
```

## 使用方法

### 博主管理

```bash
# 添加博主
python cli.py add <博主ID>
python cli.py add <博主ID> --alias "我的别名"

# 删除博主
python cli.py remove <博主ID>

# 查看博主列表
python cli.py list

# 设置别名
python cli.py alias <博主ID> "新别名"
```

### 下载笔记

```bash
# 下载指定博主的笔记（默认10个）
python cli.py download <博主ID>

# 下载指定数量
python cli.py download <博主ID> --count 20

# 下载所有笔记
python cli.py download <博主ID> --all

# 强制重新下载（忽略已下载记录）
python cli.py download <博主ID> --force

# 下载所有博主的笔记
python cli.py download-all
python cli.py download-all --count 5
```

### 系统状态

```bash
python cli.py status
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `add <博主ID>` | 添加博主 |
| `remove <博主ID>` | 删除博主 |
| `list` | 查看博主列表 |
| `alias <博主ID> <别名>` | 设置别名 |
| `download <博主ID>` | 下载指定博主笔记 |
| `download-all` | 下载所有博主笔记 |
| `status` | 检查系统状态 |

## 项目结构

```
xhs-batch-downloader/
├── cli.py           # 命令行入口
├── config.py        # 配置文件
├── database.py      # 博主数据库管理
├── xhs_client.py    # 小红书 API 客户端
├── downloader.py    # 下载调度模块
├── requirements.txt # 依赖列表
├── README.md        # 使用说明
└── data/
    └── bloggers.db  # 博主数据库
```

## 数据存储

- **博主数据库**：`data/bloggers.db`
- **下载记录**：复用 XHS-Downloader 的 `ExploreID.db`
- **下载文件**：`C:\Users\admin\XHS-Downloader\Volume\Download\`

## 常见问题

### Q: API 返回 code: -1 错误

这通常是 Cookie 过期导致的。请按照安装步骤重新配置 Cookie。

小红书的 Cookie 通常有效期为 7-30 天，过期后需要重新获取。

### Q: 如何获取博主ID？

1. 打开小红书网页版 https://www.xiaohongshu.com
2. 进入博主主页
3. URL 中的 `user/profile/` 后面的24位字符串即为博主ID

示例：`https://www.xiaohongshu.com/user/profile/5c6fb3fb00000000110126a2`

博主ID 为：`5c6fb3fb00000000110126a2`

### Q: 下载失败怎么办？

1. 检查 Cookie 是否有效：重新获取最新的 Cookie
2. 检查网络连接
3. 等待一段时间后重试（避免频率过高被限制）

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                   CLI 命令行界面                         │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  博主管理    │    │  笔记获取    │    │  作品下载    │  │
│  │  (SQLite)   │───▶│(ReaJason/xhs)│───▶│(XHS-Downloader)│
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              下载记录数据库 (SQLite)              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## 许可证

MIT License
