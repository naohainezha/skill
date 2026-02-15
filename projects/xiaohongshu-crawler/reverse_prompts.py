"""
ComfyUI 图片反推提示词生成器
使用BLIP模型从图片中生成提示词描述
"""

import json
import urllib.request
import urllib.error
import base64
import os
import sys
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============ 配置 ============
COMFYUI_HOST = "127.0.0.1"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}"

# 输入图片目录
INPUT_DIR = r"D:\xiaohongshu-crawler\output\glasses_images"

# 输出文件
OUTPUT_FILE = r"D:\xiaohongshu-crawler\output\reverse_prompts_glasses.txt"


# 图片反推工作流（使用BLIP模型）
WORKFLOW = {
    "1": {
        "class_type": "LoadImage",
        "inputs": {
            "image": "example.png"
        }
    },
    "2": {
        "class_type": "BLIPModelLoader",
        "inputs": {
            "blip_model": "BLIP_base"
        }
    },
    "3": {
        "class_type": "ImageCaptioning",
        "inputs": {
            "blip_model": ["2", 0],
            "image": ["1", 0],
            "min_length": 10,
            "max_length": 100,
            "enable_beam_search": False
        }
    }
}


def encode_image_to_base64(image_path):
    """将图片编码为base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def generate_caption(image_path):
    """使用ComfyUI的BLIP模型生成图片描述"""
    try:
        # 读取图片并编码为base64
        image_b64 = encode_image_to_base64(image_path)

        # 设置工作流中的图片
        workflow = json.loads(json.dumps(WORKFLOW))  # 深拷贝
        workflow["1"]["inputs"]["image"] = image_b64

        # 发送到ComfyUI
        data = json.dumps({"prompt": workflow}).encode('utf-8')
        req = urllib.request.Request(
            f"{COMFYUI_URL}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())

        # 获取prompt ID
        prompt_id = result['prompt_id']

        # 轮询获取结果
        while True:
            try:
                with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
                    history = json.loads(response.read())

                if prompt_id in history:
                    output = history[prompt_id]['outputs']
                    if '3' in output:
                        # 获取生成的描述
                        caption = output['3'][0]['caption']
                        return caption

            except urllib.error.HTTPError as e:
                if e.code == 404:
                    pass  # 还没完成

            import time
            time.sleep(1)

    except Exception as e:
        print(f"  生成描述失败: {e}")
        return None


def batch_process_images():
    """批量处理图片目录中的所有图片"""
    # 获取所有图片文件
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        image_files.extend(Path(INPUT_DIR).rglob(ext))

    print(f"找到 {len(image_files)} 张图片")

    results = []

    for idx, img_path in enumerate(image_files[:10], 1):  # 先处理前10张
        print(f"\n处理 {idx}/{len(image_files)}: {img_path.name}")

        # 生成描述
        caption = generate_caption(str(img_path))

        if caption:
            print(f"  描述: {caption[:100]}...")
            results.append({
                'image': str(img_path),
                'caption': caption
            })
        else:
            print(f"  跳过")

        # 保存进度
        save_results(results)

    return results


def save_results(results):
    """保存结果到文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("图片反推提示词 - 眼镜穿搭专题\n")
        f.write("=" * 80 + "\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"【图片 {i}】\n")
            f.write(f"文件: {Path(result['image']).name}\n")
            f.write(f"提示词: {result['caption']}\n")
            f.write("-" * 80 + "\n\n")

        f.write("=" * 80 + "\n")
        f.write(f"共 {len(results)} 个提示词\n")
        f.write("=" * 80 + "\n")

    print(f"\n结果已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    # 检查ComfyUI是否运行
    try:
        urllib.request.urlopen(f"{COMFYUI_URL}/system_stats", timeout=5)
        print("ComfyUI 已运行")
    except:
        print("错误: ComfyUI 未运行，请先启动 ComfyUI")
        sys.exit(1)

    # 批量处理图片
    results = batch_process_images()

    print(f"\n完成！共处理 {len(results)} 张图片")
