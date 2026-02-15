"""
ComfyUI洗图自动化工具 - 配置文件
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# ComfyUI配置
COMFYUI_CONFIG = {
    # 秋叶启动器路径
    "launcher_path": r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\绘世启动器.exe",
    # ComfyUI根目录
    "comfyui_dir": r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI",
    # 工作流文件路径 (API格式)
    "workflow_path": r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json",
    # API地址
    "api_url": "http://192.168.11.158:8188",
    # WebSocket地址
    "ws_url": "ws://192.168.11.158:8188/ws",
    # 输出目录 (ComfyUI默认输出)
    "comfyui_output": r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\output",
}

# 洗图配置
WASH_CONFIG = {
    # 默认输入目录
    "input_dir": str(PROJECT_ROOT / "input"),
    # 默认输出目录
    "output_dir": str(PROJECT_ROOT / "output"),
    # 支持的图片格式
    "image_extensions": [".jpg", ".jpeg", ".png", ".webp"],
    # 队列间隔(秒) - 避免GPU内存不足
    "queue_interval": 5,
    # 最大重试次数
    "max_retries": 3,
    # 启动超时(秒)
    "startup_timeout": 120,
    # 任务超时(秒)
    "task_timeout": 300,
}

# 工作流节点配置 (根据z洗图1222.json结构调整)
WORKFLOW_NODES = {
    # 输入节点ID或类型
    "input_node_types": ["LoadImage", "LoadImageBatch"],
    # 输出节点ID或类型
    "output_node_types": ["SaveImage", "PreviewImage"],
}


def get_comfyui_config():
    """获取ComfyUI配置"""
    return COMFYUI_CONFIG.copy()


def get_wash_config():
    """获取洗图配置"""
    return WASH_CONFIG.copy()


def validate_paths():
    """
    验证路径是否存在

    Returns:
        (bool, list) - (是否全部有效, 错误信息列表)
    """
    config = get_comfyui_config()
    errors = []

    # 检查启动器
    if not Path(config["launcher_path"]).exists():
        errors.append(f"启动器不存在: {config['launcher_path']}")

    # 检查ComfyUI目录
    if not Path(config["comfyui_dir"]).exists():
        errors.append(f"ComfyUI目录不存在: {config['comfyui_dir']}")

    # 检查工作流文件
    if not Path(config["workflow_path"]).exists():
        errors.append(f"工作流文件不存在: {config['workflow_path']}")

    return len(errors) == 0, errors
