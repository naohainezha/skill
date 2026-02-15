"""
小红书素材整理自动化工具 - 图片合并模块
功能：将多个文件夹的图片合并到一个统一目录，自动去重
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Set, Tuple
from PIL import Image
import io

from config import get_config, DEFAULT_CONFIG


class ImageMerger:
    """图片合并器"""

    def __init__(self):
        self.config = get_config()
        self.supported_extensions = tuple(self.config["image_extensions"])
        self.seen_hashes: Set[str] = set()
        self.stats = {
            "total_found": 0,
            "duplicates_skipped": 0,
            "merged": 0,
            "errors": 0,
        }

    def calculate_hash(self, image_path: Path) -> str:
        """
        计算图片的感知哈希（用于去重）
        使用 dHash (差异哈希) - 对轻微变化鲁棒

        Args:
            image_path: 图片路径

        Returns:
            哈希字符串
        """
        try:
            with Image.open(image_path) as img:
                # 转换为灰度图并缩小
                img = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)

                pixels = list(img.getdata())

                # 计算差异哈希
                diff = []
                for row in range(8):
                    for col in range(8):
                        left_pixel = pixels[row * 9 + col]
                        right_pixel = pixels[row * 9 + col + 1]
                        diff.append(left_pixel > right_pixel)

                # 转换为十六进制
                decimal_value = sum(bit << i for i, bit in enumerate(diff))
                return f"{decimal_value:016x}"
        except Exception as e:
            # 如果无法计算感知哈希，回退到MD5
            try:
                with open(image_path, "rb") as f:
                    return hashlib.md5(f.read()).hexdigest()
            except Exception:
                return None

    def find_images(self, folders: List[Path]) -> List[Path]:
        """
        从多个文件夹中查找所有图片

        Args:
            folders: 文件夹路径列表

        Returns:
            图片路径列表
        """
        images = []
        for folder in folders:
            if not folder.exists():
                print(f"⚠️  文件夹不存在: {folder}")
                continue

            for ext in self.supported_extensions:
                images.extend(folder.rglob(f"*{ext}"))
                images.extend(folder.rglob(f"*{ext.upper()}"))

        return sorted(set(images))  # 去重并排序

    def merge(
        self,
        input_folders: List[str],
        output_folder: str,
        preserve_structure: bool = False,
        copy_mode: bool = True,
    ) -> Tuple[int, int, int]:
        """
        合并多个文件夹的图片

        Args:
            input_folders: 输入文件夹路径列表
            output_folder: 输出文件夹路径
            preserve_structure: 是否保留原始目录结构
            copy_mode: True=复制，False=移动

        Returns:
            (成功数量, 跳过数量, 错误数量)
        """
        input_paths = [Path(f).resolve() for f in input_folders]
        output_path = Path(output_folder).resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        # 查找所有图片
        images = self.find_images(input_paths)
        self.stats["total_found"] = len(images)

        print(f"[INFO] 找到 {len(images)} 张图片")

        for i, img_path in enumerate(images, 1):
            try:
                # 计算哈希去重
                if self.config["processing"]["skip_duplicates"]:
                    img_hash = self.calculate_hash(img_path)
                    if img_hash and img_hash in self.seen_hashes:
                        self.stats["duplicates_skipped"] += 1
                        continue
                    if img_hash:
                        self.seen_hashes.add(img_hash)

                # 确定目标路径
                if preserve_structure:
                    # 保留原始目录结构
                    rel_path = self._get_relative_path(img_path, input_paths)
                    dest_path = output_path / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # 扁平化存储
                    dest_path = output_path / img_path.name

                    # 处理重名
                    dest_path = self._get_unique_path(dest_path)

                # 复制或移动
                if copy_mode:
                    shutil.copy2(img_path, dest_path)
                else:
                    shutil.move(str(img_path), str(dest_path))

                self.stats["merged"] += 1

                if i % 50 == 0:
                    print(f"  已处理 {i}/{len(images)}...")

            except Exception as e:
                print(f"❌ 处理失败 {img_path}: {e}")
                self.stats["errors"] += 1

        return (
            self.stats["merged"],
            self.stats["duplicates_skipped"],
            self.stats["errors"],
        )

    def _get_relative_path(self, img_path: Path, input_paths: List[Path]) -> Path:
        """
        获取图片相对于输入文件夹的相对路径

        Args:
            img_path: 图片路径
            input_paths: 输入文件夹列表

        Returns:
            相对路径
        """
        for input_path in input_paths:
            try:
                return img_path.relative_to(input_path)
            except ValueError:
                continue
        return img_path.name

    def _get_unique_path(self, path: Path) -> Path:
        """
        如果文件已存在，生成唯一路径

        Args:
            path: 原始路径

        Returns:
            唯一路径
        """
        if not path.exists():
            return path

        stem = path.stem
        suffix = path.suffix
        counter = 1

        while True:
            new_path = path.parent / f"{stem}_{counter:03d}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    def get_stats(self) -> dict:
        """获取统计信息"""
        return self.stats.copy()


def merge_folders(
    input_folders: List[str],
    output_folder: str = None,
    preserve_structure: bool = False,
    copy_mode: bool = True,
) -> dict:
    """
    合并文件夹的便捷函数

    Args:
        input_folders: 输入文件夹列表
        output_folder: 输出文件夹（默认使用配置中的路径）
        preserve_structure: 是否保留目录结构
        copy_mode: 复制模式

    Returns:
        统计信息字典
    """
    config = get_config()
    if output_folder is None:
        output_folder = config["output_dir"]

    merger = ImageMerger()
    success, skipped, errors = merger.merge(
        input_folders=input_folders,
        output_folder=output_folder,
        preserve_structure=preserve_structure,
        copy_mode=copy_mode,
    )

    return {
        "success": success,
        "skipped": skipped,
        "errors": errors,
        "total": success + skipped + errors,
    }


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) < 3:
        print(
            "用法: python merge.py <输入文件夹1> <输入文件夹2> ... --output <输出文件夹>"
        )
        sys.exit(1)

    # 简单解析参数
    input_dirs = []
    output_dir = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--output":
            output_dir = sys.argv[i + 1]
            i += 2
        else:
            input_dirs.append(sys.argv[i])
            i += 1

    if not input_dirs:
        print("请指定输入文件夹")
        sys.exit(1)

    if not output_dir:
        output_dir = str(Path(input_dirs[0]).parent / "merged")

    result = merge_folders(input_dirs, output_dir)
    print(f"\n✅ 合并完成！")
    print(f"   成功: {result['success']}")
    print(f"   跳过: {result['skipped']}")
    print(f"   错误: {result['errors']}")
