import urllib.request
import json

url = "http://127.0.0.1:8188/object_info"
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
        node = data.get("Save Text File")
        if node:
            print(json.dumps(node, indent=2))
        else:
            print("Node not found")
except Exception as e:
    print(f"Error: {e}")
