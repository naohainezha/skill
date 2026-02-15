"""
小红书素材整理自动化工具 - CLI命令行界面
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 添加项目目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_config, DEFAULT_CONFIG
from merge import merge_folders, ImageMerger
from filter import filter_images, ImageFilter


console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    小红书素材整理工具

    自动化处理图片：合并 -> 人脸检测 -> 筛选
    """
    pass


@cli.command()
@click.argument("folders", nargs=-1, required=True)
@click.option("--output", "-o", help="输出文件夹路径")
@click.option("--preserve-structure", is_flag=True, help="保留原始目录结构")
@click.option("--copy", is_flag=True, help="复制模式（默认移动）")
@click.option(
    "--threshold", "-t", default=0.95, help="去重相似度阈值 (0-1)", show_default=True
)
def merge(
    folders: tuple, output: str, preserve_structure: bool, copy: bool, threshold: float
):
    """
    合并多个文件夹的图片

    示例:
        xhs-filter merge folder1 folder2 folder3 --output merged/
        xhs-filter merge /path/to/notes/* --output all_images/
    """
    if not folders:
        console.print("[red]请指定至少一个输入文件夹[/red]")
        return

    input_folders = list(folders)

    if output is None:
        output = str(Path(input_folders[0]).parent / "merged")

    console.print(
        Panel(
            f"[bold blue]图片合并[/bold blue]\n"
            f"输入: {len(input_folders)} 个文件夹\n"
            f"输出: {output}",
            title="开始合并",
        )
    )

    try:
        with console.status("[bold green]正在合并图片..."):
            result = merge_folders(
                input_folders=input_folders,
                output_folder=output,
                preserve_structure=preserve_structure,
                copy_mode=not copy,
            )

        # 显示结果
        table = Table(title="合并结果")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="magenta")

        table.add_row("找到图片", str(result["total"]))
        table.add_row("[green]成功合并", f"[green]{result['success']}[/green]")
        table.add_row("[yellow]重复跳过", f"[yellow]{result['skipped']}[/yellow]")
        table.add_row("[red]处理错误", f"[red]{result['errors']}[/red]")

        console.print(table)
        console.print(f"\n[green]合并完成！输出目录: {output}[/green]")

    except Exception as e:
        console.print(f"[red]合并失败: {e}[/red]")


@cli.command()
@click.argument("input_folder")
@click.option("--output", "-o", help="输出文件夹路径")
@click.option(
    "--min-ratio",
    default=0.02,
    help="最小人脸占比 (0-1), 默认2%适合全身照博主",
    show_default=True,
)
@click.option("--max-ratio", default=0.90, help="最大人脸占比 (0-1)", show_default=True)
@click.option(
    "--confidence", default=0.5, help="人脸检测置信度 (0-1)", show_default=True
)
@click.option("--copy", is_flag=True, help="复制模式（默认移动，会删除原文件）")
def filter(
    input_folder: str,
    output: str,
    min_ratio: float,
    max_ratio: float,
    confidence: float,
    copy: bool,
):
    """
    人脸检测筛选图片

    根据人脸占比筛选合格素材，筛除无人物或人脸过小的图片

    示例:
        xhs-filter filter ./downloads --output ./filtered
        xhs-filter filter ./images --min-ratio 0.25 --max-ratio 0.80
    """
    config = get_config()

    if output is None:
        output = config["output_dir"]

    console.print(
        Panel(
            f"[bold blue]人脸检测筛选[/bold blue]\n"
            f"输入: {input_folder}\n"
            f"输出: {output}\n"
            f"人脸占比阈值: {min_ratio:.0%} - {max_ratio:.0%}",
            title="开始筛选",
        )
    )

    try:
        with ImageFilter(
            min_detection_confidence=confidence,
            min_face_ratio=min_ratio,
            max_face_ratio=max_ratio,
            copy_mode=copy,
        ) as filter_obj:
            filtered_dir = str(Path(output) / "filtered")
            rejected_dir = str(Path(output) / "rejected")

            # 清空上一次的输出目录，避免累积
            for d in [filtered_dir, rejected_dir]:
                p = Path(d)
                if p.exists():
                    shutil.rmtree(p)
                p.mkdir(parents=True, exist_ok=True)

            with console.status("[bold green]正在检测人脸..."):
                result = filter_obj.filter_folder(
                    input_folder=input_folder,
                    output_filtered=filtered_dir,
                    output_rejected=rejected_dir,
                    supported_extensions=config["image_extensions"],
                )

        # 显示结果
        table = Table(title="筛选结果")
        table.add_column("项目", style="cyan")
        table.add_column("数量", style="magenta")

        table.add_row("总图片数", str(result["total"]))
        table.add_row("[green]通过筛选", f"[green]{result['passed']}[/green]")
        table.add_row(
            "[red]筛除总计", f"[red]{result['total'] - result['passed']}[/red]"
        )
        table.add_row("  ├─ 无人脸", str(result["rejected"]["no_face"]))
        table.add_row("  ├─ 人脸太小", str(result["rejected"]["small_face"]))
        table.add_row("  ├─ 人脸太大", str(result["rejected"]["large_face"]))
        table.add_row("  ├─ 置信度低", str(result["rejected"]["low_confidence"]))
        table.add_row("  └─ 处理错误", str(result["rejected"]["error"]))

        console.print(table)

        pass_rate = (
            result["passed"] / result["total"] * 100 if result["total"] > 0 else 0
        )
        console.print(f"\n[green]筛选完成！通过率: {pass_rate:.1f}%[/green]")
        console.print(f"[dim]合格素材: {filtered_dir}[/dim]")
        console.print(f"[dim]筛除图片: {rejected_dir}[/dim]")

        # 筛选完成后清空输入目录的图片，避免下次重复筛选
        input_path = Path(input_folder)
        if input_path.exists():
            image_exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
            removed = 0
            for f in input_path.iterdir():
                if f.is_file() and f.suffix.lower() in image_exts:
                    f.unlink()
                    removed += 1
            if removed > 0:
                console.print(f"[dim]已清理输入目录 {removed} 张图片[/dim]")

    except ImportError as e:
        console.print(f"[red]缺少依赖: {e}[/red]")
        console.print("[yellow]请运行: pip install mediapipe opencv-python[/yellow]")
    except Exception as e:
        console.print(f"[red]筛选失败: {e}[/red]")


@cli.command()
@click.argument("folders", nargs=-1, required=True)
@click.option("--output", "-o", help="输出文件夹路径")
@click.option(
    "--min-ratio",
    default=0.02,
    help="最小人脸占比, 默认2%适合全身照博主",
    show_default=True,
)
@click.option("--max-ratio", default=0.90, help="最大人脸占比", show_default=True)
@click.option("--confidence", default=0.5, help="人脸检测置信度", show_default=True)
@click.option("--copy", is_flag=True, help="复制模式（默认移动）")
def process(
    folders: tuple,
    output: str,
    min_ratio: float,
    max_ratio: float,
    confidence: float,
    copy: bool,
):
    """
    一键处理：合并 + 人脸筛选

    先合并多个文件夹，然后自动进行人脸检测筛选

    示例:
        xhs-filter process folder1 folder2 --output ./final
    """
    if not folders:
        console.print("[red]请指定至少一个输入文件夹[/red]")
        return

    input_folders = list(folders)

    if output is None:
        output = str(Path(input_folders[0]).parent / "processed")

    # 步骤1: 合并
    console.print(Panel("[bold blue]步骤 1/2: 合并图片[/bold blue]", title="Step 1"))

    merged_dir = str(Path(output) / "_merged")

    try:
        result_merge = merge_folders(
            input_folders=input_folders,
            output_folder=merged_dir,
            copy_mode=True,  # 合并阶段始终复制
        )

        console.print(f"[green]合并完成: {result_merge['success']} 张图片[/green]\n")

        if result_merge["success"] == 0:
            console.print("[yellow]没有图片需要处理[/yellow]")
            return

        # 步骤2: 筛选
        console.print(
            Panel("[bold blue]步骤 2/2: 人脸检测筛选[/bold blue]", title="Step 2")
        )

        config = get_config()

        with ImageFilter(
            min_detection_confidence=confidence,
            min_face_ratio=min_ratio,
            max_face_ratio=max_ratio,
            copy_mode=copy,
        ) as filter_obj:
            filtered_dir = str(Path(output) / "filtered")
            rejected_dir = str(Path(output) / "rejected")

            result_filter = filter_obj.filter_folder(
                input_folder=merged_dir,
                output_filtered=filtered_dir,
                output_rejected=rejected_dir,
                supported_extensions=config["image_extensions"],
            )

        # 清理临时合并目录
        if not copy:
            import shutil

            shutil.rmtree(merged_dir, ignore_errors=True)

        # 显示最终结果
        console.print("")
        console.print(
            Panel(
                f"[bold green]处理完成！[/bold green]\n\n"
                f"输入图片: {result_merge['total']}\n"
                f"重复跳过: {result_merge['skipped']}\n"
                f"人脸筛选: {result_filter['passed']} / {result_filter['total']}\n"
                f"最终合格: {result_filter['passed']} 张",
                title="Result",
            )
        )

        console.print(f"\n[green]输出目录: {output}[/green]")
        console.print(f"  [cyan]filtered/[/cyan] - passed")
        console.print(f"  [dim]rejected/[/dim] - rejected")

    except Exception as e:
        console.print(f"[red]处理失败: {e}[/red]")


@cli.command()
def config():
    """
    显示当前配置

    查看默认路径、人脸检测参数等配置信息
    """
    cfg = get_config()

    table = Table(title="当前配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="yellow")

    # 路径配置
    table.add_row("输入目录", cfg["input_dir"], style="dim")
    table.add_row("输出目录", cfg["output_dir"], style="dim")
    table.add_row("合格素材目录", cfg["filtered_dir"], style="dim")
    table.add_row("筛除图片目录", cfg["rejected_dir"], style="dim")

    table.add_row("", "", style="dim")

    # 人脸检测配置
    fd = cfg["face_detection"]
    table.add_row("检测置信度", f"{fd['min_detection_confidence']}")
    table.add_row("最小人脸占比", f"{fd['min_face_ratio']:.0%}")
    table.add_row("最大人脸占比", f"{fd['max_face_ratio']:.0%}")

    table.add_row("", "", style="dim")

    # 处理配置
    proc = cfg["processing"]
    table.add_row("跳过重复图片", "是" if proc["skip_duplicates"] else "否")
    table.add_row("操作模式", "复制" if proc["copy_mode"] else "移动")

    console.print(table)


@cli.command()
@click.argument("image_path")
@click.option("--confidence", default=0.5, help="检测置信度", show_default=True)
def detect(image_path: str, confidence: float):
    """
    检测单张图片的人脸

    用于测试人脸检测效果

    示例:
        xhs-filter detect ./test.jpg
        xhs-filter detect ./test.jpg --confidence 0.7
    """
    from filter import FaceDetector
    from PIL import Image

    img_path = Path(image_path)

    if not img_path.exists():
        console.print(f"[red]文件不存在: {image_path}[/red]")
        return

    console.print(f"[blue]检测图片: {img_path.name}[/blue]\n")

    try:
        detector = FaceDetector(min_detection_confidence=confidence)

        # 检测人脸
        faces = detector.detect_faces(img_path)

        # 获取图片尺寸
        with Image.open(img_path) as img:
            img_width, img_height = img.size

        console.print(f"图片尺寸: {img_width} x {img_height}")
        console.print(f"检测到人脸: {len(faces)} 个\n")

        if faces:
            table = Table(title="人脸详情")
            table.add_column("#", style="cyan")
            table.add_column("位置 (x, y)", style="yellow")
            table.add_column("尺寸 (w x h)", style="yellow")
            table.add_column("置信度", style="green")
            table.add_column("占比", style="magenta")

            for i, face in enumerate(faces, 1):
                ratio = face.area / (img_width * img_height)
                table.add_row(
                    str(i),
                    f"({face.x}, {face.y})",
                    f"{face.width} x {face.height}",
                    f"{face.confidence:.2%}",
                    f"{ratio:.2%}",
                )

            console.print(table)

            # 筛选建议
            max_ratio = max(f.area for f in faces) / (img_width * img_height)
            if max_ratio < 0.30:
                console.print(
                    f"\n[yellow]人脸占比过小 ({max_ratio:.2%} < 30%)，会被筛除[/yellow]"
                )
            elif max_ratio > 0.90:
                console.print(
                    f"\n[yellow]人脸占比过大 ({max_ratio:.2%} > 90%)，会被筛除[/yellow]"
                )
            else:
                console.print(
                    f"\n[green]人脸占比合适 ({max_ratio:.2%})，会通过筛选[/green]"
                )
        else:
            console.print("[red]未检测到人脸[/red]")

        detector.close()

    except ImportError:
        console.print("[red]请先安装依赖: pip install mediapipe opencv-python[/red]")
    except Exception as e:
        console.print(f"[red]检测失败: {e}[/red]")


def main():
    """主入口"""
    cli()


if __name__ == "__main__":
    main()
