# 启动 ComfyUI 服务

**目的**: 确保 ComfyUI 服务正常运行，为洗图任务做准备。

---

## 📋 前置检查

### 1. 验证文件存在

```bash
# 检查 ComfyUI 目录
ls "D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI"

# 检查启动脚本
ls C:\Users\admin\projects\xhs-comfyui-wash\start_comfyui.py

# 检查 Python 解释器
ls "D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\python\python.exe"
```

### 2. 确认端口可用

```bash
# 检查 8188 端口是否被占用
netstat -an | findstr 8188

# 如果被占用，查找进程
tasklist | findstr python
```

---

## 🚀 启动步骤

### 方法1：使用自动启动脚本（✅ 推荐）

```bash
# 进入项目目录
cd C:\Users\admin\projects\xhs-comfyui-wash

# 运行启动脚本
python start_comfyui.py
```

**预期输出**：
```
============================================================
ComfyUI启动工具
============================================================

[信息] ComfyUI未运行，尝试启动...
[尝试] 直接启动ComfyUI...
[启动] PID: 26912
[等待] 等待ComfyUI启动 (超时: 120秒)...
  等待中... (10/120秒)
  等待中... (30/120秒)
  等待中... (50/120秒)
  等待中... (70/120秒)
  等待中... (90/120秒)
[成功] ComfyUI已启动!
```

**成功标志**：
- 看到 `[成功] ComfyUI已启动!`
- 进程 PID: 26912（示例）
- API 可访问

### 方法2：直接启动（备用）

```bash
# 进入 ComfyUI 目录
cd "D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI"

# 使用内置 Python 启动
..\python\python.exe main.py --listen 0.0.0.0 --port 8188
```

**注意**：
- 此方法会打开新控制台窗口
- 需要手动检查是否启动成功
- 建议在新窗口中运行，便于监控日志

### 方法3：使用秋叶启动器（GUI）

```bash
# 双击运行启动器
"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\绘世启动器.exe"

# 或使用命令行
cd "D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1"
start 绘世启动器.exe
```

**步骤**：
1. 等待启动器窗口打开
2. 点击"启动"按钮
3. 等待 ComfyUI 完全加载
4. 看到 "Starting server" 消息

---

## ✅ 验证启动成功

### 方法1：API 检查

```bash
# 使用 curl
curl http://192.168.11.158:8188/system_stats

# 使用 Python
python -c "import requests; r = requests.get('http://192.168.11.158:8188/system_stats', timeout=5); print('Running:', r.status_code == 200)"
```

**成功响应**：
```json
{
  "system_stats": {
    "queue_remaining": 0
  }
}
```

### 方法2：Web UI 检查

1. 打开浏览器
2. 访问: `http://192.168.11.158:8188`
3. 看到ComfyUI界面即成功

### 方法3：进程检查

```bash
# Windows
tasklist | findstr python

# 应该看到2个 python.exe 进程（ComfyUI主进程 + 工作进程）
```

---

## ⚠️ 故障排除

### 问题1：连接被拒绝

**错误**：
```
ConnectionRefusedError: [WinError 10061] 目标计算机积极拒绝连接
```

**原因**：ComfyUI 未启动或端口配置错误

**解决**：
1. 确认运行了 `start_comfyui.py`
2. 检查端口是否为 8188
3. 查看防火墙设置

### 问题2：启动超时

**错误**：
```
[超时] ComfyUI未启动
```

**原因**：启动时间超过120秒（正常情况）

**解决**：
1. 检查进程是否在运行：`tasklist | findstr python`
2. 检查 ComfyUI 控制台日志
3. 增加超时时间或手动验证

### 问题3：启动失败

**错误**：
```
[错误] 启动失败: ...
```

**可能原因**：
- Python 路径错误
- main.py 文件损坏
- 依赖库缺失

**解决**：
1. 验证文件完整性
2. 检查 Python 环境
3. 重新安装 ComfyUI

---

## 📊 实测数据（2026-01-30）

**启动时间**：
- 最快: 70秒
- 最慢: 90秒
- 平均: 80秒

**资源占用**：
- 内存: 50-60MB（2个进程）
- CPU: 启动时高，稳定后低
- GPU: 根据模型大小变化

**成功案例**：
```
PID: 26912
启动时间: 2026-01-30 17:43
验证: ✅ API 响应正常
首次洗图: 4张图片，全部成功
```

---

## 📝 后续步骤

启动成功后，继续下一步：

**→ [step2-执行洗图.md](step2-执行洗图.md)**

执行洗图任务：
```bash
python wash_lora.py "输入目录" "xiaolian_000001800.safetensors" 0.8
```

---

## 💡 提示

- ✅ **首次启动**: 使用 `start_comfyui.py` 最简单
- ✅ **日常使用**: 如果 ComfyUI 已运行，脚本会自动检测
- ✅ **后台运行**: ComfyUI 在独立控制台中运行，不影响其他操作
- ⚠️ **端口冲突**: 确保 8188 端口未被占用
- ⚠️ **防火墙**: 可能需要允许 Python 访问网络
