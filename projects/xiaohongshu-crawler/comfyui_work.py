# -*- coding: utf-8 -*-
"""
ComfyUI自动处理 - 修复版本（跳过source_path）
"""

import json
import requests
import os
import sys
import time
from pathlib import Path

# 修复Windows控制台编码
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


def modify_workflow(workflow, image_dir_path, image_index):
    """修改工作流：设置Load Image Batch的路径和索引"""
    workflow_copy = json.loads(json.dumps(workflow))

    # 修改节点4（Load Image Batch）
    for node in workflow_copy['nodes']:
        if node['id'] == 4:
            # widgets_values: [mode, seed, index, label, path, pattern, allow_RGBA_output, filename_text_extension]
            node['widgets_values'][5] = str(image_dir_path)  # path
            node['widgets_values'][0] = "single_image"       # mode
            node['widgets_values'][2] = image_index             # index
            node['widgets_values'][1] = 77777                  # seed
            break

    return workflow_copy


def convert_to_api_prompt(workflow):
    """将workflow格式转换为API prompt格式"""
    prompt = {}

    # 构建link映射：link_id -> [from_node, from_slot]
    link_map = {}
    for link in workflow['links']:
        link_map[link[0]] = [link[1], link[2]]  # [from_node, from_slot]

    # 为每个节点构建API prompt entry
    for node in workflow['nodes']:
        node_id = str(node['id'])
        class_type = node.get('type', '')
        inputs = {}

        # 获取inputs和widgets
        node_inputs = node.get('inputs', [])
        widgets = node.get('widgets_values', [])

        # 为每个input赋值
        for i, input_def in enumerate(node_inputs):
            input_name = input_def['name']

            # 检查是否有link
            has_link = 'link' in input_def and input_def['link'] is not None

            if has_link:
                # 有link：从link_map获取
                link_id = input_def['link']
                if link_id in link_map:
                    inputs[input_name] = link_map[link_id]

            elif i < len(widgets):
                # 没有link：使用widgets值
                # 跳过Qwen3的source_path
                if not (class_type == 'Qwen3_VQA' and input_name == 'source_path'):
                    inputs[input_name] = widgets[i]

        prompt[node_id] = {
            'class_type': class_type,
            'inputs': inputs
        }

    return prompt


def submit_prompt(prompt):
    """提交prompt到ComfyUI"""
    try:
        data = {'prompt': prompt}
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


def wait_for_completion(prompt_id, timeout=180):
    """等待完成并返回Qwen3的输出"""
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            print(f"  超时")
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
                    status = result.get('status', {})

                    if status.get('completed', False):
                        # 提取节点2（Qwen3_VQA）的输出
                        outputs = result.get('outputs', {})
                        if '2' in outputs:
                            node_output = outputs['2']
                            if 'text' in node_output and len(node_output['text']) > 0:
                                return node_output['text'][0]

                    if status.get('status_str') == 'execution_error':
                        print(f"  执行错误")
                        return None

        except:
            pass

        time.sleep(3)


def batch_process():
    """批量处理所有图片"""
    workflow = load_workflow()

    note_dirs = sorted([d for d in Path(IMAGES_DIR).iterdir() if d.is_dir()])

    print(f"找到 {len(note_dirs)} 个笔记目录\n")

    results = []

    for idx, note_dir in enumerate(note_dirs, 1):
        print(f"处理第 {idx} 个笔记: {note_dir.name}")

        # 获取图片
        image_files = sorted([
            f for f in note_dir.iterdir()
            if f.suffix.lower() in ['.png', '.jpg', '.jpeg']
        ])

        if not image_files:
            print(f"  没有图片，跳过\n")
            continue

        # 选择前N张
        selected_images = image_files[:IMAGES_PER_NOTE]

        for img_idx, img_path in enumerate(selected_images):
            print(f"  处理: {img_path.name}")

            # 1. 修改workflow
            modified_workflow = modify_workflow(
                workflow,
                img_path.parent,
                img_idx
            )

            # 2. 转换为API prompt
            prompt = convert_to_api_prompt(modified_workflow)

            # 3. 提交
            prompt_id = submit_prompt(prompt)

            if not prompt_id:
                print(f"  失败\n")
                continue

            print(f"  等待... (ID: {prompt_id})")

            # 4. 等待结果
            caption = wait_for_completion(prompt_id)

            if caption:
                print(f"  ✓ {caption[:50]}...")
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
        f.write("眼镜穿搭图片反推提示词（ComfyUI Qwen3-VQA）\n")
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
        print(f"错误: 图片目录不存在")
        sys.exit(1)

    if not os.path.exists(WORKFLOW_FILE):
        print(f"错误: 工作流文件不存在")
        sys.exit(1)

    print(f"ComfyUI: {COMFYUI_URL}")
    print(f"图片目录: {IMAGES_DIR}")
    print(f"输出文件: {OUTPUT_FILE}")
    print("")

    # 开始处理
    results = batch_process()

    print("\n" + "=" * 80)
    print(f"完成！共处理 {len(results)} 张图片")
    print(f"结果已保存到: {OUTPUT_FILE}")
    print("=" * 80)
