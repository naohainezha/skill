# -*- coding: utf-8 -*-
"""
使用ComfyUI的原始格式提交
"""

import json
import urllib.request
import urllib.error
import os

COMFYUI_URL = "http://192.168.11.158:8188"

# 使用原始工作流格式
workflow_file = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json"

with open(workflow_file, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 直接提交原始workflow（不做任何修改）
prompt_data = {
    "prompt": workflow
}

print("提交原始workflow...")
try:
    data = json.dumps(prompt_data, ensure_ascii=False).encode('utf-8')
    print(f"数据大小: {len(data)} bytes")

    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={'Content-Type': 'application/json; charset=utf-8'}
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        print(f"成功! prompt_id: {result.get('prompt_id')}")
except urllib.error.HTTPError as e:
    print(f"HTTP错误 {e.code}")
    try:
        error_content = e.read().decode('utf-8')
        print(f"错误详情: {error_content}")
    except:
        pass
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
