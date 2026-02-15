# 第二步：执行下载

## 你的任务

使用 XHS-Downloader API 下载小红书作品。

## ⚠️ 重要：先判断使用场景

### 场景A：单条作品链接 → 使用本工具
有具体的作品链接，如 `https://www.xiaohongshu.com/explore/xxx`

### 场景B：批量下载博主笔记 → 使用 xhs-batch-downloader
用户提供了博主ID，或要求下载"10篇笔记"、"批量下载"

**立即切换到 xhs-batch-downloader**：
```bash
cd C:\Users\admin\Projects\xhs-batch-downloader
python cli.py download <博主ID> --count 10
```

---

## 单条作品下载方式

### 方式一：Python 脚本（推荐）

使用提供的脚本模板：

```bash
cd C:\Users\admin
python [脚本路径] "小红书作品URL"
```

**脚本模板**：见 [scripts/download_template.py](../scripts/download_template.py)

### 方式二：直接调用 API

```bash
cd C:\Users\admin\Projects\XHS-Downloader
python -c "import asyncio; import sys; sys.path.insert(0, r'C:\\Users\\admin\\XHS-Downloader'); from source import XHS; asyncio.run(XHS().__aenter__())"
```

## 下载选项

### 仅获取作品信息（不下载文件）

```python
await xhs.extract(url, download=False)
```

### 指定下载部分图片（图文作品）

```python
await xhs.extract(url, download=True, index=[1, 3, 5])  # 下载第1、3、5张图
```

## 支持的链接格式

- `https://www.xiaohongshu.com/explore/作品ID?xsec_token=XXX`
- `https://www.xiaohongshu.com/discovery/item/作品ID?xsec_token=XXX`
- `https://www.xiaohongshu.com/user/profile/作者ID/作品ID?xsec_token=XXX`
- `https://xhslink.com/分享码`

## 完成标志

下载完成后，进入下一步查看结果。

## 参考资源

- API参考：[references/API参考.md](../references/API参考.md)
- 支持的链接：[references/支持的链接.md](../references/支持的链接.md)
