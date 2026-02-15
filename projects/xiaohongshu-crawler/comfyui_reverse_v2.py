# -*- coding: utf-8 -*-
"""
使用requests库的ComfyUI提示词反推
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


def modify_workflow(workflow, image_path):
    """修改工作流的图片路径"""
    workflow_copy = json.loads(json.dumps(workflow))  # 深拷贝

    # 修改节点4（Load Image Batch）的路径
    for node in workflow_copy['nodes']:
        if node['id'] == 4:
            # 设置为图片所在目录
            node['widgets_values'][5] = str(image_path.parent)
            # 模式改为single image
            node['widgets_values'][0] = "single_image"
            # 找到该目录下的图片索引
            images_in_dir = sorted([f for f in image_path.parent.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])
            try:
                img_index = images_in_dir.index(image_path)
            except:
                img_index = 0
            node['widgets_values'][2] = img_index
            break

    # 为Qwen3_VQA节点设置source_path
    for node in workflow_copy['nodes']:
        if node['id'] == 2:
            # 在inputs中找到source_path并设置值
            for i, inp in enumerate(node['inputs']):
                if inp['name'] == 'source_path':
                    node['inputs'][i] = str(image_path)
                    break
            break

    return workflow_copy


def convert_workflow_to_prompt(workflow):
    """将工作流格式转换为ComfyUI API prompt格式"""
    prompt = {}

    # 转换每个节点
    for node in workflow['nodes']:
        node_id = str(node['id'])
        prompt[node_id] = {
            'class_type': node['type'],
            'inputs': {}
        }

        # 添加inputs - 同时遍历inputs和widgets_values
        widgets = node.get('widgets_values', [])
        for i, inp in enumerate(node.get('inputs', [])):
            # 调试：跳过有问题的节点
            if node['id'] == 2 and i == 0:  # Qwen3_VQA的source_path输入
                # source_path需要特殊处理，直接设置为值（在modify_workflow中已设置）
                if isinstance(inp, str):
                    prompt[node_id]['inputs']['source_path'] = inp
                else:
                    pass
                continue

            # 如果有link，使用引用
            if 'link' in inp and inp['link'] is not None:
                # link是数字，需要查找对应的节点和输出索引
                # 在links数组中找到这个link
                for link in workflow['links']:
                    if link[0] == inp['link']:  # link ID
                        # link格式: [link_id, from_node, from_slot, to_node, to_slot, type]
                        prompt[node_id]['inputs'][inp['name']] = [
                            int(link[1]),  # from_node
                            int(link[2])   # from_slot
                        ]
                        break
            else:
                # 否则使用widgets_values中对应位置的值
                if i < len(widgets):
                    prompt[node_id]['inputs'][inp['name']] = widgets[i]

        # 添加_meta
        prompt[node_id]['_meta'] = {
            'title': node.get('type', '')
        }

    return prompt


def submit_workflow(prompt):
    """提交工作流到ComfyUI"""
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json={'prompt': prompt},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('prompt_id')
        else:
            print(f"  HTTP错误 {response.status_code}")
            print(f"  错误详情: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"  提交工作流失败: {e}")
        return None


def wait_for_result(prompt_id, timeout=300):
    """等待工作流完成"""
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            print(f"  等待超时")
            return None

        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()

                if prompt_id in history:
                    result = history[prompt_id]

                    # 检查是否完成
                    if result.get('status', {}).get('completed', False):
                        # 获取节点2（Qwen3_VQA）的输出
                        if 'outputs' in result:
                            outputs = result['outputs']
                            if '2' in outputs:
                                text_output = outputs['2']
                                if 'text' in text_output and len(text_output['text']) > 0:
                                    return text_output['text'][0]

                    # 如果失败
                    if result.get('status', {}).get('status_str') == 'execution_error':
                        print(f"  执行错误")
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

        for img_path in selected_images:
            print(f"  处理图片: {img_path.name}")

            # 修改工作流的图片路径
            modified_workflow = modify_workflow(workflow, img_path)

            # 转换为prompt格式
            prompt = convert_workflow_to_prompt(modified_workflow)

            # 保存prompt用于调试
            debug_file = f"D:\\xiaohongshu-crawler\\output\\debug_prompt_{idx}_{img_path.stem}.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(prompt, f, indent=2, ensure_ascii=False)

            # 提交工作流
            prompt_id = submit_workflow(prompt)

            if not prompt_id:
                print(f"  提交失败，跳过\n")
                continue

            print(f"  等待结果 (prompt_id: {prompt_id})...")

            # 等待结果
            caption = wait_for_result(prompt_id)

            if caption:
                print(f"  生成完成: {caption[:80]}...")
                results.append({
                    'note': note_dir.name,
                    'image': img_path.name,
                    'caption': caption
                })
            else:
                print(f"  生成失败")

            print("")

        # 保存进度
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
        sys.exit(1)

    # 检查图片目录
    if not os.path.exists(IMAGES_DIR):
        print(f"错误: 图片目录不存在: {IMAGES_DIR}")
        sys.exit(1)

    # 批量处理图片
    results = batch_process_images()

    print(f"\n完成！共处理 {len(results)} 张图片")
    print(f"结果已保存到: {OUTPUT_FILE}")
