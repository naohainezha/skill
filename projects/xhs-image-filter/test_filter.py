"""
测试脚本：直接调用筛选功能
"""

import sys
from pathlib import Path

# 添加项目目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from filter import ImageFilter
from config import get_config

# 配置
input_folder = r"C:\Users\admin\Projects\XHS-Downloader\Volume\Download"
output_folder = r"C:\Users\admin\Projects\xhs-image-filter\output"

print("=" * 60)
print("小红书素材整理工具 - 人脸检测筛选")
print("=" * 60)
print(f"输入: {input_folder}")
print(f"输出: {output_folder}")
print(f"人脸占比阈值: 10% - 90%")
print("=" * 60)
print()

# 运行筛选
try:
    with ImageFilter(
        min_detection_confidence=0.5,
        min_face_ratio=0.10,
        max_face_ratio=0.90,
        copy_mode=True,
    ) as filter_obj:
        filtered_dir = str(Path(output_folder) / "filtered")
        rejected_dir = str(Path(output_folder) / "rejected")

        config = get_config()
        result = filter_obj.filter_folder(
            input_folder=input_folder,
            output_filtered=filtered_dir,
            output_rejected=rejected_dir,
            supported_extensions=config["image_extensions"],
        )

    print()
    print("=" * 60)
    print("筛选结果")
    print("=" * 60)
    print(f"总图片数: {result['total']}")
    print(f"通过筛选: {result['passed']}")
    print(f"筛除总计: {result['total'] - result['passed']}")
    print(f"  - 无人脸: {result['rejected']['no_face']}")
    print(f"  - 人脸太小: {result['rejected']['small_face']}")
    print(f"  - 人脸太大: {result['rejected']['large_face']}")
    print(f"  - 置信度低: {result['rejected']['low_confidence']}")
    print(f"  - 处理错误: {result['rejected']['error']}")
    print("=" * 60)

    pass_rate = result["passed"] / result["total"] * 100 if result["total"] > 0 else 0
    print(f"通过率: {pass_rate:.1f}%")
    print()
    print(f"合格素材: {filtered_dir}")
    print(f"筛除图片: {rejected_dir}")

except Exception as e:
    print(f"错误: {e}")
    import traceback

    traceback.print_exc()
