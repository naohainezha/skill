"""
测试ComfyUI洗图功能
"""

import sys
from pathlib import Path

# 添加项目目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from wash import ComfyUIWasher
from config import validate_paths

print("=" * 60)
print("ComfyUI洗图功能测试")
print("=" * 60)

# 1. 验证路径
print("\n[1] 验证路径...")
valid, errors = validate_paths()
if not valid:
    print("[错误] 路径验证失败:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
print("[成功] 路径验证通过")

# 2. 检测ComfyUI状态
print("\n[2] 检测ComfyUI状态...")
washer = ComfyUIWasher()
if washer.is_running():
    print("[成功] ComfyUI正在运行")
else:
    print("[警告] ComfyUI未运行")
    print("  请先启动ComfyUI，然后再次测试")
    print("  启动命令: 运行秋叶启动器")
    sys.exit(1)

# 3. 加载工作流
print("\n[3] 加载工作流...")
workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"
try:
    workflow = washer.load_workflow(workflow_path)
    print(f"[成功] 工作流加载完成")
    print(f"  节点数量: {len(workflow)}")

    # 显示LoadImage节点
    if "35" in workflow:
        node = workflow["35"]
        print(f"  LoadImage节点(35):")
        print(f"    当前图片: {node['inputs'].get('image', 'N/A')}")
except Exception as e:
    print(f"[错误] 加载工作流失败: {e}")
    sys.exit(1)

# 4. 测试修改工作流
print("\n[4] 测试修改工作流...")
test_image = "test_image.jpg"
modified_workflow = washer.modify_workflow_for_image(workflow, test_image)
if modified_workflow["35"]["inputs"]["image"] == test_image:
    print(f"[成功] 工作流修改成功")
    print(f"  新图片: {test_image}")
else:
    print("[错误] 工作流修改失败")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n可以开始洗图了:")
print("  python wash.py <输入目录> <输出目录>")
print("\n示例:")
print('  python wash.py "C:\\path\\to\\filtered" "C:\\path\\to\\washed"')
