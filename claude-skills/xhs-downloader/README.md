# XHS-Downloader Skill

小红书作品下载工具 - 提取作品信息、下载无水印图片和视频

## 功能特性

- ✅ 提取小红书作品元数据（标题、作者、标签、互动数据）
- ✅ 下载无水印图片（支持 PNG/JPEG/WEBP/HEIC 格式）
- ✅ 下载无水印视频
- ✅ 支持图文作品指定图片序号下载
- ✅ 自动跳过已下载作品
- ✅ 无需登录即可使用

## 支持的链接格式

- `https://www.xiaohongshu.com/explore/作品ID`
- `https://www.xiaohongshu.com/discovery/item/作品ID`
- `https://www.xiaohongshu.com/user/profile/作者ID/作品ID`
- `https://xhslink.com/分享码`

## 快速开始

### 基础用法

下载小红书作品：

```
用户：下载这个小红书作品 https://www.xiaohongshu.com/discovery/item/6954ec6700000000220329a6
```

Skill 会自动：
1. 提取作品信息
2. 下载所有无水印文件
3. 返回下载位置

### 高级用法

#### 仅获取作品信息（不下载文件）

```
用户：获取这个作品的信息，不要下载 https://www.xiaohongshu.com/explore/xxx
```

#### 指定下载部分图片

```
用户：只下载第1、3、5张图片 https://www.xiaohongshu.com/discovery/item/xxx
```

## 下载位置

默认下载路径：
```
C:\Users\admin\Projects\XHS-Downloader\Volume\Download\
```

文件命名格式：
```
发布时间_作者昵称_作品标题_序号.扩展名
例：2025-12-31_17.29.01_Ruuu_我的年度18张图_1.png
```

## 项目结构

```
C:\Users\admin\Projects\XHS-Downloader\
├── source\                 # 源代码
│   ├── application\       # 核心应用
│   ├── expansion\         # 扩展功能（浏览器 Cookie 读取）
│   ├── module\            # 数据提取、下载管理
│   └── translation\      # 国际化
├── Volume\                 # 工作目录
│   ├── Download\          # 下载文件
│   ├── ExploreData.db     # 作品数据
│   ├── ExploreID.db       # 下载记录
│   └── settings.json      # 配置文件
└── main.py                # 程序入口
```

## 配置说明

配置文件：`Volume/settings.json`

主要参数：
- `work_path`: 工作目录
- `folder_name`: 下载文件夹名称（默认 Download）
- `name_format`: 文件命名格式
- `image_format`: 图片格式（PNG/WEBP/JPEG/HEIC）
- `image_download`: 是否下载图片
- `video_download`: 是否下载视频
- `download_record`: 是否记录下载历史

## 返回数据格式

```python
[
  {
    "收藏数量": "1543",
    "评论数量": "1239",
    "点赞数量": "1901",
    "分享数量": "1.3万",
    "作品标签": "#旅行 #美食",
    "作品ID": "6954ec6700000000220329a6",
    "作品链接": "https://www.xiaohongshu.com/explore/xxx",
    "作品标题": "我的年度18张图",
    "作品描述": "#旅行[地点]#",
    "作品类型": "图文",
    "发布时间": "2025-12-31_17:29:01",
    "作者昵称": "Ruuu",
    "作者ID": "5c6fb3fb00000000110126a2",
    "作者链接": "https://www.xiaohongshu.com/user/profile/xxx",
    "下载地址": [
      "https://ci.xiaohongshu.com/notes_pre_post/xxx.png"
    ]
  }
]
```

## 常见问题

### 1. 依赖安装失败
`rookiepy` 模块已修改为可选依赖，不影响核心下载功能。

### 2. 下载文件已存在
程序默认启用下载记录，自动跳过已下载作品。删除 `ExploreID.db` 可清空记录。

### 3. 文件名乱码
确保终端支持 UTF-8 编码（Windows 10/11 默认支持）。

## 版本信息

- **Skill 版本**: 1.0.0
- **基于项目**: XHS-Downloader
- **最后更新**: 2026-01-23

## 技术栈

- Python 3.12+
- httpx (HTTP 客户端)
- lxml (HTML 解析)
- asyncio (异步 IO)

## 许可证

基于 XHS-Downloader 项目，遵循 GNU General Public License v3.0

## 相关链接

- XHS-Downloader: https://github.com/JoeanAmier/XHS-Downloader
