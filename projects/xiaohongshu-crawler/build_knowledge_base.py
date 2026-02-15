"""
结合图片反推和笔记内容生成提示词
"""

import json
import sys
from pathlib import Path

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============ 配置 ============
# 笔记JSON文件
NOTES_FILE = r"D:\xiaohongshu-crawler\output\notes_20260108_085720.json"

# 图片目录
IMAGES_DIR = r"D:\xiaohongshu-crawler\output\glasses_images"

# 反推结果文件
REVERSE_FILE = r"D:\xiaohongshu-crawler\output\reverse_prompts_glasses.txt"

# 最终输出文件
OUTPUT_FILE = r"D:\xiaohongshu-crawler\output\knowledge_base_glasses_outfit.txt"


def load_notes():
    """加载笔记数据"""
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_reverse_results():
    """加载反推结果"""
    results = {}

    with open(REVERSE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_note = None

    for line in lines:
        line = line.strip()

        if line.startswith('【笔记】'):
            current_note = line.replace('【笔记】', '').strip()
            results[current_note] = []

        elif line.startswith('提示词:') and current_note:
            caption = line.replace('提示词:', '').strip()
            results[current_note].append(caption)

    return results


def generate_enhanced_prompt(note, caption):
    """结合笔记内容和图片反推生成增强的提示词"""

    # 笔记信息
    title = note.get('title', '')
    content = note.get('content', '')

    # 清理标签
    content_clean = ' '.join([line for line in content.split('\n') if not line.strip().startswith('#')])

    # 关键词提取（简单的）
    keywords = []
    if '高智' in content or '高知' in content:
        keywords.append('高知感')
    if '韩系' in content or '韩' in content:
        keywords.append('韩系')
    if '温柔' in content:
        keywords.append('温柔')
    if '姐姐' in content:
        keywords.append('姐姐感')
    if 'cleanfit' in content.lower():
        keywords.append('cleanfit风格')
    if '通勤' in content:
        keywords.append('通勤')
    if '日常' in content:
        keywords.append('日常')

    # 将英文caption翻译成中文描述
    caption_cn = translate_caption(caption)

    # 生成完整的提示词
    prompt_parts = []

    # 1. 场景描述（基于反推）
    prompt_parts.append(f"场景：{caption_cn}")

    # 2. 人物状态
    if 'woman' in caption.lower() or 'girl' in caption.lower():
        prompt_parts.append("人物：一位戴眼镜的年轻女性")

    # 3. 氛围风格
    style_words = []
    if '高知感' in keywords:
        style_words.append("知性优雅")
    if '韩系' in keywords:
        style_words.append("韩系温柔")
    if '温柔' in keywords:
        style_words.append("温柔恬静")
    if '姐姐' in keywords:
        style_words.append("成熟姐姐风")

    if style_words:
        prompt_parts.append(f"风格：{', '.join(style_words)}")

    # 4. 摄影风格
    prompt_parts.append("摄影：iPhone拍摄，自然光，真实生活感")

    # 5. 穿搭细节（从内容中提取）
    outfit_keywords = []
    if '衬衫' in content:
        outfit_keywords.append('衬衫')
    if '针织' in content:
        outfit_keywords.append('针织')
    if '西装' in content:
        outfit_keywords.append('西装')
    if '大衣' in content:
        outfit_keywords.append('大衣')
    if 'polo' in content.lower():
        outfit_keywords.append('polo衫')
    if '毛衣' in content:
        outfit_keywords.append('毛衣')
    if '黑色' in title or '黑色' in content:
        outfit_keywords.append('黑色系')
    if '白色' in title or '白色' in content:
        outfit_keywords.append('白色系')

    if outfit_keywords:
        prompt_parts.append(f"穿搭：{', '.join(outfit_keywords)}")

    # 6. 氛围感
    prompt_parts.append("氛围：松弛、自然、充满生活气息")

    # 组合所有部分
    full_prompt = '，'.join(prompt_parts)

    return full_prompt


def translate_caption(caption):
    """简单的英文caption翻译"""
    translations = {
        "a series of glasses with different frames": "多副不同款式眼镜的展示",
        "a pair of glasses with a stuffed animal on them": "一副眼镜搭配毛绒玩具",
        "a woman with glasses drinking a drink": "一位戴眼镜的女性正在喝饮料",
        "a woman wearing glasses and holding a flower": "一位戴眼镜的女性手持花朵",
        "a woman sitting at a table with a glass": "一位女性坐在桌边，面前有水杯",
        "a woman sitting at a table with a cup": "一位女性坐在桌边，面前有杯子",
        "a young woman in a white shirt and black bag": "一位穿白色衬衫、背黑色包的年轻女性",
        "a woman with long hair and a black shirt": "一位长发女性，身穿黑色上衣"
    }

    return translations.get(caption, caption)


def build_knowledge_base(notes, reverse_results):
    """构建知识库"""
    knowledge_base = []

    for idx, note in enumerate(notes, 1):
        # 获取笔记对应的反推结果
        note_dir_name = f"{idx:02d}_"

        # 查找匹配的反推结果
        caption = None
        for key in reverse_results:
            if key.startswith(str(idx)) and reverse_results[key]:
                caption = reverse_results[key][0]
                break

        if not caption:
            print(f"  跳过（没有反推结果）: {note['title']}")
            continue

        # 生成增强的提示词
        enhanced_prompt = generate_enhanced_prompt(note, caption)

        knowledge_base.append({
            'id': idx,
            'title': note['title'],
            'original_caption': caption,
            'enhanced_prompt': enhanced_prompt,
            'content_summary': note['content'][:200] + '...' if len(note['content']) > 200 else note['content']
        })

    return knowledge_base


def save_knowledge_base(knowledge_base):
    """保存知识库到文件"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("眼镜穿搭提示词知识库\n")
        f.write("=" * 100 + "\n\n")
        f.write("本知识库基于小红书'眼镜穿搭'专题的10篇笔记生成\n")
        f.write("包含原始图片反推描述 + 笔记内容分析 + 增强版提示词\n\n")
        f.write("=" * 100 + "\n\n")

        for item in knowledge_base:
            f.write(f"【示例 {item['id']}】{item['title']}\n")
            f.write("-" * 100 + "\n\n")

            f.write("原始笔记内容摘要:\n")
            f.write(f"{item['content_summary']}\n\n")

            f.write("原始图片反推:\n")
            f.write(f"{item['original_caption']}\n\n")

            f.write("【增强版提示词】\n")
            f.write(f"{item['enhanced_prompt']}\n\n")

            f.write("=" * 100 + "\n\n")

        f.write(f"\n总计：{len(knowledge_base)} 个提示词示例\n")
        f.write("=" * 100 + "\n")


def analyze_patterns(knowledge_base):
    """分析提示词模式"""
    print("\n" + "=" * 100)
    print("提示词模式分析")
    print("=" * 100)

    # 统计关键词
    all_prompts = [item['enhanced_prompt'] for item in knowledge_base]

    # 常用场景
    print("\n【常用场景元素】")
    scenes = ["咖啡店", "居家", "街拍", "办公室", "户外", "餐厅"]
    for scene in scenes:
        count = sum(1 for p in all_prompts if scene in p)
        if count > 0:
            print(f"  {scene}: {count}次")

    # 常用风格
    print("\n【常用风格词】")
    styles = ["韩系", "高知感", "温柔", "知性", "日常", "通勤"]
    for style in styles:
        count = sum(1 for p in all_prompts if style in p)
        if count > 0:
            print(f"  {style}: {count}次")

    # 常用穿搭
    print("\n【常用穿搭元素】")
    outfits = ["衬衫", "针织", "西装", "毛衣", "大衣", "polo"]
    for outfit in outfits:
        count = sum(1 for p in all_prompts if outfit in p)
        if count > 0:
            print(f"  {outfit}: {count}次")

    # 摄影风格
    print("\n【摄影风格】")
    print("  iPhone拍摄: 100%")
    print("  自然光: 100%")
    print("  真实生活感: 100%")

    print("\n" + "=" * 100)


if __name__ == "__main__":
    print("正在加载笔记数据...")
    notes = load_notes()
    print(f"加载了 {len(notes)} 篇笔记")

    print("\n正在加载反推结果...")
    reverse_results = load_reverse_results()
    print(f"加载了 {len(reverse_results)} 条反推结果")

    print("\n正在构建知识库...")
    knowledge_base = build_knowledge_base(notes, reverse_results)
    print(f"生成了 {len(knowledge_base)} 条知识库条目")

    print("\n正在保存知识库...")
    save_knowledge_base(knowledge_base)

    print("\n正在分析提示词模式...")
    analyze_patterns(knowledge_base)

    print(f"\n完成！知识库已保存到: {OUTPUT_FILE}")
