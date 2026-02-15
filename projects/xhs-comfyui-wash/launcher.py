"""
ComfyUI洗图自动化工具 - 启动器模块
功能：检测ComfyUI状态，自动启动秋叶启动器
"""

import subprocess
import time
import requests
from pathlib import Path
from typing import Optional

from config import get_comfyui_config, get_wash_config


class ComfyUILauncher:
    """ComfyUI启动管理器"""

    def __init__(self):
        self.config = get_comfyui_config()
        self.wash_config = get_wash_config()
        self.process: Optional[subprocess.Popen] = None

    def is_running(self) -> bool:
        """
        检测ComfyUI是否正在运行

        Returns:
            bool - 是否运行中
        """
        try:
            response = requests.get(f"{self.config['api_url']}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False

    def start(self, wait: bool = True, timeout: int = None) -> bool:
        """
        启动ComfyUI (通过秋叶启动器)

        Args:
            wait: 是否等待启动完成
            timeout: 等待超时时间(秒)，默认使用配置

        Returns:
            bool - 是否启动成功
        """
        if timeout is None:
            timeout = self.wash_config["startup_timeout"]

        # 检查启动器是否存在
        launcher_path = Path(self.config["launcher_path"])
        if not launcher_path.exists():
            print(f"[错误] 启动器不存在: {launcher_path}")
            return False

        print(f"[信息] 正在启动ComfyUI...")
        print(f"[信息] 启动器: {launcher_path}")

        try:
            # 启动秋叶启动器
            # 注意：秋叶启动器可能不支持命令行参数，这里直接启动
            self.process = subprocess.Popen(
                [str(launcher_path)],
                cwd=str(launcher_path.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

            print(f"[信息] 启动器PID: {self.process.pid}")

            if wait:
                return self.wait_for_startup(timeout)

            return True

        except Exception as e:
            print(f"[错误] 启动失败: {e}")
            return False

    def wait_for_startup(self, timeout: int = 120) -> bool:
        """
        等待ComfyUI启动完成

        Args:
            timeout: 超时时间(秒)

        Returns:
            bool - 是否启动成功
        """
        print(f"[信息] 等待ComfyUI启动 (超时: {timeout}秒)...")

        start_time = time.time()
        check_interval = 2

        while time.time() - start_time < timeout:
            if self.is_running():
                print(f"[信息] ComfyUI已启动!")
                return True

            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0:  # 每10秒打印一次
                print(f"[信息] 等待中... ({elapsed}/{timeout}秒)")

            time.sleep(check_interval)

        print(f"[错误] 启动超时 ({timeout}秒)")
        return False

    def stop(self) -> bool:
        """
        停止ComfyUI

        Returns:
            bool - 是否停止成功
        """
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                print("[信息] ComfyUI已停止")
                return True
            except:
                self.process.kill()
                return False

        return True

    def ensure_running(self) -> bool:
        """
        确保ComfyUI正在运行，如果没有则自动启动

        Returns:
            bool - 是否运行中
        """
        if self.is_running():
            print("[信息] ComfyUI已在运行")
            return True

        return self.start(wait=True)


def test_launcher():
    """测试启动器"""
    launcher = ComfyUILauncher()

    # 检查路径
    from config import validate_paths

    valid, errors = validate_paths()

    if not valid:
        print("[错误] 路径验证失败:")
        for error in errors:
            print(f"  - {error}")
        return

    # 检测状态
    if launcher.is_running():
        print("[信息] ComfyUI已在运行")
    else:
        print("[信息] ComfyUI未运行，正在启动...")
        if launcher.start(wait=True):
            print("[成功] ComfyUI启动成功!")
        else:
            print("[失败] ComfyUI启动失败")


if __name__ == "__main__":
    test_launcher()
