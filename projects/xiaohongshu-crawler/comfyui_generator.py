"""
ComfyUI 自动图片生成器 V2
使用 zimage文生图0106 工作流，只修改 CLIPTextEncode 节点的提示词

使用方法：
    python comfyui_generator.py                          # 使用最新的提示词文件
    python comfyui_generator.py image_prompts_xxx.txt    # 指定提示词文件
"""

import json
import urllib.request
import urllib.error
import time
import uuid
import os
import sys
import glob
import re
import subprocess
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============ 配置 ============
COMFYUI_HOST = "127.0.0.1"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}"

# ComfyUI安装路径（秋叶启动器版本）
COMFYUI_ROOT = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1"
COMFYUI_LAUNCHER = os.path.join(COMFYUI_ROOT, "绘世启动器.exe")

# 工作流路径 - 固定使用 zimage文生图0106
WORKFLOW_FILE = os.path.join(COMFYUI_ROOT, r"ComfyUI\user\default\workflows\zimage文生图0106.json")

# CLIPTextEncode 节点ID（在zimage文生图0106工作流中）
CLIP_TEXT_ENCODE_NODE_ID = "33"

# 输出目录
PROMPTS_DIR = r"D:\xiaohongshu-crawler\output"


def parse_prompts_from_txt(txt_file):
    """从TXT文件解析提示词"""
    prompts = []
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配提示词块：找到"提示词N - 描述"后面的段落
    pattern = r'提示词\d+\s*[-—]\s*[^\n]+\n([^\n【提示词]+)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        prompt = match.strip()
        prompt = re.sub(r'-{10,}', '', prompt)
        prompt = re.sub(r'={10,}', '', prompt)
        prompt = prompt.strip()
        
        if prompt and len(prompt) > 20:
            prompts.append(prompt)
    
    return prompts


def check_comfyui_running():
    """检查ComfyUI是否在运行"""
    try:
        response = urllib.request.urlopen(f"{COMFYUI_URL}/prompt", timeout=5)
        return True
    except:
        return False


def start_comfyui():
    """启动ComfyUI (直接运行 main.py)"""
    python_exe = os.path.join(COMFYUI_ROOT, "python", "python.exe")
    main_py = os.path.join(COMFYUI_ROOT, "ComfyUI", "main.py")
    
    if not os.path.exists(python_exe) or not os.path.exists(main_py):
        print(f"错误: 找不到Python或main.py")
        return False
        
    print(f"正在启动ComfyUI (main.py)...")
    
    # 构造命令
    cmd = [python_exe, main_py, "--listen", "127.0.0.1", "--port", str(COMFYUI_PORT)]
    
    # 使用subprocess启动，创建新窗口
    try:
        subprocess.Popen(
            cmd,
            cwd=os.path.join(COMFYUI_ROOT, "ComfyUI"),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"启动失败: {e}")
        return False
    
    # 等待ComfyUI启动
    print("等待ComfyUI启动...", end="", flush=True)
    for i in range(60):  # 最多等待60秒
        time.sleep(2)
        print(".", end="", flush=True)
        if check_comfyui_running():
            print(" 启动成功!")
            return True
    
    print(" 启动超时!")
    return False


def load_workflow_api_format():
    """
    加载工作流并转换为API格式
    关键：只修改CLIPTextEncode节点的text，其他保持不变
    """
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    nodes = workflow.get('nodes', [])
    links = workflow.get('links', [])
    
    # 创建link映射: link_id -> (source_node_id, source_slot)
    link_map = {}
    for link in links:
        link_id = link[0]
        source_node = str(link[1])
        source_slot = link[2]
        link_map[link_id] = (source_node, source_slot)
    
    # 找出所有被使用的节点（有输入或输出连接的）
    used_nodes = set()
    for link in links:
        used_nodes.add(str(link[1]))  # source node
        used_nodes.add(str(link[3]))  # target node
    
    api_prompt = {}
    
    for node in nodes:
        node_id = str(node['id'])
        node_type = node['type']
        
        # 跳过禁用的节点
        if node.get('mode', 0) == 4:
            continue
        
        # 跳过未使用的Reroute节点
        if node_type == "Reroute" and node_id not in used_nodes:
            continue
        
        # 跳过某些辅助节点
        skip_types = ["Fast Groups Bypasser (rgthree)", "Image Comparer (rgthree)", "VRAMCleanup"]
        if node_type in skip_types:
            continue
        
        # 检查KSampler节点是否有完整的连接（如果没有model连接，说明是未使用的节点）
        if node_type in ["KSampler", "KSamplerAdvanced"]:
            inputs_def = node.get('inputs', [])
            has_model_link = False
            for inp in inputs_def:
                if inp['name'] == 'model' and inp.get('link') is not None:
                    has_model_link = True
                    break
            if not has_model_link:
                continue  # 跳过没有model连接的KSampler
        
        api_node = {
            "class_type": node_type,
            "inputs": {}
        }
        
        widgets_values = node.get('widgets_values', [])
        inputs_def = node.get('inputs', [])
        
        # 处理连接输入
        for inp in inputs_def:
            inp_name = inp['name']
            if 'link' in inp and inp['link'] is not None:
                link_id = inp['link']
                if link_id in link_map:
                    source_node, source_slot = link_map[link_id]
                    api_node["inputs"][inp_name] = [source_node, source_slot]
        
        # 根据节点类型处理widgets_values
        if node_type == "CLIPTextEncode":
            # CLIPTextEncode: widgets_values[0] 是提示词文本
            if widgets_values:
                api_node["inputs"]["text"] = widgets_values[0]
            # clip输入保持连接
        
        elif node_type == "KSampler":
            if len(widgets_values) >= 7:
                api_node["inputs"]["seed"] = widgets_values[0]
                api_node["inputs"]["steps"] = widgets_values[2]
                api_node["inputs"]["cfg"] = widgets_values[3]
                api_node["inputs"]["sampler_name"] = widgets_values[4]
                api_node["inputs"]["scheduler"] = widgets_values[5]
                api_node["inputs"]["denoise"] = widgets_values[6]
        
        elif node_type == "KSamplerAdvanced":
            # widgets_values: [add_noise, seed, control_after_generate, steps, cfg, sampler_name, scheduler, start_at_step, end_at_step, return_with_leftover_noise]
            if len(widgets_values) >= 10:
                api_node["inputs"]["add_noise"] = widgets_values[0]
                api_node["inputs"]["noise_seed"] = widgets_values[1]
                api_node["inputs"]["steps"] = widgets_values[3]
                api_node["inputs"]["cfg"] = widgets_values[4]
                api_node["inputs"]["sampler_name"] = widgets_values[5]
                api_node["inputs"]["scheduler"] = widgets_values[6]
                api_node["inputs"]["start_at_step"] = widgets_values[7]
                api_node["inputs"]["end_at_step"] = widgets_values[8]
                api_node["inputs"]["return_with_leftover_noise"] = widgets_values[9]
        
        elif node_type == "EmptyLatentImage":
            if len(widgets_values) >= 3:
                api_node["inputs"]["width"] = widgets_values[0]
                api_node["inputs"]["height"] = widgets_values[1]
                api_node["inputs"]["batch_size"] = widgets_values[2]
        
        elif node_type == "UNETLoader":
            if widgets_values:
                api_node["inputs"]["unet_name"] = widgets_values[0]
                if len(widgets_values) > 1:
                    api_node["inputs"]["weight_dtype"] = widgets_values[1]
        
        elif node_type == "CLIPLoader":
            if widgets_values:
                api_node["inputs"]["clip_name"] = widgets_values[0]
                if len(widgets_values) > 1:
                    api_node["inputs"]["type"] = widgets_values[1]
                if len(widgets_values) > 2:
                    api_node["inputs"]["device"] = widgets_values[2]
        
        elif node_type == "VAELoader":
            if widgets_values:
                api_node["inputs"]["vae_name"] = widgets_values[0]
        
        elif node_type == "LoraLoaderModelOnly":
            if widgets_values:
                api_node["inputs"]["lora_name"] = widgets_values[0]
                if len(widgets_values) > 1:
                    api_node["inputs"]["strength_model"] = widgets_values[1]
        
        elif node_type == "Image Save":
            if len(widgets_values) >= 15:
                api_node["inputs"]["output_path"] = widgets_values[0]
                api_node["inputs"]["filename_prefix"] = widgets_values[1]
                api_node["inputs"]["filename_delimiter"] = widgets_values[2]
                api_node["inputs"]["filename_number_padding"] = widgets_values[3]
                api_node["inputs"]["filename_number_start"] = widgets_values[4]
                api_node["inputs"]["extension"] = widgets_values[5]
                api_node["inputs"]["dpi"] = widgets_values[6]
                api_node["inputs"]["quality"] = widgets_values[7]
                api_node["inputs"]["optimize_image"] = widgets_values[8]
                api_node["inputs"]["lossless_webp"] = widgets_values[9]
                api_node["inputs"]["overwrite_mode"] = widgets_values[10]
                api_node["inputs"]["show_history"] = widgets_values[11]
                api_node["inputs"]["show_history_by_prefix"] = widgets_values[12]
                api_node["inputs"]["embed_workflow"] = widgets_values[13]
                api_node["inputs"]["show_previews"] = widgets_values[14]
        
        elif node_type == "VAEDecode":
            # VAEDecode只需要连接输入，已在上面处理
            pass
        
        elif node_type == "VAEEncode":
            # VAEEncode只需要连接输入
            pass
        
        elif node_type == "ConditioningZeroOut":
            # 只需要连接输入
            pass
        
        elif node_type == "PreviewImage":
            # 预览节点，只需要连接输入
            pass
        
        elif node_type == "LoadImage":
            if widgets_values:
                api_node["inputs"]["image"] = widgets_values[0]
                if len(widgets_values) > 1:
                    api_node["inputs"]["upload"] = widgets_values[1]
        
        elif node_type == "ImageScaleToMaxDimension":
            # widgets_values: ['lanczos', 1920] - [upscale_method, largest_size]
            if widgets_values:
                if len(widgets_values) >= 2:
                    api_node["inputs"]["upscale_method"] = widgets_values[0]
                    api_node["inputs"]["largest_size"] = widgets_values[1]
                elif len(widgets_values) == 1:
                    api_node["inputs"]["largest_size"] = widgets_values[0]
                    api_node["inputs"]["upscale_method"] = "lanczos"
        
        elif node_type == "Reroute":
            # Reroute节点只做数据传递，连接输入已处理
            pass
        
        # 其他未知类型的节点，只保留连接输入
        
        api_prompt[node_id] = api_node
    
    return api_prompt


def set_prompt_text(api_prompt, prompt_text, batch_index=0):
    """设置CLIPTextEncode节点的提示词，并更新seed"""
    # 修改CLIPTextEncode节点的text
    if CLIP_TEXT_ENCODE_NODE_ID in api_prompt:
        api_prompt[CLIP_TEXT_ENCODE_NODE_ID]["inputs"]["text"] = prompt_text
    
    # 更新所有KSampler的seed（确保每张图不同）
    new_seed = int(time.time() * 1000 + batch_index) % (2**32)
    for node_id, node in api_prompt.items():
        if node["class_type"] == "KSampler":
            node["inputs"]["seed"] = new_seed
        elif node["class_type"] == "KSamplerAdvanced":
            node["inputs"]["noise_seed"] = new_seed
    
    return api_prompt


def queue_prompt(prompt):
    """发送prompt到ComfyUI队列"""
    p = {"prompt": prompt, "client_id": str(uuid.uuid4())}
    data = json.dumps(p).encode('utf-8')
    
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"错误: {error_body[:300]}")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None


def wait_for_completion(prompt_id, timeout=300):
    """等待生成完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
            history = json.loads(response.read())
            
            if prompt_id in history:
                return history[prompt_id]
        except:
            pass
        
        time.sleep(1)
    
    return None


def find_latest_prompts_file():
    """查找最新的提示词文件"""
    txt_files = glob.glob(os.path.join(PROMPTS_DIR, "image_prompts_*.txt"))
    
    if not txt_files:
        return None
    
    return max(txt_files, key=os.path.getmtime)


def main():
    print("=" * 60)
    print("    ComfyUI 小红书配图生成器 V2")
    print("    工作流: zimage文生图0106")
    print("=" * 60)
    
    # 解析参数
    prompts_file = None
    args = sys.argv[1:]
    
    for arg in args:
        if not arg.startswith("--"):
            prompts_file = arg
    
    # 查找提示词文件
    if not prompts_file:
        prompts_file = find_latest_prompts_file()
        if not prompts_file:
            print("错误: 未找到提示词文件！")
            return
    
    if not os.path.exists(prompts_file):
        prompts_file = os.path.join(PROMPTS_DIR, prompts_file)
    
    if not os.path.exists(prompts_file):
        print(f"错误: 提示词文件不存在: {prompts_file}")
        return
    
    print(f"提示词文件: {prompts_file}")
    print(f"工作流: {WORKFLOW_FILE}")
    
    # 解析提示词
    prompts = parse_prompts_from_txt(prompts_file)
    if not prompts:
        print("错误: 未解析到有效提示词！")
        return
    
    print(f"解析到 {len(prompts)} 个提示词")
    print()
    
    # 检查ComfyUI是否运行
    if not check_comfyui_running():
        print("ComfyUI未运行，正在启动...")
        if not start_comfyui():
            print("错误: 无法启动ComfyUI！")
            return
    else:
        print("ComfyUI已运行")
    
        # 加载工作流API格式
    try:
        base_api_prompt = load_workflow_api_format()
        print("工作流加载成功")
        
        # =================================================================
        # 优化配置 (基于用户偏好 - 方案3)
        # 1. 保持原分辨率 (1440x1920)
        # 2. 仅使用前两次采样 (保留LoRA效果)，跳过第三次采样和放大流程
        # =================================================================
        
        print("应用配置: 原分辨率(1440x1920) + 仅前两次采样 (保留LoRA特征)")

        # 1. 确保初始分辨率为 1440x1920
        if "31" in base_api_prompt and base_api_prompt["31"]["class_type"] == "EmptyLatentImage":
            base_api_prompt["31"]["inputs"]["width"] = 1440
            base_api_prompt["31"]["inputs"]["height"] = 1920

        # 2. 绕过第三次采样
        # Node 3 (Save) 原本连接 Node 11 (3rd Pass Decode)，改为连接 Node 12 (2nd Pass Decode)
        if "3" in base_api_prompt:
            base_api_prompt["3"]["inputs"]["images"] = ["12", 0]
            
        # 3. 移除多余节点 (清理显存占用)
        # 36=KSampler3, 11=VAEDecode2, 10=Upscale, 7=VAEEncode, 8=Preview, 24=Preview
        nodes_to_remove = ["36", "11", "10", "7", "8", "24"]
        for node_id in nodes_to_remove:
            if node_id in base_api_prompt:
                del base_api_prompt[node_id]

        print(f"节点数量: {len(base_api_prompt)}")
        
        # 保存debug文件
        debug_file = os.path.join(PROMPTS_DIR, "debug_api_prompt.json")
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(base_api_prompt, f, indent=2, ensure_ascii=False)
        print(f"已保存调试文件: {debug_file}")
        
        # 检查关键节点是否存在
        required_nodes = ['3', '5', '11', '33', '36']
        missing = [n for n in required_nodes if n not in base_api_prompt]
        if missing:
            print(f"警告: 缺少关键节点: {missing}")
        else:
            print("关键节点检查通过: Image Save(3), VAELoader(5), VAEDecode(11), CLIPTextEncode(33), KSampler(36)")
    except Exception as e:
        print(f"错误: 加载工作流失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("开始生成图片...")
    print("-" * 60)
    
    success_count = 0
    for i, prompt_text in enumerate(prompts):
        print(f"\n[{i+1}/{len(prompts)}] 生成中...")
        print(f"   提示词: {prompt_text[:50]}...")
        
        try:
            # 复制基础API格式并设置新提示词
            import copy
            api_prompt = copy.deepcopy(base_api_prompt)
            api_prompt = set_prompt_text(api_prompt, prompt_text, i)
            
            # 发送到队列
            result = queue_prompt(api_prompt)
            
            if result and 'prompt_id' in result:
                prompt_id = result['prompt_id']
                print(f"   已加入队列: {prompt_id[:20]}...")
                
                print("   等待生成...", end="", flush=True)
                history = wait_for_completion(prompt_id)
                
                if history:
                    print(" 完成!")
                    success_count += 1
                else:
                    print(" 超时")
            else:
                print("   发送失败")
        
        except Exception as e:
            print(f"   出错: {e}")
        
        time.sleep(1)
    
    print()
    print("=" * 60)
    print(f"完成! 成功: {success_count}/{len(prompts)}")
    print(f"图片输出目录: D:\\output\\xitu")
    print("=" * 60)


if __name__ == "__main__":
    main()
