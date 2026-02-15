"""
ComfyUI自动启动脚本
尝试多种方式启动ComfyUI
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

# 配置
COMFYUI_DIR = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI"
PYTHON_EXE = (
    r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\python\python.exe"
)
LAUNCHER_EXE = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\绘世启动器.exe"
API_URL = "http://192.168.11.158:8188"


def is_comfyui_running():
    """检查ComfyUI是否运行"""
    try:
        response = requests.get(f"{API_URL}/system_stats", timeout=3)
        return response.status_code == 200
    except:
        return False


def start_comfyui_direct():
    """方式1: 直接用Python启动ComfyUI"""
    print("[尝试] 直接启动ComfyUI...")

    main_py = Path(COMFYUI_DIR) / "main.py"
    if not main_py.exists():
        print(f"[错误] 找不到 {main_py}")
        return False

    try:
        # 启动ComfyUI
        process = subprocess.Popen(
            [PYTHON_EXE, str(main_py), "--listen", "192.168.11.158", "--port", "8188"],
            cwd=COMFYUI_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        print(f"[启动] PID: {process.pid}")
        return True

    except Exception as e:
        print(f"[错误] 启动失败: {e}")
        return False


def start_comfyui_launcher():
    """方式2: 启动秋叶启动器"""
    print("[尝试] 启动秋叶启动器...")

    if not Path(LAUNCHER_EXE).exists():
        print(f"[错误] 找不到启动器: {LAUNCHER_EXE}")
        return False

    try:
        process = subprocess.Popen(
            [LAUNCHER_EXE], creationflags=subprocess.CREATE_NEW_CONSOLE
        )

        print(f"[启动] 启动器PID: {process.pid}")
        print("[提示] 请在启动器中点击'启动'按钮")
        return True

    except Exception as e:
        print(f"[错误] 启动失败: {e}")
        return False


def wait_for_comfyui(timeout=120):
    """等待ComfyUI启动"""
    print(f"[等待] 等待ComfyUI启动 (超时: {timeout}秒)...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_comfyui_running():
            print("[成功] ComfyUI已启动!")
            return True

        elapsed = int(time.time() - start_time)
        if elapsed % 10 == 0:
            print(f"  等待中... ({elapsed}/{timeout}秒)")

        time.sleep(2)

    print("[超时] ComfyUI未启动")
    return False


def main():
    """主函数"""
    print("=" * 60)
    print("ComfyUI启动工具")
    print("=" * 60)

    # 检查是否已运行
    if is_comfyui_running():
        print("\n[信息] ComfyUI已在运行")
        print(f"  地址: {API_URL}")
        return True

    print("\n[信息] ComfyUI未运行，尝试启动...")

    # 尝试直接启动
    if start_comfyui_direct():
        if wait_for_comfyui():
            return True

    # 如果直接启动失败，尝试启动器
    print("\n[提示] 直接启动失败，尝试启动秋叶启动器...")
    if start_comfyui_launcher():
        print("\n" + "=" * 60)
        print("启动器已打开!")
        print("=" * 60)
        print("\n请手动操作:")
        print("  1. 在启动器窗口中点击'启动'按钮")
        print("  2. 等待ComfyUI完全启动")
        print("  3. 再次运行此脚本或洗图脚本")
        print("\n或者等待120秒自动检测...")

        if wait_for_comfyui(timeout=120):
            return True

    print("\n[失败] 无法启动ComfyUI")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
