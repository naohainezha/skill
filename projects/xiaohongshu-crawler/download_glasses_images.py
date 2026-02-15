import os
import json
import requests
from urllib.parse import urlparse
from pathlib import Path

# 读取JSON文件
json_file = r"D:\xiaohongshu-crawler\output\notes_20260108_085720.json"
output_dir = r"D:\xiaohongshu-crawler\output\glasses_images"

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 读取数据
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"共找到 {len(data)} 篇笔记")

# 下载图片
downloaded_count = 0
for idx, note in enumerate(data, 1):
    # 移除标题中的emoji
    title_clean = ''.join(c for c in note['title'] if ord(c) < 128)
    print(f"\n处理第 {idx} 篇笔记: {title_clean}")
    
    # 为每篇笔记创建子目录
    note_dir = os.path.join(output_dir, f"{idx:02d}_{title_clean[:10]}")
    os.makedirs(note_dir, exist_ok=True)
    
    images = note.get('images_list', [])
    print(f"  找到 {len(images)} 张图片")
    
    for img_idx, img_url in enumerate(images, 1):
        try:
            # 修复http协议问题
            if img_url.startswith('http://'):
                img_url = img_url.replace('http://', 'https://', 1)
            
            # 获取文件扩展名
            parsed = urlparse(img_url)
            ext = '.jpg' if '.jpg' in parsed.path or '.jpeg' in parsed.path else '.png'
            
            # 生成文件名
            filename = f"{img_idx:02d}{ext}"
            filepath = os.path.join(note_dir, filename)
            
            # 下载图片
            response = requests.get(img_url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"    [OK] 下载完成: {filename}")
            downloaded_count += 1
            
        except Exception as e:
            print(f"    [FAIL] 下载失败: {e}")

print(f"\n总共下载 {downloaded_count} 张图片")
print(f"图片保存在: {output_dir}")
