import json
import urllib.request
import urllib.error
import time
import uuid
import os
import sys
import glob
import subprocess

# ============ Configuration ============
COMFYUI_HOST = "127.0.0.1"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}"
WORKFLOW_FILE = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json"
OUTPUT_DIR = r"D:\xiaohongshu-crawler\output"
IMAGE_DIR_BASE = r"D:\xiaohongshu-crawler\images"

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": str(uuid.uuid4())}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print(f"Error queuing prompt: {e}")
        try:
            print(f"Error body: {e.read().decode('utf-8')}")
        except:
            pass
        return None
    except Exception as e:
        print(f"Error queuing prompt: {e}")
        return None

def get_history(prompt_id):
    try:
        response = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
        return json.loads(response.read())
    except Exception as e:
        print(f"Error getting history: {e}")
        return None

def download_images(json_path, keyword):
    """Download images from the XHS crawler JSON output."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    save_dir = os.path.join(IMAGE_DIR_BASE, keyword)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    image_paths = []
    print(f"Downloading images to {save_dir}...")
    
    count = 0
    for note in data:
        images = note.get('images_list', [])
        if not images and 'image_list' in note:
             images = note['image_list']
        
        for url in images:
            if not url: continue
            try:
                filename = url.split('/')[-1].split('?')[0]
                if not filename.endswith(('.jpg', '.png', '.webp')):
                    filename += ".jpg"
                
                filepath = os.path.join(save_dir, filename)
                
                if not os.path.exists(filepath):
                    # Use urllib instead of requests to avoid dependency issues if requests is missing
                    try:
                        with urllib.request.urlopen(url, timeout=10) as response, open(filepath, 'wb') as out_file:
                             out_file.write(response.read())
                        image_paths.append(filepath)
                        count += 1
                    except Exception as e:
                        print(f"Failed to download {url}: {e}")
                else:
                    image_paths.append(filepath)
                    
            except Exception as e:
                print(f"Error processing {url}: {e}")
    
    print(f"Downloaded {count} new images. Total ready: {len(image_paths)}")
    return save_dir, image_paths

def load_workflow_api():
    """
    Convert the UI workflow to API format by manually mapping widgets to inputs.
    """
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    api_prompt = {}
    
    for node in workflow['nodes']:
        node_id = str(node['id'])
        node_type = node['type']
        
        api_node = {
            "class_type": node_type,
            "inputs": {}
        }
        
        # 1. Map Widgets to Inputs (Crucial step for UI->API conversion)
        if 'widgets_values' in node:
            vals = node['widgets_values']
            
            if node_type == "Load Image Batch":
                # Mapping based on typical WAS Node structure and inspection
                # Widgets: [mode, seed, seed_control, index, label, path, pattern, allow_rgba, ext]
                if len(vals) >= 8:
                    api_node["inputs"]["mode"] = vals[0]
                    api_node["inputs"]["seed"] = vals[1]
                    api_node["inputs"]["index"] = vals[3]
                    api_node["inputs"]["label"] = vals[4]
                    api_node["inputs"]["path"] = vals[5]
                    api_node["inputs"]["pattern"] = vals[6]
                    api_node["inputs"]["allow_RGBA_output"] = vals[7]
                    if len(vals) > 8:
                        api_node["inputs"]["filename_text_extension"] = vals[8]

            elif node_type == "Qwen3_VQA":
                # Ensure all required inputs are mapped from widgets
                # Widgets: [text, model, quantization, keep_model_loaded, temperature, max_new_tokens, min_pixels, max_pixels, seed, seed_control, attention]
                # Note: 'seed_control' (index 9) is usually not an input to the node logic, 'seed' (index 8) is.
                # 'attention' is likely index 10.
                
                # Default mapping based on inspection
                if len(vals) >= 2:
                    api_node["inputs"]["text"] = vals[0]
                    api_node["inputs"]["model"] = vals[1]
                if len(vals) >= 11:
                    api_node["inputs"]["quantization"] = vals[2]
                    api_node["inputs"]["keep_model_loaded"] = vals[3]
                    api_node["inputs"]["temperature"] = vals[4]
                    api_node["inputs"]["max_new_tokens"] = vals[5]
                    api_node["inputs"]["min_pixels"] = vals[6]
                    api_node["inputs"]["max_pixels"] = vals[7]
                    api_node["inputs"]["seed"] = vals[8]
                    # vals[9] is 'control_after_generate' (randomize/fixed), ignore
                    api_node["inputs"]["attention"] = vals[10]
            
            elif node_type == "SaveText|pysssss":
                # widgets: [root_dir, file, append, insert]
                if len(vals) >= 4:
                    api_node["inputs"]["root_dir"] = vals[0]
                    api_node["inputs"]["file"] = vals[1]
                    api_node["inputs"]["append"] = vals[2]
                    api_node["inputs"]["insert"] = vals[3]

        # 2. Map Linked Inputs
        if 'inputs' in node:
            for inp in node['inputs']:
                if inp.get('link'):
                    link_id = inp['link']
                    # Find the source node for this link
                    for l in workflow['links']:
                        if l[0] == link_id:
                            source_id = str(l[1])
                            source_slot = l[2]
                            api_node["inputs"][inp['name']] = [source_id, source_slot]
                            break
        
        api_prompt[node_id] = api_node
        
    return api_prompt

def main():
    if len(sys.argv) < 2:
        print("Usage: python xhs_prompt_learner.py <keyword> [count] [--skip-crawl]")
        return
    
    keyword = sys.argv[1]
    count = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "5"
    skip_crawl = "--skip-crawl" in sys.argv

    if not skip_crawl:
        print(f"=== Step 1: Searching Xiaohongshu for '{keyword}' ({count} notes) ===")
        subprocess.run(["python", "search_xhs.py", keyword, count], cwd=r"D:\xiaohongshu-crawler")
    else:
        print("=== Step 1: Skipping Search (using existing data) ===")
    
    list_of_files = glob.glob(os.path.join(OUTPUT_DIR, 'notes_*.json'))
    if not list_of_files:
        print("No JSON found. Crawler failed?")
        return
    latest_file = max(list_of_files, key=os.path.getmtime)
    print(f"Processing data from: {latest_file}")
    
    print(f"=== Step 2: Downloading Images ===")
    image_dir, image_paths = download_images(latest_file, keyword)
    if not image_paths:
        print("No images found.")
        return
        
    print(f"=== Step 3: Processing in ComfyUI ===")
    
    api_template = load_workflow_api()
    
    if '4' not in api_template:
        print("Error: Node 4 (Load Image Batch) not found in workflow.")
        return

    # Add Save Text File node (WAS Suite)
    api_template["100"] = {
        "class_type": "Save Text File",
        "inputs": {
            "text": ["2", 0],
            "path": r"D:\xiaohongshu-crawler",
            "filename_prefix": "123",
            "filename_delimiter": "_",
            "filename_number_padding": 4
        }
    }
    
    # Remove PreviewImage (Node 3) and others to force execution of other paths
    for node_to_remove in ["3", "1", "5", "99"]:
        if node_to_remove in api_template:
            del api_template[node_to_remove]

    api_template['4']['inputs']['mode'] = 'incremental_image'
    
    knowledge_base = []
    
    for i in range(len(image_paths)):
        print(f"Processing image {i+1}/{len(image_paths)}...")
        
        # Update inputs to force re-execution
        api_template['4']['inputs']['index'] = i
        
        # Randomize seeds to prevent caching
        import random
        new_seed = random.randint(1, 999999999999999)
        
        if 'seed' in api_template['4']['inputs']:
             api_template['4']['inputs']['seed'] = new_seed
        
        # Qwen node seed (if available in inputs, otherwise try to add it)
        # Check Node 2 inputs
        if '2' in api_template:
            # Qwen seed is usually a widget, so it should be in 'inputs' if we mapped it or we can add it
            api_template['2']['inputs']['seed'] = new_seed

        with open("debug_payload.json", "w", encoding="utf-8") as f:
            json.dump(api_template, f, indent=2, ensure_ascii=False)

        result = queue_prompt(api_template)
        if not result or 'prompt_id' not in result:
            print("Failed to queue prompt.")
            continue
            
        prompt_id = result['prompt_id']
        
        while True:
            history = get_history(prompt_id)
            if history and prompt_id in history:
                break
            time.sleep(1)
        
        # DEBUG: Print whole history for the first item
        if i == 0:
            print(f"DEBUG: Full history for item 0: {json.dumps(history[prompt_id], indent=2, ensure_ascii=False)}")

        outputs = history[prompt_id].get('outputs', {})
        print(f"DEBUG: Outputs keys: {outputs.keys()}")
        if '2' in outputs:
            print(f"DEBUG: Node 2 output: {outputs['2']}")
        if '1' in outputs:
            print(f"DEBUG: Node 1 output: {outputs['1']}")

        text_content = ""
        
        if '1' in outputs:
            val = outputs['1'].get('text', [])
            if val:
                text_content = val[0] if isinstance(val, list) else str(val)
        
        if not text_content and '2' in outputs:
             val = outputs['2'].get('text', [])
             if val:
                 text_content = val[0]
                 
        if text_content:
            print(f"  Result: {text_content[:50]}...")
            knowledge_base.append(f"Image {i+1}:\n{text_content}\n")
        else:
            print("  No text output found.")
            
    # 5. Save Knowledge Base (only if we captured text manually)
    if knowledge_base:
        kb_path = os.path.join(OUTPUT_DIR, f"knowledge_base_{keyword}_captured.txt")
        with open(kb_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(knowledge_base))
        print(f"=== Done! Captured text saved to: {kb_path} ===")
    else:
        print(f"=== Done! Check output directory for ComfyUI generated files ===")

if __name__ == "__main__":
    main()
