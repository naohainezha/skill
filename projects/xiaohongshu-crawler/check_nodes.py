import urllib.request
import json

url = "http://127.0.0.1:8188/object_info"
try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read())
        for node_name in data.keys():
            if "save" in node_name.lower() and "text" in node_name.lower():
                print(f"Found node: {node_name}")
except Exception as e:
    print(f"Error: {e}")
