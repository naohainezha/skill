# 步骤1：检查ComfyUI状态

## 你的任务

确认ComfyUI已启动并正常运行。

## 检查方法

### 方法1：浏览器访问

打开浏览器访问：
```
http://192.168.11.158:8188
```

如果能看到ComfyUI界面，说明已运行。

### 方法2：命令行检测

```bash
python -c "import requests; r = requests.get('http://192.168.11.158:8188/system_stats', timeout=5); print('运行中' if r.status_code == 200 else '未运行')"
```

## 启动ComfyUI

如果未运行，执行：

```bash
# 方法1：使用启动器
cd "D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1"
start 绘世启动器.exe

# 然后在启动器中点击"启动"
```

或

```bash
# 方法2：直接启动
cd "D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI"
"..\python\python.exe" main.py --listen 192.168.11.158 --port 8188
```

## 完成标志

- [ ] ComfyUI界面可访问
- [ ] API接口响应正常

## 下一步

确认运行后，执行 [步骤2-执行洗图](step2-执行洗图.md)
