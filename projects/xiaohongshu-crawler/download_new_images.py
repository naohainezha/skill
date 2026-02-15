import json
import os
import urllib.request
import time

def download_images(json_path, keyword):
    """Download images from the XHS crawler JSON output."""
    save_dir = os.path.join(r"D:\xiaohongshu-crawler\images", keyword)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Downloading images to {save_dir}...")
    count = 0
    downloaded = 0
    
    for note in data:
        images = note.get('images_list', [])
        for url in images:
            if not url: continue
            try:
                filename = url.split('/')[-1].split('?')[0]
                if not filename.endswith(('.jpg', '.png', '.webp')):
                    filename += ".jpg"
                
                filepath = os.path.join(save_dir, filename)
                
                if not os.path.exists(filepath):
                    try:
                        # Add User-Agent header
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as response, open(filepath, 'wb') as out_file:
                             out_file.write(response.read())
                        downloaded += 1
                    except Exception as e:
                        print(f"Failed to download {url}: {e}")
                count += 1
            except Exception as e:
                print(f"Error processing {url}: {e}")
    
    print(f"Processed {count} images. Downloaded {downloaded} new images.")

if __name__ == "__main__":
    # Find latest JSON
    import glob
    files = glob.glob(r"D:\xiaohongshu-crawler\output\*.json")
    if files:
        latest = max(files, key=os.path.getmtime)
        print(f"Using data file: {latest}")
        download_images(latest, "眼镜穿搭")
    else:
        print("No JSON files found!")
