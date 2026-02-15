# API 参考

## XHS.extract() 方法

```python
async def extract(
    self,
    url: str,                    # 小红书作品链接
    download: bool = False,       # 是否下载文件
    index: list[int] = None,     # 指定下载的图片序号（图文作品）
) -> list[dict]:
    """
    提取作品信息并可选地下载文件

    参数：
        url: 小红书作品链接
        download: 是否下载文件（默认 False）
        index: 指定下载的图片序号列表（图文作品）

    返回：
        作品信息列表
    """
```

## 返回数据结构

```python
[
  {
    "收藏数量": "1543",
    "评论数量": "1239",
    "点赞数量": "1901",
    "分享数量": "1.3万",
    "作品标签": "#旅行 #美食 #生活",
    "作品ID": "6954ec6700000000220329a6",
    "作品链接": "https://www.xiaohongshu.com/explore/xxx",
    "作品标题": "我的年度18张图",
    "作品描述": "#旅行[地点]# #美食[时间]#",
    "作品类型": "图文",
    "发布时间": "2025-12-31_17:29:01",
    "作者昵称": "Ruuu",
    "作者ID": "5c6fb3fb00000000110126a2",
    "作者链接": "https://www.xiaohongshu.com/user/profile/xxx",
    "下载地址": [
      "https://ci.xiaohongshu.com/notes_pre_post/xxx.png",
      ...
    ]
  }
]
```

## 使用示例

### 示例1：下载单个作品
```python
from source import XHS

async with XHS() as xhs:
    result = await xhs.extract(
        url="https://www.xiaohongshu.com/discovery/item/xxx",
        download=True
    )
    print(result)
```

### 示例2：仅获取作品信息
```python
from source import XHS

async with XHS() as xhs:
    result = await xhs.extract(
        url="https://www.xiaohongshu.com/explore/xxx",
        download=False  # 不下载文件
    )
    print(result)
```

### 示例3：指定下载部分图片
```python
from source import XHS

async with XHS() as xhs:
    result = await xhs.extract(
        url="https://www.xiaohongshu.com/explore/xxx",
        download=True,
        index=[1, 3, 5]  # 只下载第1、3、5张图
    )
    print(result)
```

## 注意事项

1. **异步调用**：必须使用 `async with` 或 `await`
2. **下载记录**：默认启用，已下载的作品ID会被跳过
3. **文件编码**：确保系统支持 UTF-8 编码
