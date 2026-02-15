"""
小红书素材整理自动化工具 - 人脸检测筛选模块 (OpenCV版本)
功能：检测图片中的人脸，根据占比筛选合格素材
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from PIL import Image


class FilterReason(Enum):
    """筛选原因"""

    PASSED = "passed"  # 通过
    NO_FACE = "no_face"  # 无人脸
    SMALL_FACE = "small_face"  # 人脸太小
    LARGE_FACE = "large_face"  # 人脸太大
    LOW_CONFIDENCE = "low_confidence"  # 置信度低
    ERROR = "error"  # 处理错误


@dataclass
class FaceInfo:
    """人脸信息"""

    x: int  # 左上角x
    y: int  # 左上角y
    width: int  # 宽度
    height: int  # 高度
    confidence: float  # 置信度 (0-1)

    @property
    def area(self) -> int:
        """人脸面积"""
        return self.width * self.height


@dataclass
class FilterResult:
    """筛选结果"""

    image_path: Path
    reason: FilterReason
    faces: List[FaceInfo]
    face_ratio: float  # 最大人脸占比
    message: str  # 说明信息


class FaceDetector:
    """人脸检测器（基于OpenCV DNN）"""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_face_ratio: float = 0.30,
        max_face_ratio: float = 0.90,
        model_selection: int = 1,
    ):
        """
        初始化人脸检测器

        Args:
            min_detection_confidence: 最小检测置信度
            min_face_ratio: 最小人脸占比
            max_face_ratio: 最大人脸占比
            model_selection: 模型选择（保留参数，OpenCV不使用）
        """
        self.min_confidence = min_detection_confidence
        self.min_face_ratio = min_face_ratio
        self.max_face_ratio = max_face_ratio

        # 使用OpenCV DNN人脸检测
        self._net = None
        self._initialized = False

    def _init_detector(self):
        """初始化检测器（延迟加载）"""
        if self._initialized:
            return

        # 使用Haar级联分类器（OpenCV内置，无需额外模型文件）
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._cascade = cv2.CascadeClassifier(cascade_path)
        self._use_cascade = True

        self._initialized = True

    def detect_faces(self, image_path: Path) -> List[FaceInfo]:
        """
        检测图片中的人脸

        Args:
            image_path: 图片路径

        Returns:
            人脸信息列表
        """
        self._init_detector()

        # 读取图片 (使用PIL处理中文路径，再转换为OpenCV格式)
        try:
            pil_image = Image.open(image_path).convert("RGB")
            image = np.array(pil_image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"无法读取图片: {image_path} - {e}")

        faces = []

        # 使用Haar级联分类器
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        detected = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        for x, y, width, height in detected:
            faces.append(
                FaceInfo(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    confidence=0.7,  # Haar分类器没有置信度，使用固定值
                )
            )

        return faces

    def calculate_face_ratio(self, faces: List[FaceInfo], image_path: Path) -> float:
        """
        计算最大人脸占比

        Args:
            faces: 人脸列表
            image_path: 图片路径

        Returns:
            人脸占比 (0-1)
        """
        if not faces:
            return 0.0

        # 获取图片尺寸
        with Image.open(image_path) as img:
            img_width, img_height = img.size

        image_area = img_width * img_height

        # 找到最大的人脸
        max_face_area = max(face.area for face in faces)

        return max_face_area / image_area if image_area > 0 else 0.0

    def filter_image(self, image_path: Path) -> FilterResult:
        """
        筛选单张图片

        Args:
            image_path: 图片路径

        Returns:
            筛选结果
        """
        try:
            # 检测人脸
            faces = self.detect_faces(image_path)

            # 无人脸
            if not faces:
                return FilterResult(
                    image_path=image_path,
                    reason=FilterReason.NO_FACE,
                    faces=[],
                    face_ratio=0.0,
                    message="未检测到人脸",
                )

            # 计算人脸占比
            face_ratio = self.calculate_face_ratio(faces, image_path)

            # 检查置信度
            max_confidence = max(f.confidence for f in faces)
            if max_confidence < self.min_confidence:
                return FilterResult(
                    image_path=image_path,
                    reason=FilterReason.LOW_CONFIDENCE,
                    faces=faces,
                    face_ratio=face_ratio,
                    message=f"人脸置信度过低 ({max_confidence:.2f} < {self.min_confidence})",
                )

            # 人脸太小
            if face_ratio < self.min_face_ratio:
                return FilterResult(
                    image_path=image_path,
                    reason=FilterReason.SMALL_FACE,
                    faces=faces,
                    face_ratio=face_ratio,
                    message=f"人脸占比过小 ({face_ratio:.2%} < {self.min_face_ratio:.0%})",
                )

            # 人脸太大（特写）
            if face_ratio > self.max_face_ratio:
                return FilterResult(
                    image_path=image_path,
                    reason=FilterReason.LARGE_FACE,
                    faces=faces,
                    face_ratio=face_ratio,
                    message=f"人脸占比过大 ({face_ratio:.2%} > {self.max_face_ratio:.0%})",
                )

            # 通过筛选
            return FilterResult(
                image_path=image_path,
                reason=FilterReason.PASSED,
                faces=faces,
                face_ratio=face_ratio,
                message=f"通过 ({face_ratio:.2%}, {len(faces)}个人脸)",
            )

        except Exception as e:
            return FilterResult(
                image_path=image_path,
                reason=FilterReason.ERROR,
                faces=[],
                face_ratio=0.0,
                message=f"处理错误: {str(e)}",
            )

    def close(self):
        """释放资源"""
        self._initialized = False


class ImageFilter:
    """图片筛选器"""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_face_ratio: float = 0.30,
        max_face_ratio: float = 0.90,
        copy_mode: bool = False,
    ):
        """
        初始化筛选器

        Args:
            min_detection_confidence: 最小检测置信度
            min_face_ratio: 最小人脸占比
            max_face_ratio: 最大人脸占比
            copy_mode: True=复制，False=移动
        """
        self.detector = FaceDetector(
            min_detection_confidence=min_detection_confidence,
            min_face_ratio=min_face_ratio,
            max_face_ratio=max_face_ratio,
        )
        self.copy_mode = copy_mode

        self.stats = {
            "total": 0,
            "passed": 0,
            "rejected": {
                "no_face": 0,
                "small_face": 0,
                "large_face": 0,
                "low_confidence": 0,
                "error": 0,
            },
        }

    def filter_folder(
        self,
        input_folder: str,
        output_filtered: str,
        output_rejected: str,
        supported_extensions: List[str] = None,
    ) -> Dict:
        """
        筛选整个文件夹的图片

        Args:
            input_folder: 输入文件夹
            output_filtered: 合格图片输出目录
            output_rejected: 不合格图片输出目录
            supported_extensions: 支持的图片格式

        Returns:
            统计信息
        """
        input_path = Path(input_folder).resolve()
        filtered_path = Path(output_filtered).resolve()
        rejected_path = Path(output_rejected).resolve()

        # 创建输出目录
        filtered_path.mkdir(parents=True, exist_ok=True)
        rejected_path.mkdir(parents=True, exist_ok=True)

        # 创建分类子目录
        for reason in FilterReason:
            if reason != FilterReason.PASSED:
                (rejected_path / reason.value).mkdir(exist_ok=True)

        # 查找所有图片
        if supported_extensions is None:
            supported_extensions = [".jpg", ".jpeg", ".png", ".webp"]

        images = []
        for ext in supported_extensions:
            images.extend(input_path.rglob(f"*{ext}"))
            images.extend(input_path.rglob(f"*{ext.upper()}"))

        images = sorted(set(images))
        self.stats["total"] = len(images)

        print(f"[INFO] 找到 {len(images)} 张图片，开始筛选...")
        print(
            f"   人脸占比阈值: {self.detector.min_face_ratio:.0%} - {self.detector.max_face_ratio:.0%}"
        )
        print()

        # 处理每张图片
        for i, img_path in enumerate(images, 1):
            result = self.detector.filter_image(img_path)

            # 确定目标路径
            if result.reason == FilterReason.PASSED:
                dest_path = filtered_path / img_path.name
                self.stats["passed"] += 1
                status = "[OK]"
            else:
                dest_path = rejected_path / result.reason.value / img_path.name
                self.stats["rejected"][result.reason.value] += 1
                status = "[XX]"

            # 处理重名
            dest_path = self._get_unique_path(dest_path)

            # 复制或移动
            try:
                if self.copy_mode:
                    shutil.copy2(img_path, dest_path)
                else:
                    shutil.move(str(img_path), str(dest_path))
            except Exception as e:
                print(f"   文件操作失败: {e}")
                continue

            # 打印进度
            if i % 20 == 0 or i <= 5:
                print(f"{status} [{i}/{len(images)}] {img_path.name}")
                print(f"   └─ {result.message}")

        return self.get_stats()

    def _get_unique_path(self, path: Path) -> Path:
        """生成唯一路径"""
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

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()

    def close(self):
        """释放资源"""
        self.detector.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def filter_images(
    input_folder: str,
    output_folder: str = None,
    min_face_ratio: float = 0.30,
    max_face_ratio: float = 0.90,
    copy_mode: bool = True,
) -> Dict:
    """
    筛选图片的便捷函数

    Args:
        input_folder: 输入文件夹
        output_folder: 输出文件夹
        min_face_ratio: 最小人脸占比
        max_face_ratio: 最大人脸占比
        copy_mode: 复制模式

    Returns:
        统计信息
    """
    from config import get_config

    config = get_config()
    if output_folder is None:
        output_folder = config["output_dir"]

    filtered_dir = str(Path(output_folder) / "filtered")
    rejected_dir = str(Path(output_folder) / "rejected")

    with ImageFilter(
        min_face_ratio=min_face_ratio,
        max_face_ratio=max_face_ratio,
        copy_mode=copy_mode,
    ) as filter_obj:
        return filter_obj.filter_folder(
            input_folder=input_folder,
            output_filtered=filtered_dir,
            output_rejected=rejected_dir,
            supported_extensions=config["image_extensions"],
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python filter.py <输入文件夹> [--output <输出文件夹>]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = (
        sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--output" else None
    )

    result = filter_images(input_dir, output_dir)

    print(f"\n[INFO] 筛选完成！")
    print(f"   总数: {result['total']}")
    print(f"   通过: {result['passed']}")
    print(f"   筛除: {result['total'] - result['passed']}")
    print(f"     - 无人脸: {result['rejected']['no_face']}")
    print(f"     - 人脸太小: {result['rejected']['small_face']}")
    print(f"     - 人脸太大: {result['rejected']['large_face']}")
    print(f"     - 置信度低: {result['rejected']['low_confidence']}")
    print(f"     - 处理错误: {result['rejected']['error']}")
