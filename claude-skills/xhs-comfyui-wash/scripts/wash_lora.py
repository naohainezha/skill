"""
ComfyUI洗图工具 - 支持指定LoRA模型
"""

import json
import requests
import time
from pathlib import Path


class ComfyUIWasher:
    def __init__(self):
        self.api_url = "http://192.168.11.158:8188"
        self.output_dir = Path(r"D:\output\xitu")

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

        # 修改图像节点
        if "43" in workflow:
            node = workflow["43"]
            if node.get("class_type") == "Load Image Batch":
                folder = Path(image_path).parent
                node["inputs"]["path"] = str(folder)
                all_images = sorted(folder.glob("*.png")) + sorted(folder.glob("*.jpg"))
                try:
                    idx = all_images.index(Path(image_path))
                    node["inputs"]["index"] = idx
                except:
                    pass

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
                            return True
                        elif status == "error":
                            return False
            except:
                pass
            time.sleep(2)
        return False

    def wash_image(
        self, image_path, workflow, index, total, lora_name=None, lora_strength=0.8
    ):
        print(f"\n[{index}/{total}] {Path(image_path).name}")
        try:
            modified = self.modify_workflow(
                workflow, image_path, lora_name, lora_strength
            )
            prompt_id = self.submit_task(modified)
            print(f"  任务: {prompt_id[:8]}...")
            if self.wait_complete(prompt_id):
                print("  完成!")
                return True
            else:
                print("  失败!")
                return False
        except Exception as e:
            print(f"  错误: {e}")
            return False

    def wash_batch(
        self, input_folder, workflow_path, lora_name=None, lora_strength=0.8
    ):
        input_path = Path(input_folder)
        images = []
        for ext in ["*.png", "*.jpg"]:
            images.extend(input_path.glob(ext))
        images = sorted(set(images))
        total = len(images)

        print("=" * 60)
        print("ComfyUI洗图 - 循环单张模式")
        print("=" * 60)
        print(f"输入: {input_folder}")
        print(f"图片: {total}张")
        if lora_name:
            print(f"LoRA: {lora_name} (强度{lora_strength})")
        print("=" * 60)

        if not self.is_running():
            print("\n[错误] ComfyUI未运行")
            return

        workflow = self.load_workflow(workflow_path)
        success = failed = 0

        for i, img in enumerate(images, 1):
            if self.wash_image(str(img), workflow, i, total, lora_name, lora_strength):
                success += 1
            else:
                failed += 1
            if i < total:
                time.sleep(5)

        print(f"\n{'=' * 60}")
        print(f"完成! 成功:{success} 失败:{failed}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python wash_lora.py <输入文件夹> [LoRA名] [强度]")
        print("\n示例:")
        print("  python wash_lora.py ./filtered")
        print('  python wash_lora.py ./filtered "xiaolian2_000008250.safetensors" 0.8')
        print('  python wash_lora.py ./filtered "Z_kuanlian_000000540.safetensors" 0.8')
        sys.exit(1)

    input_folder = sys.argv[1]
    lora_name = sys.argv[2] if len(sys.argv) > 2 else None
    lora_strength = float(sys.argv[3]) if len(sys.argv) > 3 else 0.8

    # 加载LoRA别名配置
    try:
        config_path = Path(__file__).parent.parent / "config" / "lora_aliases.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                aliases = json.load(f)
                if lora_name in aliases:
                    print(f"使用别名: {lora_name} -> {aliases[lora_name]}")
                    lora_name = aliases[lora_name]
    except Exception as e:
        print(f"加载LoRA别名失败: {e}")

    workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"

    washer = ComfyUIWasher()
    washer.wash_batch(input_folder, workflow_path, lora_name, lora_strength)


if __name__ == "__main__":
    main()
