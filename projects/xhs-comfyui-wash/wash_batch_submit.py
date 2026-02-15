"""
ComfyUI洗图工具 - 只提交任务到队列，不等待
让ComfyUI自动依次处理所有图片
"""

import json
import requests
import time
from pathlib import Path


class ComfyUIWasher:
    def __init__(self):
        self.api_url = "http://192.168.11.158:8188"
        self.filtered_dir = Path(
            r"C:\Users\admin\Projects\xhs-image-filter\output\new_batch\filtered"
        )
        self.processed_dir = Path(
            r"C:\Users\admin\Projects\xhs-image-filter\output\new_batch\processed"
        )
        self.comfyui_output = Path(
            r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\output"
        )

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

    def modify_workflow(
        self, workflow, image_index, total_images, lora_name=None, lora_strength=0.8
    ):
        """修改工作流，设置图片索引"""
        workflow = json.loads(json.dumps(workflow))

        # 修改图像节点 - 设置索引
        if "43" in workflow:
            node = workflow["43"]
            if node.get("class_type") == "Load Image Batch":
                node["inputs"]["path"] = str(self.filtered_dir)
                node["inputs"]["index"] = image_index
                node["inputs"]["mode"] = "incremental_image"

        # 修改LoRA节点
        if lora_name and "44" in workflow:
            node = workflow["44"]
            if "Lora" in node.get("class_type", ""):
                node["inputs"]["lora_name"] = lora_name
                node["inputs"]["strength_model"] = lora_strength

        return workflow

    def submit_task(self, workflow):
        """提交任务到队列"""
        r = requests.post(f"{self.api_url}/prompt", json={"prompt": workflow})
        if r.status_code == 200:
            return r.json().get("prompt_id")
        raise Exception(f"提交失败: {r.status_code}")

    def submit_all_tasks(self, total_images, lora_name=None, lora_strength=0.8):
        """提交所有任务到队列"""
        workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"
        workflow = self.load_workflow(workflow_path)

        print("=" * 60)
        print("ComfyUI洗图 - 批量提交模式")
        print("=" * 60)
        print(f"待处理图片: {total_images} 张")
        print(f"LoRA: {lora_name} (强度: {lora_strength})")
        print("=" * 60)
        print("\n正在提交任务到队列...")

        submitted = 0
        failed = 0

        for i in range(total_images):
            try:
                modified = self.modify_workflow(
                    workflow, i, total_images, lora_name, lora_strength
                )
                prompt_id = self.submit_task(modified)
                submitted += 1
                print(f"  [{i + 1}/{total_images}] 已提交: {prompt_id[:8]}...")
                time.sleep(0.5)  # 短暂间隔避免过载
            except Exception as e:
                failed += 1
                print(f"  [{i + 1}/{total_images}] 提交失败: {e}")

        print(f"\n{'=' * 60}")
        print(f"提交完成!")
        print(f"  成功: {submitted} 个任务")
        print(f"  失败: {failed} 个任务")
        print(f"\nComfyUI正在自动处理队列...")
        print(f"处理完成后，结果将保存到: {self.comfyui_output}")
        print(f"{'=' * 60}")

        return submitted

    def wait_all_complete(self, expected_count, timeout=1800):
        """等待所有任务完成"""
        print(f"\n等待 {expected_count} 张图片处理完成...")
        print(f"超时时间: {timeout}秒\n")

        start_time = time.time()
        last_count = 0
        stable_count = 0

        while time.time() - start_time < timeout:
            try:
                # 检查队列
                r = requests.get(f"{self.api_url}/queue", timeout=5)
                if r.status_code == 200:
                    queue_data = r.json()
                    running = len(queue_data.get("queue_running", []))
                    pending = len(queue_data.get("queue_pending", []))

                    # 检查输出文件数
                    output_files = list(self.comfyui_output.glob("ComfyUI_*.png"))
                    current_count = len(output_files)

                    print(
                        f"\r  队列: 运行{running} | 等待{pending} | 已完成: {current_count}/{expected_count}",
                        end="",
                        flush=True,
                    )

                    # 如果队列为空且文件数稳定
                    if running == 0 and pending == 0:
                        if current_count == last_count:
                            stable_count += 1
                            if stable_count >= 3:  # 连续3次检查稳定
                                print(f"\n\n✅ 处理完成! 共生成 {current_count} 张图片")
                                return current_count
                        else:
                            stable_count = 0

                    last_count = current_count

            except Exception as e:
                pass

            time.sleep(5)

        print(f"\n\n⚠️  等待超时，但任务可能仍在处理中")
        output_files = list(self.comfyui_output.glob("ComfyUI_*.png"))
        return len(output_files)


def main():
    import sys

    washer = ComfyUIWasher()

    # 检查ComfyUI
    if not washer.is_running():
        print("[错误] ComfyUI 未运行")
        return

    # 获取图片数量
    images = list(washer.filtered_dir.glob("*.png")) + list(
        washer.filtered_dir.glob("*.jpg")
    )
    total = len(images)

    if total == 0:
        print("[错误] filtered 目录为空")
        return

    print(f"\n找到 {total} 张待处理图片\n")

    # 默认使用小脸 LoRA
    lora_name = "xiaolian1214_000005250.safetensors"
    lora_strength = 0.8

    if len(sys.argv) > 1:
        lora_name = sys.argv[1]
    if len(sys.argv) > 2:
        lora_strength = float(sys.argv[2])

    # 提交所有任务
    submitted = washer.submit_all_tasks(total, lora_name, lora_strength)

    if submitted > 0:
        # 等待完成
        completed = washer.wait_all_complete(submitted)

        # 复制结果到processed目录
        print(f"\n复制结果到 processed 目录...")
        output_files = sorted(
            washer.comfyui_output.glob("ComfyUI_*.png"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )
        copied = 0
        for i, src_file in enumerate(output_files[:submitted]):
            dest_file = washer.processed_dir / f"washed_{i + 1:03d}.png"
            shutil.copy2(src_file, dest_file)
            copied += 1

        print(f"✅ 已复制 {copied} 张图片到 processed 目录")


if __name__ == "__main__":
    import shutil

    main()
