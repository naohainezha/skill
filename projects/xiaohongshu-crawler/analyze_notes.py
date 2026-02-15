"""
小红书笔记分析脚本 - 分析采集笔记的特点
"""
import os
import sys
import json
import re
from collections import Counter
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def analyze_notes(json_file):
    """分析小红书笔记特点"""

    with open(json_file, 'r', encoding='utf-8') as f:
        notes = json.load(f)

    print("="*60)
    print("小红书笔记特点分析报告")
    print("="*60)

    # 1. 标题分析
    print("\n【一、标题特点】")
    title_lengths = []
    title_has_emoji = []
    title_symbols = []

    for note in notes:
        title = note['title']
        title_lengths.append(len(title))

        # 检测emoji
        emoji_pattern = re.compile(r'[^\w\s\u4e00-\u9fff,.!?;:，。！？；：]')
        has_emoji = emoji_pattern.findall(title)
        title_has_emoji.append(len(has_emoji) > 0)

        # 提取特殊符号
        if has_emoji:
            title_symbols.extend(has_emoji)

    print(f"- 平均标题长度：{sum(title_lengths)/len(title_lengths):.1f}字符")
    print(f"- 最短标题：{min(title_lengths)}字符")
    print(f"- 最长标题：{max(title_lengths)}字符")
    print(f"- 使用emoji比例：{sum(title_has_emoji)}/{len(notes)} ({sum(title_has_emoji)/len(notes)*100:.0f}%)")
    print(f"- 常用符号：{Counter(title_symbols).most_common(5)}")

    # 2. 内容分析
    print("\n【二、正文特点】")
    content_lengths = []
    tag_counts = []
    all_tags = []

    for note in notes:
        content = note['content']
        content_lengths.append(len(content))

        # 提取标签
        tags = re.findall(r'#([^\s#]+)', content)
        tag_counts.append(len(tags))
        all_tags.extend(tags)

    print(f"- 平均正文长度：{sum(content_lengths)/len(content_lengths):.0f}字符")
    print(f"- 最短正文：{min(content_lengths)}字符")
    print(f"- 最长正文：{max(content_lengths)}字符")
    print(f"- 平均标签数：{sum(tag_counts)/len(tag_counts):.1f}个")
    print(f"- 常用标签：{Counter(all_tags).most_common(10)}")

    # 3. 内容结构分析
    print("\n【三、内容结构】")
    has_list = []
    has_emoji_content = []
    has_numbering = []

    for note in notes:
        content = note['content']

        # 检测列表形式
        list_pattern = re.compile(r'^[\s]*(•|·|○|\*|-|\d+\.|\d+、)', re.MULTILINE)
        has_list.append(len(list_pattern.findall(content)) > 0)

        # 检测emoji使用
        emoji_pattern = re.compile(r'[^\w\s\u4e00-\u9fff,.!?;:，。！？；：\n\r\(\)\[\]{}]')
        has_emoji_content.append(len(emoji_pattern.findall(content)) > 3)

        # 检测编号形式
        numbering_pattern = re.compile(r'^[\s]*(1️⃣|2️⃣|3️⃣|🌟|【)', re.MULTILINE)
        has_numbering.append(len(numbering_pattern.findall(content)) > 0)

    print(f"- 使用列表形式：{sum(has_list)}/{len(notes)} ({sum(has_list)/len(notes)*100:.0f}%)")
    print(f"- 大量使用emoji：{sum(has_emoji_content)}/{len(notes)} ({sum(has_emoji_content)/len(notes)*100:.0f}%)")
    print(f"- 使用编号/标记：{sum(has_numbering)}/{len(notes)} ({sum(has_numbering)/len(notes)*100:.0f}%)")

    # 4. 主题类型分析
    print("\n【四、笔记类型】")
    types = {
        "教程攻略": 0,
        "穿搭分享": 0,
        "日常记录": 0,
        "产品合集": 0
    }

    for note in notes:
        content = note['content'] + note['title']

        if any(word in content for word in ['攻略', '教程', '公式', '如何', '小技巧']):
            types["教程攻略"] += 1
        elif any(word in content for word in ['搭配', '穿搭', '韩系', '风格']):
            types["穿搭分享"] += 1
        elif any(word in content for word in ['日常', '记录', '阳光', '幸福', 'live']):
            types["日常记录"] += 1
        elif any(word in content for word in ['合集', '推荐', '清单']):
            types["产品合集"] += 1

    for note_type, count in types.items():
        if count > 0:
            print(f"- {note_type}：{count}篇")

    # 5. 总结规律
    print("\n【五、创作规律总结】")
    print("""
根据分析，小红书笔记创作有以下特点：

1. 标题特征：
   - 简短有力（10-20字符）
   - 大量使用emoji吸引眼球
   - 使用特殊符号（👓、☀️、🥯等）增加视觉效果

2. 内容特征：
   - 长度适中（50-300字符）
   - 必须包含标签（#）增加曝光
   - 使用emoji增加亲和力
   - 常用列表、编号等结构化表达

3. 常用标签：
   - #眼镜 #眼镜搭配 #女生必备
   - #日常记录 #穿搭分享
   - 根据主题添加细分标签

4. 内容类型：
   - 教程攻略类（实用性强）
   - 穿搭分享类（视觉性强）
   - 日常记录类（真实性强）
   - 产品合集类（推荐性强）
    """)

    return notes

if __name__ == "__main__":
    json_file = Path("output/notes_女生眼镜推荐_20260106_090010_incremental.json")
    if json_file.exists():
        analyze_notes(json_file)
    else:
        print(f"文件不存在：{json_file}")
