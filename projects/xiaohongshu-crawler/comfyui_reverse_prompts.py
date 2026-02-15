# -*- coding: utf-8 -*-
"""
使用ComfyUI的Qwen3_VQA工作流进行图片提示词反推
"""

import json
import urllib.request
import urllib.error
import os
import sys
import time
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============ 配置 ============
COMFYUI_HOST = "192.168.11.158"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}"

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
    """修改工作流的图片路径 - 使用单张图片模式"""
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

    return workflow_copy, str(image_path)


def submit_workflow(workflow, source_path):
    """提交工作流到ComfyUI"""
    try:
        # 简化：直接提交原始workflow，不带extra_data
        prompt_data = {
            "prompt": workflow
        }

        # 遍历nodes，为Qwen3_VQA的source_path添加值
        for node in prompt_data["prompt"]["nodes"]:
            if node["id"] == 2:
                # 在inputs中，如果有source_path没有link，直接设置值
                for i, inp in enumerate(node["inputs"]):
                    if inp["name"] == "source_path" and inp["link"] is None:
                        node["inputs"][i] = str(source_path)
                        break
                break

        # 保存请求数据到文件用于调试
        with open(r"D:\xiaohongshu-crawler\output\last_prompt.json", 'w', encoding='utf-8') as f:
            json.dump(prompt_data, f, indent=2, ensure_ascii=False)

        # 构建请求
        data = json.dumps(prompt_data).encode('utf-8')
        req = urllib.request.Request(
            f"{COMFYUI_URL}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            return result.get('prompt_id')

    except urllib.error.HTTPError as e:
        # 打印错误详情
        print(f"  HTTP错误 {e.code}: {e.reason}")
        try:
            error_content = e.read().decode('utf-8')
            print(f"  错误详情: {error_content[:500]}")
        except:
            pass
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
            with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as response:
                history = json.loads(response.read())

            if prompt_id in history:
                result = history[prompt_id]

                # 检查是否完成
                if 'status' in result:
                    status = result['status']
                    if status.get('completed', False):
                        # 获取Qwen3_VQA的输出（节点2）
                        if 'outputs' in result:
                            outputs = result['outputs']
                            if '2' in outputs:
                                # 获取文本输出
                                text_output = outputs['2']
                                if 'string' in text_output:
                                    return text_output['string'][0]

                # 如果失败
                if status.get('status_str') == 'execution_error':
                    print(f"  执行错误")
                    return None

        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass  # 还没完成，继续等待

        time.sleep(2)


def batch_process_images():
    """批量处理图片"""
    # 加载工作流
    workflow = load_workflow()

    # 打印workflow的基本信息
    print(f"工作流节点数: {len(workflow.get('nodes', []))}")
    print(f"工作流链接数: {len(workflow.get('links', []))}")

    # 检查第一个节点
    if workflow.get('nodes'):
        first_node = workflow['nodes'][0]
        print(f"第一个节点: ID={first_node.get('id')}, Type={first_node.get('type', 'N/A')}")

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

            # 检查workflow是否正确
            if not workflow or 'nodes' not in workflow:
                print(f"  Workflow加载错误")
                continue

            try:
                # 修改工作流的图片路径
                modified_workflow, source_path = modify_workflow(workflow, img_path)
            except Exception as e:
                print(f"  修改工作流出错: {e}")
                continue

            # 保存修改后的工作流到文件用于调试
            debug_file = f"D:\\xiaohongshu-crawler\\output\\debug_workflow_{idx}_{img_path.stem}.json"
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(modified_workflow, f, indent=2, ensure_ascii=False)

            # 提交工作流，传递source_path
            prompt_id = submit_workflow(modified_workflow, source_path)

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
        req = urllib.request.Request(f"{COMFYUI_URL}/history", headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=5)
        print("ComfyUI 已运行\n")
    except Exception as e:
        print(f"警告: 无法连接到ComfyUI ({e})")
        print("尝试继续运行...\n")

    # 检查图片目录
    if not os.path.exists(IMAGES_DIR):
        print(f"错误: 图片目录不存在: {IMAGES_DIR}")
        sys.exit(1)

    # 批量处理图片
    results = batch_process_images()

    print(f"\n完成！共处理 {len(results)} 张图片")
    print(f"结果已保存到: {OUTPUT_FILE}")
