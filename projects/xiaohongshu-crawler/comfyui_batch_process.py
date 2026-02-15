# -*- coding: utf-8 -*-
"""
使用ComfyUI批量反推提示词
将图片文件夹地址填入Load Image Batch节点，为每张图片运行一次
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


def modify_workflow_for_directory(workflow, image_dir_path, image_index):
    """
    修改工作流：
    1. 设置Load Image Batch的path为图片目录
    2. 设置模式为single_image，并指定图片索引
    """
    workflow_copy = json.loads(json.dumps(workflow))  # 深拷贝

    # 修改节点4（Load Image Batch）
    for node in workflow_copy['nodes']:
        if node['id'] == 4:
            # 设置图片路径
            node['widgets_values'][5] = str(image_dir_path)
            # 设置模式为single_image
            node['widgets_values'][0] = "single_image"
            # 设置图片索引
            node['widgets_values'][2] = image_index
            # 设置seed为固定值（避免每次都变）
            node['widgets_values'][1] = 12345
            break

    return workflow_copy


def extract_text_from_node_2(workflow, history_result):
    """从历史结果中提取节点2（Qwen3_VQA）的文本输出"""
    try:
        if 'outputs' in history_result:
            outputs = history_result['outputs']
            if '2' in outputs:
                output = outputs['2']
                if 'text' in output and len(output['text']) > 0:
                    return output['text'][0]
        return None
    except:
        return None


def submit_workflow(workflow):
    """提交工作流到ComfyUI"""
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={'prompt': workflow},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('prompt_id')
        else:
            print(f"  HTTP错误 {response.status_code}")
            print(f"  错误详情: {response.text[:300]}")
            return None

    except Exception as e:
        print(f"  提交失败: {e}")
        return None


def wait_for_result(prompt_id, timeout=180):
    """等待工作流完成"""
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
                        # 提取节点2的文本输出
                        text = extract_text_from_node_2(None, result)
                        if text:
                            return text
                        else:
                            print(f"  找不到输出")
                            return None

                    # 如果失败
                    if result.get('status', {}).get('status_str') == 'execution_error':
                        print(f"  执行错误")
                        if 'node_errors' in result:
                            for node_id, errors in result['node_errors'].items():
                                print(f"    节点{node_id}: {errors}")
                        return None

        except Exception as e:
            pass

        time.sleep(2)


def batch_process_images():
    """批量处理图片"""
    # 加载工作流
    workflow = load_workflow()

    # 获取所有笔记目录
    note_dirs = sorted([d for d in Path(IMAGES_DIR).iterdir() if d.is_dir()])

    print(f"找到 {len(note_dirs)} 个笔记目录\n")

    results = []

    for idx, note_dir in enumerate(note_dirs, 1):
        print(f"处理第 {idx} 个笔记: {note_dir.name}")

        # 获取该笔记的图片
        image_files = sorted([f for f in note_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])

        if not image_files:
            print(f"  没有找到图片，跳过\n")
            continue

        # 选择前N张图片
        selected_images = image_files[:IMAGES_PER_NOTE]

        for img_idx, img_path in enumerate(selected_images):
            print(f"  处理图片: {img_path.name}")

            # 修改工作流：设置目录和图片索引
            modified_workflow = modify_workflow_for_directory(
                workflow,
                img_path.parent,  # 图片所在目录
                img_idx            # 图片索引
            )

            # 提交工作流
            prompt_id = submit_workflow(modified_workflow)

            if not prompt_id:
                print(f"  提交失败，跳过\n")
                continue

            print(f"  等待结果 (prompt_id: {prompt_id})...")

            # 等待结果
            caption = wait_for_result(prompt_id)

            if caption:
                print(f"  ✓ 生成完成: {caption[:80]}...")
                results.append({
                    'note': note_dir.name,
                    'image': img_path.name,
                    'caption': caption
                })
            else:
                print(f"  ✗ 生成失败")

            print("")

        # 每处理完一个笔记就保存进度
        save_results(results)

    return results


def save_results(results):
    """保存结果到文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("眼镜穿搭图片反推提示词（ComfyUI Qwen3）\n")
        f.write("=" * 80 + "\n\n")

        current_note = None

        for result in results:
            # 如果是新笔记，添加标题
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
    # 检查ComfyUI是否运行
    try:
        response = requests.get(f"{COMFYUI_URL}/", timeout=5)
        print("ComfyUI 已运行\n")
    except:
        print("错误: ComfyUI 未运行，请先启动 ComfyUI")
        print(f"预期地址: {COMFYUI_URL}")
        sys.exit(1)

    # 检查图片目录
    if not os.path.exists(IMAGES_DIR):
        print(f"错误: 图片目录不存在: {IMAGES_DIR}")
        sys.exit(1)

    # 检查工作流文件
    if not os.path.exists(WORKFLOW_FILE):
        print(f"错误: 工作流文件不存在: {WORKFLOW_FILE}")
        sys.exit(1)

    print("配置信息:")
    print(f"  ComfyUI地址: {COMFYUI_URL}")
    print(f"  工作流文件: {WORKFLOW_FILE}")
    print(f"  图片目录: {IMAGES_DIR}")
    print(f"  每篇笔记处理图片数: {IMAGES_PER_NOTE}")
    print(f"  输出文件: {OUTPUT_FILE}")
    print("")

    # 批量处理图片
    results = batch_process_images()

    print(f"\n{'='*80}")
    print(f"完成！共处理 {len(results)} 张图片")
    print(f"结果已保存到: {OUTPUT_FILE}")
    print(f"{'='*80}")
