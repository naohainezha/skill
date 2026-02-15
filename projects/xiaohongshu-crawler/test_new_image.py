import json
import urllib.request
import urllib.error
import time
import uuid
import os
import sys

# ============ Configuration ============
COMFYUI_HOST = "127.0.0.1"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}"
WORKFLOW_FILE = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json"
IMAGE_DIR = r"D:\xiaohongshu-crawler\images\眼镜推荐"

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

def load_workflow_api(image_index=0):
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
        
        # Map widgets
        if 'widgets_values' in node:
            vals = node['widgets_values']
            
            if node_type == "Load Image Batch":
                # ["incremental_image", seed, "randomize", index, "Batch 001", path, "*", "false", "true"]
                # We want to override path and index
                api_node["inputs"]["mode"] = "incremental_image"
                api_node["inputs"]["seed"] = vals[1]
                api_node["inputs"]["index"] = image_index # Force index
                api_node["inputs"]["label"] = vals[4]
                api_node["inputs"]["path"] = IMAGE_DIR # Override path
                api_node["inputs"]["pattern"] = vals[6]
                api_node["inputs"]["allow_RGBA_output"] = vals[7]
                if len(vals) > 8:
                    api_node["inputs"]["filename_text_extension"] = vals[8]

            elif node_type == "Qwen3_VQA":
                # widgets: [text, model, quant, keep_loaded, temp, max_tokens, min_pix, max_pix, seed, control, attention]
                if len(vals) >= 11:
                    api_node["inputs"]["text"] = vals[0]
                    api_node["inputs"]["model"] = vals[1]
                    api_node["inputs"]["quantization"] = vals[2]
                    api_node["inputs"]["keep_model_loaded"] = vals[3]
                    api_node["inputs"]["temperature"] = vals[4]
                    api_node["inputs"]["max_new_tokens"] = vals[5]
                    api_node["inputs"]["min_pixels"] = vals[6]
                    api_node["inputs"]["max_pixels"] = vals[7]
                    api_node["inputs"]["seed"] = vals[8]
                    # vals[9] is control, skip
                    api_node["inputs"]["attention"] = vals[10]

            elif node_type == "easy saveText":
                # widgets: [output_file_path, file_name, file_extension, overwrite]
                if len(vals) >= 4:
                    api_node["inputs"]["output_file_path"] = vals[0]
                    api_node["inputs"]["file_name"] = vals[1]
                    api_node["inputs"]["file_extension"] = vals[2]
                    api_node["inputs"]["overwrite"] = vals[3] # Respect overwrite setting (true in file)
            
            elif node_type == "ShowText|pysssss":
                 # widgets: [text] - usually output, but sometimes input?
                 # ShowText usually just displays, but API needs inputs if they are widgets
                 pass

        # Map linked inputs
        if 'inputs' in node:
            for inp in node['inputs']:
                if inp.get('link'):
                    link_id = inp['link']
                    for l in workflow['links']:
                        if l[0] == link_id:
                            source_id = str(l[1])
                            source_slot = l[2]
                            api_node["inputs"][inp['name']] = [source_id, source_slot]
                            break
        
        api_prompt[node_id] = api_node
        
    return api_prompt

def main():
    print(f"=== Testing New Image Processing ===")
    print(f"Workflow: {WORKFLOW_FILE}")
    print(f"Image Dir: {IMAGE_DIR}")
    
    # Let's try index 1 (second image) to ensure it's a 'new' one compared to previous runs
    # Or just index 0 if we want to restart. Let's do index 0 for simplicity.
    image_index = 0
    
    api_payload = load_workflow_api(image_index)
    
    # Save debug payload
    with open("debug_test_payload.json", "w", encoding="utf-8") as f:
        json.dump(api_payload, f, indent=2, ensure_ascii=False)
        
    print("Queuing prompt...")
    result = queue_prompt(api_payload)
    
    if not result:
        print("Failed to queue.")
        return
        
    prompt_id = result['prompt_id']
    print(f"Prompt ID: {prompt_id}")
    
    print("Waiting for execution...")
    while True:
        history = get_history(prompt_id)
        if history and prompt_id in history:
            print("Execution finished.")
            # Print outputs if any
            outputs = history[prompt_id].get('outputs', {})
            print(f"Outputs: {json.dumps(outputs, indent=2, ensure_ascii=False)}")
            break
        time.sleep(1)

if __name__ == "__main__":
    main()
