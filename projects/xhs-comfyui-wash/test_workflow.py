"""
测试工作流加载
"""

import json
from pathlib import Path

workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222.json"

print("=" * 60)
print("测试工作流加载")
print("=" * 60)

try:
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    print(f"[成功] 工作流加载完成")
    print(f"[信息] 节点数量: {len(workflow)}")

    # 查找LoadImage节点
    print("\n[查找] LoadImage节点:")
    found = False
    for node_id, node in workflow.items():
        if isinstance(node, dict):
            class_type = node.get("class_type", "")
            if "LoadImage" in class_type:
                print(f"  节点ID: {node_id}")
                print(f"  类型: {class_type}")
                print(f"  输入: {node.get('inputs', {})}")
                found = True
                break

    if not found:
        print("  [警告] 未找到LoadImage节点")
        print("\n[所有节点类型]:")
        node_types = {}
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "Unknown")
                node_types[class_type] = node_types.get(class_type, 0) + 1

        for class_type, count in sorted(node_types.items()):
            print(f"  - {class_type}: {count}")

except Exception as e:
    print(f"[错误] {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
