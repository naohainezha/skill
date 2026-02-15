---
name: instagram-downloader
description: Instagram图片批量下载工具。支持下载指定用户的所有图片帖子，自动处理限流和断点续传。使用场景：用户需要下载Instagram博主的所有图片、批量备份Instagram内容、需要带延迟控制的下载以避免触发平台限制。
---

# Instagram 图片批量下载器

专业的Instagram内容下载工具，支持两种下载方案。

## 🚀 下载方案选择

| 方案 | 适用场景 | 优点 | 缺点 |
|:---|:---|:---|:---|
| **方案A: instaloader** | 批量下载、无登录 | 速度快、自动化高 | 易触发限流 |
| **方案B: Playwright浏览器** | 限流绕过、登录账号 | 稳定、模拟真人 | 需手动操作 |

**推荐策略**：先尝试方案A，遇到401/403限流时切换方案B。

---

## 📋 方案A：instaloader 命令行

### 快速开始
```bash
# 直接下载（无需登录）
下载Instagram用户 moyuka_ 的所有图片

# 登录下载（更稳定）
用账号 xxx 登录下载 Instagram 用户 yyy 的图片

# 带延迟控制
下载Instagram用户 xxx 的图片，每10篇休息2分钟
```

### 命令参数
| 参数 | 说明 |
|:---|:---|
| `--no-videos` | 跳过视频，只下载图片 |
| `--no-captions` | 不下载文字说明 |
| `--no-metadata-json` | 不下载元数据 |
| `--fast-update` | 断点续传模式 |
| `--login` | 登录模式（更稳定） |
| `--count N` | 只下载最近N篇帖子 |

### 使用脚本
```bash
python scripts/download_instagram.py {username} [--delay] [--login myuser] [--max-posts 50]
```

---

## 📋 方案B：Playwright 浏览器下载（推荐）

**适用于**：instaloader遇到限流(401/403)时的备用方案。

### 步骤1：浏览器登录Instagram

```
使用Playwright skill的browser_navigate访问 https://www.instagram.com/accounts/login/
```

登录步骤：
1. `browser_snapshot` 获取页面元素
2. `browser_type` 填写用户名和密码
3. `browser_click` 点击登录按钮
4. 如需验证，手动完成邮箱/短信验证
5. `browser_wait_for` 等待 "Search" 或 "搜索" 出现确认登录成功

### 步骤2：获取用户帖子列表

```javascript
// 导航到用户主页
browser_navigate({ url: "https://www.instagram.com/{username}/" })

// 等待页面加载
browser_wait_for({ time: 3 })

// 执行JS提取帖子shortcode
browser_evaluate({
  function: `() => {
    const links = document.querySelectorAll('a[href*="/p/"]');
    const codes = [];
    const seen = new Set();
    links.forEach(a => {
      const match = a.href.match(/\\/p\\/([A-Za-z0-9_-]+)/);
      if (match && !seen.has(match[1])) {
        seen.add(match[1]);
        codes.push(match[1]);
      }
    });
    return codes.slice(0, 20);  // 获取最近20个帖子
  }`
})
```

**滚动加载更多**：如需更多帖子，执行滚动后重复提取
```javascript
browser_evaluate({ function: "() => window.scrollTo(0, document.body.scrollHeight)" })
browser_wait_for({ time: 2 })
```

### 步骤3：提取单个帖子图片URL

对每个shortcode执行：

```javascript
// 导航到帖子页面
browser_navigate({ url: "https://www.instagram.com/p/{shortcode}/" })
browser_wait_for({ time: 2 })

// 提取图片URL（排除头像和缩略图）
browser_evaluate({
  function: `() => {
    const imgs = document.querySelectorAll('article img, main img');
    const urls = [];
    const seen = new Set();
    imgs.forEach(img => {
      const src = img.src;
      if (src && src.includes('scontent') && !seen.has(src)) {
        const alt = img.alt || '';
        // 排除头像和缩略图
        if (!alt.includes('头像') && !alt.includes('avatar') && 
            !src.includes('s150x150') && !src.includes('_s.jpg')) {
          seen.add(src);
          urls.push(src);
        }
      }
    });
    return urls.slice(0, 10);  // 每帖最多10张图
  }`
})
```

### 步骤4：下载图片

使用Python requests下载提取到的URL：

```python
import requests
import os

def download_image(url, filepath):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.instagram.com/",
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"
    }
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(resp.content)
        return True
    return False

# 使用示例
download_image(url, f"{shortcode}_{i}.jpg")
```

### 辅助脚本

使用 `scripts/batch_download_ig.py`：
```bash
python batch_download_ig.py {shortcode} "{url1}" "{url2}"
```

---

## 📁 输出结构

```
{username}_downloads/
├── {shortcode}_1.jpg    # 帖子第1张图
├── {shortcode}_2.jpg    # 帖子第2张图（多图帖子）
└── ...
```

---

## ⚠️ 常见问题

### 限流问题 (401/403)
- **方案A限流**：切换到方案B（Playwright浏览器）
- **方案B限流**：等待30-60分钟后重试

### 视频帖子(Reels)
- 两种方案都只下载图片
- 视频帖子会自动跳过

### 多图帖子
- 方案A：自动下载所有图片
- 方案B：JS提取可获取前10张

### 登录验证
- Instagram可能要求邮箱/短信验证
- 方案B时可在浏览器中手动完成验证

---

## 🔒 合规提示

- 仅用于个人备份和学习用途
- 请遵守 Instagram 使用条款
- 尊重原作者版权
