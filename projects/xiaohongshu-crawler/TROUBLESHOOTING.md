# 问题解决方案

## 问题1: run_v3.bat 打不开

### 原因
批处理文件编码问题或路径问题

### 解决方案（按优先级）

#### 方案A：使用 go.bat（最简单）
双击运行：
```
go.bat
```

#### 方案B：使用 launcher.py（推荐）
```bash
cd xiaohongshu-crawler
python launcher.py
```

#### 方案C：直接运行
```bash
cd xiaohongshu-crawler
python crawler_v3.py
```

#### 方案D：使用 start.bat
双击运行：
```
start.bat
```

---

## 问题2: 爬虫采集不到数据

### 已修复的bug
crawler_v3.py 第485行缺少 await 关键字

**已自动修复！**

### 其他可能原因

1. **需要重新登录**
   - 删除 cookies.json
   - 重新运行扫码登录

2. **页面结构变化**
   - 小红书更新了页面结构
   - 需要等待V3.1更新

3. **cookies过期**
   - 删除 cookies.json
   - 重新登录

---

## 测试步骤

### 1. 验证环境
```bash
cd xiaohongshu-crawler
python test_env.py
```

应该看到：
```
✅ 环境测试完成！
```

### 2. 清理cookies
```bash
del cookies.json  (Windows)
rm cookies.json   (Linux/Mac)
```

### 3. 运行爬虫
```bash
# Windows
go.bat

# 或
python launcher.py

# 或
python crawler_v3.py
```

### 4. 扫码登录
- 等待浏览器打开
- 使用小红书APP扫码
- 登录成功后自动采集

---

## 文件说明

### 启动文件

| 文件 | 说明 | 推荐度 |
|------|------|--------|
| go.bat | 最简单，调用launcher.py | ⭐⭐⭐ |
| launcher.py | Python启动器，功能完整 | ⭐⭐⭐ |
| start.bat | 简化批处理 | ⭐⭐ |
| run_v3.bat | 原始文件（可能有编码问题） | ⭐ |
| run_v3_simple.bat | 简化版 | ⭐⭐ |

### 爬虫文件

| 文件 | 说明 | 推荐度 |
|------|------|--------|
| crawler_v3.py | V3深度人工模拟版 | ⭐⭐⭐ |
| crawler_v2.py | V2改进版 | ⭐⭐ |
| crawler.py | V1基础版 | ⭐ |

---

## 推荐使用流程

### 首次使用
```bash
1. cd xiaohongshu-crawler
2. python test_env.py
3. del cookies.json
4. python launcher.py
5. 扫码登录
6. 等待采集完成
```

### 日常使用
```bash
cd xiaohongshu-crawler
python launcher.py
```

或直接双击：
```
go.bat
```

---

## 如果还是不行

### 1. 检查Python
```bash
python --version
```
应该显示：Python 3.8+

### 2. 检查依赖
```bash
pip show playwright
pip show fake-useragent
```

### 3. 重新安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. 查看错误信息
运行时查看具体错误，然后提供错误信息以便进一步诊断

---

## 联系方式

如遇到问题，请提供：
1. 运行的命令
2. 错误信息截图或文本
3. Python版本
4. 操作系统版本

---

*最后更新：2026-01-05*
