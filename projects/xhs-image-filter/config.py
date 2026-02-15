"""
小红书素材整理自动化工具 - 配置文件
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 默认路径配置
DEFAULT_CONFIG = {
    # 输入输出路径
    "input_dir": str(PROJECT_ROOT / "input"),
    "output_dir": str(PROJECT_ROOT / "output"),
    "filtered_dir": str(PROJECT_ROOT / "output" / "filtered"),  # 筛选通过的图片
    "rejected_dir": str(PROJECT_ROOT / "output" / "rejected"),  # 被筛除的图片
    # 支持的图片格式
    "image_extensions": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"],
    # 人脸检测配置
    "face_detection": {
        "min_detection_confidence": 0.5,  # 人脸检测置信度阈值 (0-1)
        "min_face_ratio": 0.02,  # 最小人脸占比（脸部面积/图片面积）- 默认2%，适合全身照博主
        "max_face_ratio": 0.90,  # 最大人脸占比（避免特写过头）
        "model_selection": 1,  # MediaPipe模型：0=轻量，1=完整
    },
    # 处理配置
    "processing": {
        "preserve_structure": False,  # 是否保留原始目录结构
        "skip_duplicates": True,  # 是否跳过重复图片（基于文件hash）
        "copy_mode": True,  # True=复制，False=移动
    },
}


def get_config():
    """获取配置"""
    return DEFAULT_CONFIG.copy()


def get_rejected_subdir(reason: str) -> str:
    """
    根据筛除原因返回子目录名

    Args:
        reason: 筛除原因

    Returns:
        子目录路径
    """
    reason_map = {
        "no_face": "no_face",  # 无人脸
        "small_face": "small_face",  # 人脸太小
        "large_face": "large_face",  # 人脸太大（特写）
        "low_confidence": "low_confidence",  # 检测置信度低
        "error": "error",  # 处理错误
    }
    return reason_map.get(reason, "unknown")
