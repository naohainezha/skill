"""
ComfyUI 方案对比测试脚本
生成同一个提示词的三种方案对比图，使用相同的Seed
"""

import json
import urllib.request
import time
import uuid
import os
import sys
import copy

# ============ 配置 ============
COMFYUI_URL = "http://192.168.11.158:8188"
WORKFLOW_FILE = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\zimage文生图0106.json"
OUTPUT_DIR = r"D:\output\xitu"

# 测试提示词
PROMPT_TEXT = """
胶片感街拍。一个清爽的短发女生骑着复古自行车穿过阳光斑驳的林荫道。她穿着干净的白衬衫和卡其色背带裤，回头对着镜头开怀大笑，发丝在风中飞扬。背景是虚化的绿树和透下来的金光，光影斑驳地洒在她脸上。画面带有轻微的动态模糊和颗粒感，色彩浓郁复古，充满90年代的青春电影氛围。由iPhone 13 Pro模拟胶片模式拍摄。
"""

def get_base_workflow():
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    # 转换为API格式 (简化版逻辑，只提取需要的节点)
    # 这里直接复用之前生成的 debug_api_prompt.json 的结构更稳妥，
    # 但为了独立性，还是得重新解析。为免繁琐，我们假设 comfyui_generator.py 里的 load_workflow_api_format 是可靠的
    # 这里我们直接硬编码关键修改，基于 generator 的逻辑
    
    # 稍微hack一下，直接调用 generator 的函数
    from comfyui_generator import load_workflow_api_format
    return load_workflow_api_format()

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": str(uuid.uuid4())}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    return json.loads(urllib.request.urlopen(req).read())

def wait_for_completion(prompt_id):
    while True:
        try:
            history = json.loads(urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}").read())
            if prompt_id in history:
                return
        except:
            pass
        time.sleep(1)

def set_common_params(workflow, seed):
    # 设置提示词
    workflow["33"]["inputs"]["text"] = PROMPT_TEXT
    
    # 设置Seed
    if "34" in workflow: workflow["34"]["inputs"]["noise_seed"] = seed
    if "35" in workflow: workflow["35"]["inputs"]["noise_seed"] = seed
    if "36" in workflow: workflow["36"]["inputs"]["seed"] = seed
    
    return workflow

def run_test():
    print("开始方案对比测试...")
    print(f"提示词: {PROMPT_TEXT.strip()[:50]}...")
    
    # 固定Seed以便对比
    SEED = int(time.time() * 1000) % (2**32)
    print(f"使用固定Seed: {SEED}")
    
    base_wf = get_base_workflow()
    
    # ==========================================
    # 方案1: 优化版 (960x1280 -> 放大 -> 3次采样)
    # ==========================================
    print("\n[1/3] 生成: 优化版 (Upscale + 3 Pass)...")
    wf1 = copy.deepcopy(base_wf)
    wf1 = set_common_params(wf1, SEED)
    
    # 设置初始分辨率 960x1280
    wf1["31"]["inputs"]["width"] = 960
    wf1["31"]["inputs"]["height"] = 1280
    # 确保 Upscale 节点存在并设置目标
    wf1["10"]["inputs"]["largest_size"] = 1920
    # 设置文件名前缀
    wf1["3"]["inputs"]["filename_prefix"] = "TEST_OPT_3PASS_"
    
    res1 = queue_prompt(wf1)
    print(f"任务ID: {res1['prompt_id']}")
    wait_for_completion(res1['prompt_id'])
    print("完成!")

    # ==========================================
    # 方案2: 原分辨率 (1440x1920 -> 3次采样)
    # ==========================================
    print("\n[2/3] 生成: 原分辨率版 (Raw + 3 Pass)...")
    wf2 = copy.deepcopy(base_wf)
    wf2 = set_common_params(wf2, SEED)
    
    # 保持原分辨率 1440x1920
    wf2["31"]["inputs"]["width"] = 1440
    wf2["31"]["inputs"]["height"] = 1920
    # Upscale 节点虽然在，但不起作用(目标<原图或相等)
    wf2["10"]["inputs"]["largest_size"] = 1920 
    
    wf2["3"]["inputs"]["filename_prefix"] = "TEST_RAW_3PASS_"
    
    res2 = queue_prompt(wf2)
    print(f"任务ID: {res2['prompt_id']}")
    wait_for_completion(res2['prompt_id'])
    print("完成!")

    # ==========================================
    # 方案3: 原分辨率 (1440x1920 -> 仅2次采样)
    # ==========================================
    print("\n[3/3] 生成: 原分辨率版 (Raw + 2 Pass Only)...")
    wf3 = copy.deepcopy(base_wf)
    wf3 = set_common_params(wf3, SEED)
    
    # 保持原分辨率
    wf3["31"]["inputs"]["width"] = 1440
    wf3["31"]["inputs"]["height"] = 1920
    
    # 绕过 Node 36 (KSampler3) 和 Node 11 (VAEDecode2)
    # 将 Node 3 (Save) 的输入直接连到 Node 12 (VAEDecode1)
    wf3["3"]["inputs"]["images"] = ["12", 0]
    
    # 删除不需要的节点
    for nid in ["36", "11", "10", "7", "8", "24"]: # 清理相关链
        if nid in wf3: del wf3[nid]
        
    wf3["3"]["inputs"]["filename_prefix"] = "TEST_RAW_2PASS_"
    
    res3 = queue_prompt(wf3)
    print(f"任务ID: {res3['prompt_id']}")
    wait_for_completion(res3['prompt_id'])
    print("完成!")
    
    print("\n所有测试生成完毕！请查看 D:\\output\\xitu 目录下的 TEST_ 开头文件。")

if __name__ == "__main__":
    run_test()
