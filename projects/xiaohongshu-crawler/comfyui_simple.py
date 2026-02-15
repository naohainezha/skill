# -*- coding: utf-8 -*-
"""
简化版：直接提交原始workflow JSON给ComfyUI
"""

import json
import requests
import os
import sys
import time
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============ 配置 ============
COMFYUI_URL = "http://192.168.11.158:8188"

# 工作流文件
WORKFLOW_FILE = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json"

# 图片目录
IMAGES_DIR = r"D:\xiaohongshu-crawler\output\glasses_images"

# 输出文件
OUTPUT_FILE = r"D:\xiaohongshu-crawler\output\reverse_prompts_comfyui.txt"

# 每篇笔记选择几张图片
IMAGES_PER_NOTE = 1


def load_workflow():
    """加载工作流"""
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def modify_workflow_simple(workflow, image_dir_path, image_index):
    """
    修改工作流：
    只修改Load Image Batch节点的路径、模式和索引
    """
    workflow_copy = json.loads(json.dumps(workflow))  # 深拷贝

    # 修改节点4（Load Image Batch）
    for node in workflow_copy['nodes']:
        if node['id'] == 4:
            # widgets_values: [mode, seed, index, label, path, pattern, allow_RGBA_output, filename_text_extension]
            # 修改path（索引5）
            node['widgets_values'][5] = str(image_dir_path)
            # 修改mode为single_image（索引0）
            node['widgets_values'][0] = "single_image"
            # 修改index（索引2）
            node['widgets_values'][2] = image_index
            # 固定seed（索引1）
            node['widgets_values'][1] = 99999
            break

    return workflow_copy


def submit_workflow_raw(workflow):
    """直接提交原始workflow JSON"""
    try:
        # 直接提交，不转换为API prompt格式
        data = {
            'prompt': workflow
        }

        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('prompt_id')
        else:
            print(f"  HTTP错误 {response.status_code}")
            print(f"  响应: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"  提交失败: {e}")
        return None


def get_result(prompt_id, timeout=180):
    """获取执行结果"""
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            print(f"  等待超时")
            return None

        try:
            response = requests.get(
                f"{COMFYUI_URL}/history/{prompt_id}",
                timeout=5
            )

            if response.status_code == 200:
                history = response.json()

                if prompt_id in history:
                    result = history[prompt_id]

                    # 检查是否完成
                    if result.get('status', {}).get('completed', False):
                        # 查找Qwen3_VQA节点的输出
                        if 'outputs' in result:
                            outputs = result['outputs']
                            # Qwen3_VQA是节点2
                            if '2' in outputs:
                                output = outputs['2']
                                if 'text' in output and len(output['text']) > 0:
                                    return output['text'][0]

                    # 检查错误
                    if result.get('status', {}).get('status_str') == 'execution_error':
                        print(f"  执行错误")
                        return None

        except:
            pass

        time.sleep(3)


def batch_process():
    """批量处理图片"""
    workflow = load_workflow()

    note_dirs = sorted([d for d in Path(IMAGES_DIR).iterdir() if d.is_dir()])

    print(f"找到 {len(note_dirs)} 个笔记目录\n")

    results = []

    for idx, note_dir in enumerate(note_dirs, 1):
        print(f"处理第 {idx} 个笔记: {note_dir.name}")

        image_files = sorted([f for f in note_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])

        if not image_files:
            print(f"  没有图片，跳过\n")
            continue

        selected_images = image_files[:IMAGES_PER_NOTE]

        for img_idx, img_path in enumerate(selected_images):
            print(f"  处理图片: {img_path.name}")

            # 修改工作流
            modified_workflow = modify_workflow_simple(
                workflow,
                img_path.parent,
                img_idx
            )

            # 提交
            prompt_id = submit_workflow_raw(modified_workflow)

            if not prompt_id:
                print(f"  提交失败\n")
                continue

            print(f"  等待结果...")

            # 等待结果
            caption = get_result(prompt_id)

            if caption:
                print(f"  ✓ 完成: {caption[:80]}...")
                results.append({
                    'note': note_dir.name,
                    'image': img_path.name,
                    'caption': caption
                })
            else:
                print(f"  ✗ 失败")

            print("")

        # 保存进度
        save_results(results)

    return results


def save_results(results):
    """保存结果"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("眼镜穿搭图片反推提示词（ComfyUI Qwen3）\n")
        f.write("=" * 80 + "\n\n")

        current_note = None

        for result in results:
            if result['note'] != current_note:
                current_note = result['note']
                f.write(f"【笔记】{current_note}\n")
                f.write("-" * 80 + "\n")

            f.write(f"图片: {result['image']}\n")
            f.write(f"提示词: {result['caption']}\n")
            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write(f"共 {len(results)} 个提示词\n")
        f.write("=" * 80 + "\n")


if __name__ == "__main__":
    # 检查ComfyUI
    try:
        requests.get(f"{COMFYUI_URL}/", timeout=5)
        print("ComfyUI 已运行\n")
    except:
        print("错误: ComfyUI 未运行")
        sys.exit(1)

    # 检查路径
    if not os.path.exists(IMAGES_DIR):
        print(f"错误: 图片目录不存在: {IMAGES_DIR}")
        sys.exit(1)

    if not os.path.exists(WORKFLOW_FILE):
        print(f"错误: 工作流文件不存在: {WORKFLOW_FILE}")
        sys.exit(1)

    print(f"ComfyUI地址: {COMFYUI_URL}")
    print(f"工作流文件: {WORKFLOW_FILE}")
    print(f"图片目录: {IMAGES_DIR}")
    print("")

    # 批量处理
    results = batch_process()

    print(f"\n完成！共处理 {len(results)} 张图片")
    print(f"结果已保存到: {OUTPUT_FILE}")
