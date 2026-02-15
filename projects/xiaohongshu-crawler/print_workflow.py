import json

path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json"

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(json.dumps(data, indent=2))
