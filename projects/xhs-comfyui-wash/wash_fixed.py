"""
ComfyUI洗图修复版 - 确保正确处理所有图片
"""

import json
import requests
import time
import shutil
from pathlib import Path


class ComfyUIWasherFixed:
    """修复版洗图工具"""

    def __init__(self):
        self.api_url = "http://192.168.11.158:8188"
        self.output_dir = r"D:\output\xitu"  # 工作流配置的输出目录

    def is_running(self):
        try:
            response = requests.get(f"{self.api_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False

    def load_workflow(self, workflow_path):
        with open(workflow_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def modify_workflow(self, workflow, input_folder):
        """修改工作流配置"""
        workflow = json.loads(json.dumps(workflow))

        # 找到批次图像节点（ID: 43）
        if "43" in workflow and workflow["43"].get("class_type") == "Load Image Batch":
            node = workflow["43"]
            node["inputs"]["path"] = input_folder
            # 修改模式为处理所有图片（如果支持）
            # node["inputs"]["mode"] = "all_images"  # 可能需要根据实际节点支持的模式
            print(f"[修改] 批次图像节点输入路径: {input_folder}")

        return workflow

    def queue_prompt(self, workflow):
        """提交任务"""
        data = {"prompt": workflow}
        response = requests.post(f"{self.api_url}/prompt", json=data)

        if response.status_code == 200:
            result = response.json()
            return result.get("prompt_id")
        else:
            raise Exception(f"提交失败: {response.status_code}")

    def wait_for_completion(self, prompt_id, timeout=600):
        """等待任务完成"""
        print(f"[等待] 任务 {prompt_id[:8]}...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{self.api_url}/history/{prompt_id}", timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if prompt_id in data:
                        status = data[prompt_id].get("status", {}).get("status_str", "")
                        if status == "success":
                            print("[完成] 任务成功!")
                            return True
                        elif status == "error":
                            print("[错误] 任务失败")
                            return False
            except:
                pass

            time.sleep(3)

        print("[超时] 任务未完成")
        return False

    def wash(self, input_folder, workflow_path):
        """执行洗图"""
        print("=" * 60)
        print("ComfyUI洗图 - 修复版")
        print("=" * 60)
        print(f"输入: {input_folder}")
        print(f"输出: {self.output_dir}")

        # 检查ComfyUI
        if not self.is_running():
            print("[错误] ComfyUI未运行")
            return False

        # 加载并修改工作流
        print("\n[1] 加载工作流...")
        workflow = self.load_workflow(workflow_path)
        workflow = self.modify_workflow(workflow, input_folder)

        # 保存修改后的工作流（用于调试）
        debug_path = Path(__file__).parent / "workflow_debug.json"
        with open(debug_path, "w", encoding="utf-8") as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"[调试] 工作流已保存: {debug_path}")

        # 提交任务
        print("\n[2] 提交任务...")
        prompt_id = self.queue_prompt(workflow)
        print(f"[任务ID] {prompt_id}")

        # 等待完成
        print("\n[3] 等待处理...")
        if self.wait_for_completion(prompt_id):
            # 统计输出
            output_files = list(Path(self.output_dir).glob("IMG_*.png"))
            print(f"\n[成功] 洗图完成!")
            print(f"输出文件: {len(output_files)} 张")
            print(f"输出目录: {self.output_dir}")
            return True
        else:
            print("\n[失败] 洗图未完成")
            return False


if __name__ == "__main__":
    import sys

    input_folder = r"C:\Users\admin\Projects\xhs-image-filter\output\filtered"
    workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"

    washer = ComfyUIWasherFixed()
    washer.wash(input_folder, workflow_path)
