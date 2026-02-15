import json
import urllib.request
import urllib.error
import time
import uuid
import os
import sys
import glob

# ============ Configuration ============
COMFYUI_HOST = "127.0.0.1"
COMFYUI_PORT = 8188
COMFYUI_URL = f"http://{COMFYUI_HOST}:{COMFYUI_PORT}"
WORKFLOW_FILE = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\提示词反推.json"
IMAGE_DIR = r"D:\xiaohongshu-crawler\images\眼镜穿搭" # Update to the new keyword folder
OUTPUT_FILE_BASE = "123" # Base filename requested by user

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

def load_workflow_api(image_index, output_name):
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
                api_node["inputs"]["mode"] = "incremental_image"
                api_node["inputs"]["seed"] = vals[1]
                api_node["inputs"]["index"] = image_index # Dynamic index
                api_node["inputs"]["label"] = vals[4]
                api_node["inputs"]["path"] = IMAGE_DIR # Override path
                api_node["inputs"]["pattern"] = vals[6]
                api_node["inputs"]["allow_RGBA_output"] = vals[7]
                if len(vals) > 8:
                    api_node["inputs"]["filename_text_extension"] = vals[8]

            elif node_type == "Qwen3_VQA":
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
                    api_node["inputs"]["attention"] = vals[10]

            elif node_type == "easy saveText":
                # widgets: [output_file_path, file_name, file_extension, overwrite]
                if len(vals) >= 4:
                    api_node["inputs"]["output_file_path"] = vals[0] # Keep original path (D:\xiaohongshu-crawler)
                    api_node["inputs"]["file_name"] = output_name # Dynamic filename
                    api_node["inputs"]["file_extension"] = vals[2]
                    api_node["inputs"]["overwrite"] = vals[3]

            elif node_type == "Save Text File":
                # WAS Suite Save Text File
                # widgets: [path, filename_prefix, filename_delimiter, filename_number_padding, file_extension, encoding, suffix]
                # We want to force the path and prefix
                if len(vals) >= 4:
                    api_node["inputs"]["path"] = r"D:\xiaohongshu-crawler"
                    # The workflow uses "ComfyUI" as default prefix. We want "123_001" etc.
                    # But wait, output_name already includes "123_001".
                    # If we set prefix="123_001", delimiter="_", padding=0 -> "123_001.txt" (hopefully)
                    api_node["inputs"]["filename_prefix"] = output_name 
                    api_node["inputs"]["filename_delimiter"] = "_" # vals[2] is "_"
                    api_node["inputs"]["filename_number_padding"] = 0 # Disable auto-padding
                    if len(vals) > 4:
                        api_node["inputs"]["file_extension"] = vals[4] # .txt
                    if len(vals) > 5:
                        api_node["inputs"]["encoding"] = vals[5] # utf-8
            
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
    # 1. Get list of images to know count
    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory not found: {IMAGE_DIR}")
        return

    # Count images (supports jpg, png, webp)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp']
    images = []
    for ext in image_extensions:
        images.extend(glob.glob(os.path.join(IMAGE_DIR, ext)))
    
    total_images = len(images)
    print(f"Found {total_images} images in {IMAGE_DIR}")
    
    if total_images == 0:
        return

    print("=== Starting Batch Processing ===")
    
    # Combined file path
    combined_path = os.path.join(r"D:\xiaohongshu-crawler", "123_ALL_COMBINED.txt")
    
    # Clear combined file content at start if starting fresh
    # But since we resume, we might want to keep it? 
    # Let's verify: if output_name 001 exists, we skip. So we should append only new stuff.
    # To be safe and clean: We will reconstruct it from available txt files at the end, 
    # BUT also append continuously for real-time visibility.
    
    for i in range(total_images):
        output_name = f"{OUTPUT_FILE_BASE}_{i+1:03d}"
        
        # ... (skip logic) ...
        expected_file = os.path.join(r"D:\xiaohongshu-crawler", f"{output_name}.txt")
        if os.path.exists(expected_file) and os.path.getsize(expected_file) > 0:
            print(f"Skipping image {i+1} (File exists: {output_name}.txt)")
            continue

        print(f"Processing image {i+1}/{total_images} -> {output_name}.txt")
        
        api_payload = load_workflow_api(i, output_name)
        result = queue_prompt(api_payload)
        
        if not result:
            print("Failed to queue.")
            continue
            
        prompt_id = result['prompt_id']
        
        # Wait for completion with timeout
        start_time = time.time()
        timeout = 180 # Increased timeout
        completed = False
        history = {}
        
        while (time.time() - start_time) < timeout:
            h = get_history(prompt_id)
            if h and prompt_id in h:
                history = h
                completed = True
                break
            time.sleep(2) # Relaxed polling
            
        if not completed:
            print(f"Timeout waiting for image {i+1}")
            continue

        # Get text
        outputs = history[prompt_id].get('outputs', {})
        text_out = ""
        
        # Check Node 1 (ShowText)
        if '1' in outputs and 'text' in outputs['1']:
             val = outputs['1']['text']
             if isinstance(val, list): val = val[0]
             text_out = val
        
        # Check Node 2 (Qwen)
        if not text_out and '2' in outputs:
             val = outputs['2'].get('STRING') or outputs['2'].get('text')
             if val:
                 if isinstance(val, list): val = val[0]
                 text_out = val

        if text_out:
             # Ensure encoding safety
             if isinstance(text_out, bytes):
                 text_out = text_out.decode('utf-8', errors='ignore')
             
             print(f"  Generated: {text_out[:30]}...")
             
             # Save to individual file
             try:
                 with open(expected_file, 'w', encoding='utf-8') as f:
                     f.write(text_out)
             except Exception as e:
                 print(f"Error saving individual file: {e}")

             # Append to combined file immediately (Open/Write/Close for each iteration to avoid buffer issues)
             try:
                 with open(combined_path, 'a', encoding='utf-8') as f:
                     # Add a separator if file not empty
                     if os.path.getsize(combined_path) > 0:
                         f.write("\n\n")
                     f.write(f"--- Image {i+1} ({output_name}) ---\n")
                     f.write(text_out)
                     f.write("\n")
             except Exception as e:
                 print(f"Error appending to combined file: {e}")
                 
        else:
             print("  Done (Text saved by ComfyUI or Empty)")
             # Check if ComfyUI saved it, if so, append to combined
             time.sleep(2) # Give file system time to sync
             
             # WAS Node saves as [prefix]_[number].txt usually
             # We set prefix=output_name (e.g. 123_001), padding=0. 
             # It might save as 123_001.txt OR 123_001_.txt depending on delimiter
             
             possible_files = [
                 expected_file,
                 os.path.join(r"D:\xiaohongshu-crawler", f"{output_name}_.txt"),
                 os.path.join(r"D:\xiaohongshu-crawler", f"{output_name}_0001.txt")
             ]
             
             found_content = ""
             for pf in possible_files:
                 if os.path.exists(pf):
                     try:
                         with open(pf, 'r', encoding='utf-8') as rf:
                             found_content = rf.read()
                         break
                     except: pass
             
             if found_content:
                 try:
                     with open(combined_path, 'a', encoding='utf-8') as f:
                         if os.path.getsize(combined_path) > 0:
                             f.write("\n\n")
                         f.write(f"--- Image {i+1} ({output_name}) ---\n")
                         f.write(found_content)
                         f.write("\n")
                 except: pass

    print(f"=== Batch Complete ===")

if __name__ == "__main__":
    main()
