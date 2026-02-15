# XHS Batch Downloader Skill

小红书博主笔记批量下载器 - OpenCode Skill

## 快速开始

### 安装

```bash
# 进入 skill 目录
cd ~/.claude/skills/xhs-batch-downloader

# 运行安装脚本（可选）
bash install.sh

# 或手动安装依赖
pip install playwright httpx click rich
playwright install chromium
```

### 使用

```bash
# 方法1: 作为模块运行
cd src
python -m cli login
python -m cli add <博主ID>
python -m cli download <博主ID> --count 10

# 方法2: 直接运行
cd src
python cli.py login
python cli.py add <博主ID>
python cli.py download <博主ID> --count 10
```

## 项目结构

```
xhs-batch-downloader/
├── SKILL.md              # Skill 文档
├── README.md             # 本文件
├── install.sh            # 安装脚本
└── src/                  # 源代码
    ├── __init__.py
    ├── __main__.py
    ├── cli.py            # 命令行入口
    ├── login.py          # 登录模块
    ├── sign.py           # 签名模块
    ├── api_client.py     # API客户端
    ├── xhs_client.py     # 客户端封装
    ├── downloader.py     # 下载调度
    ├── database.py       # 数据库
    └── config.py         # 配置
```

## 完整文档

详见 [SKILL.md](./SKILL.md)

## 功能特点

- ✅ 自动二维码登录
- ✅ 博主管理和别名
- ✅ 批量下载笔记
- ✅ 智能去重
- ✅ 无水印下载

## 依赖

- Python 3.8+
- Playwright
- httpx
- click
- rich

## 许可证

仅供学习和研究使用
