"""
ComfyUI洗图自动化工具 - 循环单张模式
有多少张图片就运行多少次，每次处理一张
"""

import json
import requests
import time
import shutil
from pathlib import Path
from typing import List


class ComfyUIWasherLoop:
    """ComfyUI洗图工具 - 循环单张模式"""

    def __init__(self):
        self.api_url = "http://192.168.11.158:8188"
        self.output_dir = Path(r"D:\output\xitu")
        self.output_dir.mkdir(parents=True, exist_ok=True)

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

    def modify_workflow_for_single_image(
        self,
        workflow: dict,
        image_path: str,
        lora_name: str = None,
        lora_strength: float = 0.8,
    ) -> dict:
        """
        修改工作流，设置为单张图片模式，并可指定LoRA

        Args:
            workflow: 工作流字典
            image_path: 图片路径
            lora_name: LoRA文件名（可选）
            lora_strength: LoRA强度（可选）
        """
        workflow = json.loads(json.dumps(workflow))  # 深拷贝

        # 找到批次图像节点（ID: 43）
        if "43" in workflow and workflow["43"].get("class_type") == "Load Image Batch":
            node = workflow["43"]
            # 设置文件夹路径
            folder = Path(image_path).parent
            node["inputs"]["path"] = str(folder)
            # 设置模式为单张模式（通过index控制）
            # 获取当前图片在文件夹中的索引
            all_images = sorted(folder.glob("*.png")) + sorted(folder.glob("*.jpg"))
            try:
                index = all_images.index(Path(image_path))
                node["inputs"]["index"] = index
                node["inputs"]["mode"] = "single_image"  # 如果支持的话
            except ValueError:
                pass

            print(
                f"  [设置] 处理第 {index + 1}/{len(all_images)} 张: {Path(image_path).name}"
            )

        # 如果指定了LoRA，修改LoRA节点
        if lora_name:
            for node_id, node in workflow.items():
                if isinstance(node, dict):
                    class_type = node.get("class_type", "")
                    if "Lora" in class_type or class_type == "LoraLoaderModelOnly":
                        old_lora = node.get("inputs", {}).get("lora_name", "")
                        node["inputs"]["lora_name"] = lora_name
                        node["inputs"]["strength_model"] = lora_strength
                        print(
                            f"  [LoRA] {old_lora} -> {lora_name} (强度: {lora_strength})"
                        )
                        break

        return workflow

    def queue_prompt(self, workflow: dict) -> str:
        """提交任务到ComfyUI队列"""
        data = {"prompt": workflow}
        response = requests.post(f"{self.api_url}/prompt", json=data)

        if response.status_code == 200:
            result = response.json()
            return result.get("prompt_id")
        else:
            raise Exception(f"提交任务失败: {response.status_code} - {response.text}")

    def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> bool:
        """等待任务完成"""
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
                            return True
                        elif status == "error":
                            return False
            except:
                pass

            time.sleep(2)

        return False

    def get_output_files(self, before_files: set) -> List[Path]:
        """获取新产生的输出文件"""
        current_files = set(self.output_dir.glob("IMG_*.png"))
        new_files = current_files - before_files
        return sorted(new_files, key=lambda x: x.stat().st_mtime, reverse=True)

    def wash_single(
        self, image_path: str, workflow: dict, index: int, total: int,
        lora_name: str = None, lora_strength: float = 0.8
    ) -> bool:
        """
        单张图片洗图

        Args:
            image_path: 图片路径
            workflow: 工作流模板
            index: 当前索引
            total: 总数
            lora_name: LoRA文件名（可选）
            lora_strength: LoRA强度（可选）

        Returns:
            bool: 是否成功
        """
        image_name = Path(image_path).name
        print(f"\n[{index}/{total}] 处理: {image_name}")

        try:
            # 记录当前输出文件
            before_files = set(self.output_dir.glob("IMG_*.png"))

            # 修改工作流（支持指定LoRA）
            modified_workflow = self.modify_workflow_for_single_image(
                workflow, image_path, lora_name, lora_strength
            )

            # 提交任务
            prompt_id = self.queue_prompt(modified_workflow)
            print(f"  [提交] 任务ID: {prompt_id[:8]}...")

            # 等待完成
            if self.wait_for_completion(prompt_id):
                # 查找新产生的文件
                new_files = self.get_output_files(before_files)
                if new_files:
                    # 重命名为原文件名相关
                    new_file = new_files[0]
                    target_name = f"{Path(image_path).stem}_washed.png"
                    target_path = self.output_dir / target_name
                    shutil.copy2(new_file, target_path)
                    print(f"  [完成] 输出: {target_name}")
                    return True
                else:
                    print(f"  [警告] 未找到输出文件")
                    return False
            else:
                print(f"  [失败] 处理超时或出错")
                return False

        except Exception as e:
            print(f"  [错误] {e}")
            return False
            else:
                print(f"  [失败] 处理超时或出错")
                return False

        except Exception as e:
            print(f"  [错误] {e}")
            return False

    def wash_batch(self, input_folder: str, workflow_path: str) -> dict:
        """
        批量洗图 - 循环单张模式

        Args:
            input_folder: 输入图片文件夹
            workflow_path: 工作流JSON路径

        Returns:
            统计信息
        """
        input_path = Path(input_folder)

        # 查找所有图片
        images = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
            images.extend(input_path.glob(ext))
            images.extend(input_path.glob(ext.upper()))

        images = sorted(set(images))
        total = len(images)

        print("=" * 60)
        print("ComfyUI批量洗图 - 循环单张模式")
        print("=" * 60)
        print(f"输入目录: {input_folder}")
        print(f"图片数量: {total}")
        print(f"输出目录: {self.output_dir}")
        print(f"工作流: {workflow_path}")
        print("=" * 60)

        if total == 0:
            print("\n[错误] 文件夹中没有图片")
            return {"total": 0, "success": 0, "failed": 0}

        # 检查ComfyUI是否运行
        if not self.is_running():
            print("\n[错误] ComfyUI未运行")
            return {"total": total, "success": 0, "failed": total}

        # 加载工作流
        print("\n[加载] 工作流...")
        workflow = self.load_workflow(workflow_path)

        # 循环处理每张图片
        success_count = 0
        failed_count = 0

        for i, image_path in enumerate(images, 1):
            if self.wash_single(str(image_path), workflow, i, total):
                success_count += 1
            else:
                failed_count += 1

            # 间隔5秒，避免GPU过载
            if i < total:
                time.sleep(5)

        # 统计
        print(f"\n{'=' * 60}")
        print("处理完成")
        print(f"{'=' * 60}")
        print(f"总计: {total}")
        print(f"成功: {success_count}")
        print(f"失败: {failed_count}")
        print(f"输出: {self.output_dir}")

        return {"total": total, "success": success_count, "failed": failed_count}


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("ComfyUI批量洗图 - 循环单张模式")
        print("=" * 60)
        print("用法: python wash_loop.py <输入文件夹>")
        print("示例: python wash_loop.py ./filtered")
        print("\n说明:")
        print("  每张图片单独提交一次任务")
        print("  有多少张图片就运行多少次")
        sys.exit(1)

    input_folder = sys.argv[1]

    workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"

    washer = ComfyUIWasherLoop()
    result = washer.wash_batch(input_folder, workflow_path)

    if result["success"] > 0:
        print(f"\n[成功] 洗图完成！")
    else:
        print(f"\n[失败] 没有成功处理的图片")


if __name__ == "__main__":
    main()
