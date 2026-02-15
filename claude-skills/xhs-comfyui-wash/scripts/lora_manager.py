"""
ComfyUI洗图工具 - LoRA模型管理
功能：动态更换LoRA模型
"""

import json
from pathlib import Path


class LoRAManager:
    """LoRA模型管理器"""

    def __init__(self):
        self.lora_dir = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\models\loras"
        self.workflow_path = r"D:\ComfyUI-aki-v1.6-XZG torch2.7 cuda12.6 Nunchaku0.3.1\ComfyUI\user\default\workflows\z洗图1222api.json"

    def list_available_loras(self) -> list:
        """列出所有可用的LoRA模型"""
        lora_path = Path(self.lora_dir)
        loras = []

        if lora_path.exists():
            for file in lora_path.glob("*.safetensors"):
                loras.append(file.name)

        return sorted(loras)

    def get_current_lora(self) -> str:
        """获取当前工作流使用的LoRA"""
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)

        # 查找LoRA加载器节点
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "")
                if "Lora" in class_type or class_type == "LoraLoaderModelOnly":
                    lora_name = node.get("inputs", {}).get("lora_name", "")
                    strength = node.get("inputs", {}).get("strength_model", 0.8)
                    return f"{lora_name} (强度: {strength})"

        return "未找到LoRA节点"

    def change_lora(self, new_lora_name: str, strength: float = 0.8) -> bool:
        """
        更换LoRA模型

        Args:
            new_lora_name: 新的LoRA文件名（如: xiaolian2_000008250.safetensors）
            strength: LoRA强度 (0-1)

        Returns:
            bool: 是否成功
        """
        # 检查是否为别名
        try:
            config_path = Path(__file__).parent.parent / "config" / "lora_aliases.json"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    aliases = json.load(f)
                    if new_lora_name in aliases:
                        print(
                            f"[提示] 使用别名: {new_lora_name} -> {aliases[new_lora_name]}"
                        )
                        new_lora_name = aliases[new_lora_name]
        except Exception as e:
            print(f"[警告] 加载LoRA别名失败: {e}")

        # 检查LoRA文件是否存在
        lora_file = Path(self.lora_dir) / new_lora_name
        if not lora_file.exists():
            print(f"[错误] LoRA文件不存在: {new_lora_name}")
            return False

        # 加载工作流
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)

        # 查找并修改LoRA节点
        modified = False
        for node_id, node in workflow.items():
            if isinstance(node, dict):
                class_type = node.get("class_type", "")
                if "Lora" in class_type or class_type == "LoraLoaderModelOnly":
                    old_lora = node.get("inputs", {}).get("lora_name", "")
                    node["inputs"]["lora_name"] = new_lora_name
                    node["inputs"]["strength_model"] = strength
                    modified = True
                    print(f"[修改] 节点 {node_id}")
                    print(f"  原LoRA: {old_lora}")
                    print(f"  新LoRA: {new_lora_name}")
                    print(f"  强度: {strength}")

        if not modified:
            print("[错误] 未找到LoRA节点")
            return False

        # 保存工作流
        with open(self.workflow_path, "w", encoding="utf-8") as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)

        print(f"[成功] 工作流已更新: {self.workflow_path}")
        return True


def main():
    """主函数"""
    import sys

    manager = LoRAManager()

    print("=" * 60)
    print("ComfyUI LoRA模型管理")
    print("=" * 60)

    # 显示当前LoRA
    print(f"\n当前LoRA: {manager.get_current_lora()}")

    # 列出可用LoRA
    print("\n可用LoRA模型:")
    loras = manager.list_available_loras()
    for i, lora in enumerate(loras, 1):
        marker = " *" if "xiaolian" in lora.lower() else ""
        print(f"  {i}. {lora}{marker}")

    print("\n" + "=" * 60)

    # 如果有参数，执行更换
    if len(sys.argv) >= 2:
        new_lora = sys.argv[1]
        strength = float(sys.argv[2]) if len(sys.argv) > 2 else 0.8

        print(f"\n更换LoRA: {new_lora}")
        print(f"强度: {strength}")
        print()

        if manager.change_lora(new_lora, strength):
            print("\n[成功] LoRA更换完成！")
            print("下次执行洗图时将使用新的LoRA模型")
        else:
            print("\n[失败] LoRA更换失败")
    else:
        print("\n使用方法:")
        print("  python lora_manager.py <LoRA文件名> [强度]")
        print("\n示例:")
        print('  python lora_manager.py "xiaolian2_000008250.safetensors" 0.8')


if __name__ == "__main__":
    main()
