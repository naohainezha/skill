# -*- coding: utf-8 -*-
"""
测试ComfyUI API连接
"""

import json
import urllib.request
import urllib.error

COMFYUI_URL = "http://192.168.11.158:8188"

# 加载工作流
with open(r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json", 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print(f"节点数: {len(workflow['nodes'])}")
print(f"链接数: {len(workflow['links'])}")

# 检查节点类型
print("\n节点列表:")
for node in workflow['nodes']:
    print(f"  ID: {node['id']}, Type: {node.get('type')}")

# 尝试提交一个简单的workflow
simple_prompt = {
    "prompt": {
        "3": {
            "inputs": {
                "images": [
                    2,
                    0
                ]
            },
            "class_type": "PreviewImage",
            "_meta": {
                "title": "Preview Image"
            }
        }
    }
}

print("\n尝试提交简单请求...")
try:
    data = json.dumps(simple_prompt).encode('utf-8')
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        print(f"成功! prompt_id: {result.get('prompt_id')}")
except Exception as e:
    print(f"失败: {e}")
