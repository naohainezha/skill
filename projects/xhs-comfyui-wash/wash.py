"""
ComfyUI洗图自动化工具 - 主程序 (批次模式)
功能：将输入文件夹路径设置到工作流的批次图像节点，ComfyUI自动处理所有图片
"""

import json
import requests
import time
import shutil
from pathlib import Path
from typing import List, Dict, Optional


class ComfyUIWasher:
    """ComfyUI洗图工具 - 批次模式"""

    def __init__(self):
        self.api_url = "http://192.168.11.158:8188"
        self.comfyui_dir = (
            r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI"
        )
        self.output_dir = Path(self.comfyui_dir) / "output"

    def is_running(self) -> bool:
        """检测ComfyUI是否运行"""
        try:
            response = requests.get(f"{self.api_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False

    def load_workflow(self, workflow_path: str) -> dict:
        """加载工作流JSON"""
        with open(workflow_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def modify_workflow_for_folder(self, workflow: dict, folder_path: str) -> dict:
        """
        修改工作流，设置输入文件夹路径
        根据z洗图1222api.json结构，批次图像节点ID是43
        """
        workflow = json.loads(json.dumps(workflow))  # 深拷贝

        # 查找批次图像节点 (Load Image Batch)
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "")
                if class_type == "Load Image Batch":
                    if "inputs" in node:
                        node["inputs"]["path"] = folder_path
                        print(f"  [设置输入] 批次图像节点 {node_id}")
                        print(f"  [文件夹] {folder_path}")
                        return workflow

        # 如果没找到批次节点，尝试查找普通LoadImage节点
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "")
                if class_type == "LoadImage":
                    if "inputs" in node:
                        # 如果是文件夹，取第一张图片
                        folder = Path(folder_path)
                        images = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
                        if images:
                            node["inputs"]["image"] = str(images[0])
                            print(
                                f"  [设置输入] LoadImage节点 {node_id}: {images[0].name}"
                            )
                            return workflow

        print("  [警告] 未找到图像输入节点")
        return workflow

    def queue_prompt(self, workflow: dict) -> str:
        """
        提交任务到ComfyUI队列

        Returns:
            prompt_id: 任务ID
        """
        data = {"prompt": workflow}
        response = requests.post(f"{self.api_url}/prompt", json=data)

        if response.status_code == 200:
            result = response.json()
            return result.get("prompt_id")
        else:
            raise Exception(f"提交任务失败: {response.status_code} - {response.text}")

    def get_history(self, prompt_id: str) -> Optional[dict]:
        """获取任务历史记录"""
        try:
            response = requests.get(f"{self.api_url}/history/{prompt_id}")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> bool:
        """
        等待任务完成

        Args:
            prompt_id: 任务ID
            timeout: 超时时间(秒)

        Returns:
            bool: 是否成功完成
        """
        print(f"  [等待] 任务 {prompt_id[:8]}...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)

            if history and prompt_id in history:
                prompt_data = history[prompt_id]
                status = prompt_data.get("status", {})
                status_str = status.get("status_str", "")

                if status_str == "success":
                    print(f"  [完成] 任务成功!")
                    return True
                elif status_str == "error":
                    print(f"  [错误] 任务执行失败")
                    return False

            time.sleep(2)

        print(f"  [超时] 任务未完成")
        return False

    def count_images_in_folder(self, folder_path: str) -> int:
        """统计文件夹中的图片数量"""
        folder = Path(folder_path)
        count = 0
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
            count += len(list(folder.glob(ext)))
            count += len(list(folder.glob(ext.upper())))
        return count

    def wash_folder(self, input_folder: str, workflow_path: str) -> dict:
        """
        批量洗图 - 批次模式
        将整个文件夹提交给ComfyUI，由工作流自动处理所有图片

        Args:
            input_folder: 输入图片文件夹
            workflow_path: 工作流JSON路径

        Returns:
            统计信息
        """
        input_path = Path(input_folder)

        # 统计图片数量
        image_count = self.count_images_in_folder(input_folder)

        print(f"=" * 60)
        print(f"ComfyUI批量洗图 - 批次模式")
        print(f"=" * 60)
        print(f"输入文件夹: {input_folder}")
        print(f"图片数量: {image_count}")
        print(f"工作流: {workflow_path}")
        print(f"=" * 60)

        if image_count == 0:
            print("\n[错误] 文件夹中没有图片")
            return {"total": 0, "success": 0, "failed": 0}

        # 检查ComfyUI是否运行
        if not self.is_running():
            print("\n[错误] ComfyUI未运行，请先启动ComfyUI")
            return {"total": image_count, "success": 0, "failed": image_count}

        try:
            # 1. 加载工作流
            print("\n[1] 加载工作流...")
            workflow = self.load_workflow(workflow_path)

            # 2. 修改工作流输入（设置文件夹路径）
            print("[2] 设置输入文件夹...")
            workflow = self.modify_workflow_for_folder(workflow, input_folder)

            # 3. 提交任务
            print("[3] 提交任务...")
            prompt_id = self.queue_prompt(workflow)
            print(f"  [任务ID] {prompt_id}")

            # 4. 等待完成
            print(f"[4] 等待处理完成（约 {image_count * 10} 秒）...")
            if self.wait_for_completion(prompt_id, timeout=image_count * 60):
                print(f"\n[成功] 洗图完成！")
                print(f"  输出目录: {self.output_dir}")
                print(f"  图片数量: {image_count}")
                return {"total": image_count, "success": image_count, "failed": 0}
            else:
                print(f"\n[失败] 洗图未完成")
                return {"total": image_count, "success": 0, "failed": image_count}

        except Exception as e:
            print(f"\n[错误] {e}")
            import traceback

            traceback.print_exc()
            return {"total": image_count, "success": 0, "failed": image_count}


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("ComfyUI批量洗图工具 - 批次模式")
        print("=" * 60)
        print("用法: python wash.py <输入文件夹>")
        print("示例: python wash.py ./filtered")
        print("\n说明:")
        print("  将整个文件夹提交给ComfyUI批次图像节点")
        print("  ComfyUI自动处理文件夹内所有图片")
        sys.exit(1)

    input_folder = sys.argv[1]

    workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"

    washer = ComfyUIWasher()
    result = washer.wash_folder(input_folder, workflow_path)

    print(f"\n{'=' * 60}")
    print(f"处理结果")
    print(f"{'=' * 60}")
    print(f"总计: {result['total']}")
    print(f"成功: {result['success']}")
    print(f"失败: {result['failed']}")


if __name__ == "__main__":
    main()
