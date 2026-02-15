# -*- coding: utf-8 -*-
"""
手动构造一个最简单的workflow
"""

import json
import urllib.request

COMFYUI_URL = "http://192.168.11.158:8188"

# 手动构造一个简单的prompt（只包含一个文本节点）
simple_prompt = {
    "1": {
        "inputs": {
            "text": "测试文本"
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
            "title": "CLIP Text Encode (Prompt)"
        }
    }
}

print("提交最简单的prompt...")
try:
    data = json.dumps({"prompt": simple_prompt}).encode('utf-8')
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
    import traceback
    traceback.print_exc()
