"""
ComfyUI洗图工具 - 使用正确的目录路径
"""

import json
import requests
import time
import shutil
from pathlib import Path


class ComfyUIWasher:
    def __init__(self):
        self.api_url = "http://192.168.11.158:8188"
        # 使用正确的路径
        self.filtered_dir = Path(
            r"C:\Users\admin\Projects\xhs-image-filter\output\new_batch\filtered"
        )
        self.processed_dir = Path(
            r"C:\Users\admin\Projects\xhs-image-filter\output\new_batch\processed"
        )
        self.comfyui_output = Path(
            r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\output"
        )

        # 确保 processed 目录存在
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def is_running(self):
        try:
            r = requests.get(f"{self.api_url}/system_stats", timeout=5)
            return r.status_code == 200
        except:
            return False

    def load_workflow(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def modify_workflow(self, workflow, image_path, lora_name=None, lora_strength=0.8):
        workflow = json.loads(json.dumps(workflow))

        # 修改图像节点 - 使用批量加载模式
        if "43" in workflow:
            node = workflow["43"]
            if node.get("class_type") == "Load Image Batch":
                folder = image_path.parent
                node["inputs"]["path"] = str(folder)
                all_images = sorted(folder.glob("*.png")) + sorted(folder.glob("*.jpg"))
                try:
                    idx = all_images.index(image_path)
                    node["inputs"]["index"] = idx
                    print(f"  [加载图片] {image_path.name} (索引: {idx})")
                except ValueError:
                    print(f"  [警告] 无法找到图片索引: {image_path.name}")

        # 修改LoRA节点
        if lora_name and "44" in workflow:
            node = workflow["44"]
            if "Lora" in node.get("class_type", ""):
                node["inputs"]["lora_name"] = lora_name
                node["inputs"]["strength_model"] = lora_strength
                print(f"  [LoRA] {lora_name} (强度: {lora_strength})")

        return workflow

    def submit_task(self, workflow):
        r = requests.post(f"{self.api_url}/prompt", json={"prompt": workflow})
        if r.status_code == 200:
            return r.json().get("prompt_id")
        raise Exception(f"提交失败: {r.status_code}")

    def wait_complete(self, prompt_id, timeout=300):
        start = time.time()
        while time.time() - start < timeout:
            try:
                r = requests.get(f"{self.api_url}/history/{prompt_id}", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    if prompt_id in data:
                        status = data[prompt_id].get("status", {}).get("status_str", "")
                        if status == "success":
                            return True, self.get_output_files(prompt_id)
                        elif status == "error":
                            return False, []
            except:
                pass
            time.sleep(2)
        return False, []

    def get_output_files(self, prompt_id):
        """获取输出文件路径"""
        try:
            r = requests.get(f"{self.api_url}/history/{prompt_id}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if prompt_id in data:
                    outputs = data[prompt_id].get("outputs", {})
                    if outputs:
                        for node_id, node_data in outputs.items():
                            if "images" in node_data:
                                output_files = []
                                for img_info in node_data["images"]:
                                    filename = img_info.get("filename", "")
                                    if filename:
                                        src_path = self.comfyui_output / filename
                                        if src_path.exists():
                                            output_files.append(src_path)
                                return output_files
        except:
            pass
        return []

    def wash_and_move(self, image_path, workflow, lora_name=None, lora_strength=0.8):
        """洗图并移动到 processed 目录"""
        print(f"\n[{image_path.name}]")
        try:
            # 修改工作流
            modified = self.modify_workflow(
                workflow, image_path, lora_name, lora_strength
            )

            # 提交任务
            prompt_id = self.submit_task(modified)
            print(f"  任务ID: {prompt_id[:8]}...")

            # 等待完成
            success, output_files = self.wait_complete(prompt_id)

            if success and output_files:
                # 复制到 processed 目录
                moved_count = 0
                for src_file in output_files:
                    dest_file = self.processed_dir / f"{image_path.stem}_washed.png"
                    shutil.copy2(src_file, dest_file)
                    print(f"  已保存: {dest_file.name}")
                    moved_count += 1

                # 删除原文件
                image_path.unlink()
                print(f"  原文件已移除")

                return True
            else:
                print(f"  处理失败")
                return False

        except Exception as e:
            print(f"  失败: {e}")
            time.sleep(2)
            return False

    def wash_batch(self, lora_name=None, lora_strength=0.8):
        """批量处理 filtered 中的所有图片"""
        # 获取所有 filtered 图片
        images = list(self.filtered_dir.glob("*.png")) + list(
            self.filtered_dir.glob("*.jpg")
        )
        images = sorted(set(images))

        if not images:
            print("[信息] filtered 目录为空")
            return

        total = len(images)

        print("=" * 60)
        print("ComfyUI洗图 - 筛选素材工作流")
        print("=" * 60)
        print(f"输入目录: {self.filtered_dir}")
        print(f"输出目录: {self.processed_dir}")
        print(f"待处理图片: {total} 张")
        if lora_name:
            print(f"LoRA: {lora_name} (强度: {lora_strength})")
        print("=" * 60)

        # 检查 ComfyUI
        if not self.is_running():
            print("\n[错误] ComfyUI 未运行")
            print("请先运行: python start_comfyui.py")
            return

        # 加载工作流
        workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"
        workflow = self.load_workflow(workflow_path)

        # 处理每张图片
        success_count = 0
        failed_count = 0

        for i, img in enumerate(images, 1):
            print(f"\n[{i}/{total}] {img.name}")

            if self.wash_and_move(img, workflow, lora_name, lora_strength):
                success_count += 1
            else:
                failed_count += 1

            # 队列间隔
            if i < total:
                time.sleep(5)

        print(f"\n{'=' * 60}")
        print(f"处理完成!")
        print(f"  成功: {success_count} 张")
        print(f"  失败: {failed_count} 张")
        print(f"  已保存到: {self.processed_dir}")
        print(f"  filtered 目录已清空")
        print(f"{'=' * 60}")


def main():
    import sys

    washer = ComfyUIWasher()

    # 默认使用小脸 LoRA
    lora_name = "xiaolian1214_000005250.safetensors"
    lora_strength = 0.8

    if len(sys.argv) > 1:
        lora_name = sys.argv[1]
    if len(sys.argv) > 2:
        lora_strength = float(sys.argv[2])

    # 执行批量洗图
    washer.wash_batch(lora_name, lora_strength)


if __name__ == "__main__":
    main()
