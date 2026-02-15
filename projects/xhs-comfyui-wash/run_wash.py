"""
ComfyUI洗图执行脚本
请先确保ComfyUI已启动：运行秋叶启动器
"""

import sys
from pathlib import Path

# 添加项目目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from wash import ComfyUIWasher

print("=" * 60)
print("ComfyUI洗图执行")
print("=" * 60)

# 配置
input_folder = r"C:\Users\admin\Projects\xhs-image-filter\output\filtered"
workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"

print(f"\n输入文件夹: {input_folder}")
print(f"工作流: {workflow_path}")
print(f"ComfyUI地址: http://192.168.11.158:8188")

# 检查输入
if not Path(input_folder).exists():
    print(f"\n[错误] 输入文件夹不存在: {input_folder}")
    sys.exit(1)

# 执行洗图
washer = ComfyUIWasher()
result = washer.wash_folder(input_folder, workflow_path)

print("\n" + "=" * 60)
if result["success"] > 0:
    print("[成功] 洗图任务已提交!")
    print(f"ComfyUI正在处理 {result['success']} 张图片...")
    print(f"请查看ComfyUI界面了解进度")
    print(
        f"\n输出位置: D:\\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\\ComfyUI\\output\\"
    )
else:
    print("[失败] 未能提交洗图任务")
    print("请确保:")
    print("  1. ComfyUI已启动 (运行秋叶启动器)")
    print("  2. 网络连接正常")
