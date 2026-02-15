import os

output_dir = r"D:\xiaohongshu-crawler\output"
files = os.listdir(output_dir)

for f in files:
    if f.startswith("knowledge_base") and f.endswith(".txt"):
        print(f"File: {f}")
        try:
            full_path = os.path.join(output_dir, f)
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(f"Content length: {len(content)}")
                print(content[:500])
        except Exception as e:
            print(f"Error reading: {e}")
        print("-" * 20)
