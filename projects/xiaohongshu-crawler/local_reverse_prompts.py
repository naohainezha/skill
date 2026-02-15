"""
本地图片反推提示词生成器
使用transformers库的BLIP模型
"""

import os
import sys
from pathlib import Path
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============ 配置 ============
# 输入图片目录
INPUT_DIR = r"D:\xiaohongshu-crawler\output\glasses_images"

# 输出文件
OUTPUT_FILE = r"D:\xiaohongshu-crawler\output\reverse_prompts_glasses.txt"

# 模型缓存目录（使用HuggingFace缓存）
MODEL_NAME = "Salesforce/blip-image-captioning-base"

# 每篇笔记选择几张图片进行反推
IMAGES_PER_NOTE = 1


def load_model():
    """加载BLIP模型"""
    print("正在加载BLIP模型...")
    print(f"模型: {MODEL_NAME}")
    print("首次运行会自动下载模型，请耐心等待...")

    processor = BlipProcessor.from_pretrained(MODEL_NAME)
    model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)

    # 如果有GPU，使用GPU加速
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"使用设备: {device}")

    return processor, model, device


def generate_caption(image_path, processor, model, device):
    """为图片生成描述"""
    try:
        # 打开图片
        raw_image = Image.open(image_path).convert('RGB')

        # 处理图片
        inputs = processor(raw_image, return_tensors="pt").to(device)

        # 生成描述
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return caption

    except Exception as e:
        print(f"    错误: {e}")
        return None


def batch_process_images(processor, model, device):
    """批量处理图片"""
    # 获取所有笔记目录
    note_dirs = sorted([d for d in Path(INPUT_DIR).iterdir() if d.is_dir()])

    print(f"找到 {len(note_dirs)} 个笔记目录")

    results = []

    for idx, note_dir in enumerate(note_dirs, 1):
        print(f"\n处理第 {idx} 个笔记: {note_dir.name}")

        # 获取该笔记的所有图片
        image_files = sorted([f for f in note_dir.iterdir() if f.suffix.lower() in ['.png', '.jpg', '.jpeg']])

        if not image_files:
            print(f"  没有找到图片，跳过")
            continue

        # 选择前N张图片
        selected_images = image_files[:IMAGES_PER_NOTE]

        for img_path in selected_images:
            print(f"  处理图片: {img_path.name}")

            # 生成描述
            caption = generate_caption(str(img_path), processor, model, device)

            if caption:
                print(f"    描述: {caption}")
                results.append({
                    'note': note_dir.name,
                    'image': img_path.name,
                    'caption': caption
                })
            else:
                print(f"    生成失败")

            # 每次处理完一张图片就保存进度
            save_results(results)

    return results


def save_results(results):
    """保存结果到文件"""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("眼镜穿搭图片反推提示词知识库\n")
        f.write(f"生成时间: {Path(__file__).stat().st_mtime}\n")
        f.write("=" * 80 + "\n\n")

        current_note = None

        for result in results:
            # 如果是新笔记，添加标题
            if result['note'] != current_note:
                current_note = result['note']
                f.write(f"【笔记】{current_note}\n")
                f.write("-" * 80 + "\n")

            f.write(f"图片: {result['image']}\n")
            f.write(f"提示词: {result['caption']}\n")
            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write(f"共 {len(results)} 个提示词\n")
        f.write("=" * 80 + "\n")


if __name__ == "__main__":
    # 检查输入目录
    if not os.path.exists(INPUT_DIR):
        print(f"错误: 输入目录不存在: {INPUT_DIR}")
        sys.exit(1)

    # 加载模型
    processor, model, device = load_model()

    # 批量处理图片
    results = batch_process_images(processor, model, device)

    print(f"\n完成！共处理 {len(results)} 张图片")
    print(f"结果已保存到: {OUTPUT_FILE}")
