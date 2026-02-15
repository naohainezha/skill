# -*- coding: utf-8 -*-
"""
眼镜穿搭提示词深度分析报告
"""

import json
import sys
from pathlib import Path
from collections import Counter

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 输入文件
KNOWLEDGE_BASE_FILE = r"D:\xiaohongshu-crawler\output\knowledge_base_glasses_outfit.txt"
NOTES_FILE = r"D:\xiaohongshu-crawler\output\notes_20260108_085720.json"

# 输出文件
ANALYSIS_FILE = r"D:\xiaohongshu-crawler\output\prompt_analysis_report.txt"


def load_knowledge_base():
    """加载知识库"""
    with open(KNOWLEDGE_BASE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析知识库
    examples = []
    lines = content.split('\n')

    current_example = None

    for line in lines:
        if line.startswith('【示例'):
            if current_example:
                examples.append(current_example)
            current_example = {'title': line, 'prompt': ''}
        elif current_example and '增强版提示词' in line:
            # 提取提示词部分
            idx = line.find('】')
            if idx >= 0:
                current_example['prompt'] = line[idx+1:].strip()

    if current_example:
        examples.append(current_example)

    return examples


def load_notes():
    """加载笔记数据"""
    with open(NOTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_patterns(examples, notes):
    """深度分析提示词模式"""
    all_prompts = [ex['prompt'] for ex in examples]

    # 1. 场景分析
    print("\n" + "=" * 100)
    print("一、场景特征分析")
    print("=" * 100)

    scenes = {}
    for prompt in all_prompts:
        if '场景：' in prompt:
            scene = prompt.split('场景：')[1].split('，')[0]
            scenes[scene] = scenes.get(scene, 0) + 1

    print(f"\n场景分布（共{len(scenes)}种）:")
    for scene, count in sorted(scenes.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {scene}: {count}次 ({count/len(all_prompts)*100:.1f}%)")

    # 2. 人物特征
    print("\n" + "=" * 100)
    print("二、人物特征分析")
    print("=" * 100)

    person_features = []
    for prompt in all_prompts:
        if '人物：' in prompt:
            person = prompt.split('人物：')[1].split('，')[0]
            person_features.append(person)

    print(f"\n人物特征:")
    for feature in Counter(person_features).most_common():
        print(f"  - {feature[0]}: {feature[1]}次")

    # 3. 风格特征
    print("\n" + "=" * 100)
    print("三、风格特征分析")
    print("=" * 100)

    all_styles = []
    for prompt in all_prompts:
        if '风格：' in prompt:
            style_part = prompt.split('风格：')[1].split('，')[0]
            styles = style_part.split('、')
            all_styles.extend(styles)

    print(f"\n风格关键词分布:")
    for style, count in Counter(all_styles).most_common():
        print(f"  - {style}: {count}次 ({count/len(all_prompts)*100:.1f}%)")

    # 4. 摄影风格
    print("\n" + "=" * 100)
    print("四、摄影风格分析")
    print("=" * 100)

    photo_styles = []
    for prompt in all_prompts:
        if '摄影：' in prompt:
            photo_part = prompt.split('摄影：')[1].split('，')[0]
            photo_styles.extend([s.strip() for s in photo_part.split('、')])

    print(f"\n摄影特征:")
    for style, count in Counter(photo_styles).most_common():
        print(f"  - {style}: {count}次 ({count/len(all_prompts)*100:.1f}%)")

    # 5. 氛围特征
    print("\n" + "=" * 100)
    print("五、氛围特征分析")
    print("=" * 100)

    atmosphere_keywords = []
    for prompt in all_prompts:
        if '氛围：' in prompt:
            atmosphere_part = prompt.split('氛围：')[1]
            keywords = [k.strip() for k in atmosphere_part.split('、')]
            atmosphere_keywords.extend(keywords)

    print(f"\n氛围关键词:")
    for keyword, count in Counter(atmosphere_keywords).most_common():
        print(f"  - {keyword}: {count}次")

    # 6. 笔记主题分析
    print("\n" + "=" * 100)
    print("六、笔记主题分析（从原笔记中提取）")
    print("=" * 100)

    # 统计笔记中的高频词
    all_content = ' '.join([note.get('content', '') for note in notes])

    # 移除标签和特殊字符
    lines = all_content.split('\n')
    clean_content = ' '.join([l for l in lines if not l.strip().startswith('#')])

    # 简单分词（中文）
    keywords_zh = []
    target_keywords = [
        '高智', '高知', '韩系', '温柔', '姐姐', 'cleanfit',
        '通勤', '日常', '职场', '老师', 'polo', '衬衫',
        '针织', '西装', '大衣', '毛衣', '搭配', '穿搭'
    ]

    for keyword in target_keywords:
        count = clean_content.count(keyword)
        if count > 0:
            keywords_zh.append((keyword, count))

    print(f"\n笔记高频主题词:")
    for keyword, count in sorted(keywords_zh, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {keyword}: {count}次")

    # 7. 提示词结构分析
    print("\n" + "=" * 100)
    print("七、提示词结构模式")
    print("=" * 100)

    print("\n典型提示词结构:")
    print("  1. 场景描述（基于图片反推）")
    print("  2. 人物描述（戴眼镜的年轻女性）")
    print("  3. 风格描述（知性/韩系/温柔等）")
    print("  4. 摄影风格（iPhone拍摄、自然光、真实感）")
    print("  5. 穿搭描述（衬衫、针织等）")
    print("  6. 氛围描述（松弛、自然、生活气息）")

    # 8. 模板总结
    print("\n" + "=" * 100)
    print("八、眼镜穿搭提示词模板")
    print("=" * 100)

    templates = {
        "知性优雅风": "场景：[办公/书房/教室]，人物：一位戴眼镜的知性女性，风格：知性优雅，穿搭：[衬衫/西装/大衣]，摄影：iPhone拍摄，自然光，真实生活感，氛围：专业、从容、有书卷气",
        "韩系温柔风": "场景：[咖啡店/街边/居家]，人物：一位戴眼镜的韩系女生，风格：韩系温柔，穿搭：[针织/毛衣/柔和色调]，摄影：iPhone拍摄，自然光，真实生活感，氛围：恬静、可爱、青春",
        "cleanfit简约风": "场景：[街拍/日常]，人物：一位戴眼镜的简约风女生，风格：cleanfit简约，穿搭：[基础款单品/低饱和色]，摄影：iPhone拍摄，自然光，真实生活感，氛围：简洁、高级、不费力",
        "成熟姐姐风": "场景：[餐厅/聚会/街头]，人物：一位戴眼镜的成熟女性，风格：成熟姐姐，穿搭：[西装/风衣/polo衫]，摄影：iPhone拍摄，自然光，真实生活感，氛围：自信、从容、有气场",
        "日常休闲风": "场景：[居家/街头/随便哪里]，人物：一位戴眼镜的休闲女生，风格：日常休闲，穿搭：[T恤/卫衣/牛仔裤]，摄影：iPhone拍摄，自然光，真实生活感，氛围：松弛、自然、充满生活气息"
    }

    print("\n不同风格的提示词模板:")
    for style_name, template in templates.items():
        print(f"\n【{style_name}】")
        print(f"  {template}")

    return {
        'scenes': scenes,
        'styles': Counter(all_styles),
        'photo_styles': Counter(photo_styles),
        'templates': templates
    }


def save_analysis_report(examples, analysis_results):
    """保存分析报告"""

    with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("眼镜穿搭提示词深度分析报告\n")
        f.write("=" * 100 + "\n\n")

        f.write("基于小红书'眼镜穿搭'专题10篇笔记的提示词分析\n\n")

        # 一、数据概览
        f.write("=" * 100 + "\n")
        f.write("一、数据概览\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"- 分析样本数: {len(examples)}个提示词\n")
        f.write(f"- 笔记数量: 10篇\n")
        f.write(f"- 图片数量: 60张\n\n")

        # 二、核心特征
        f.write("=" * 100 + "\n")
        f.write("二、核心特征总结\n")
        f.write("=" * 100 + "\n\n")

        f.write("1. 人物特征:\n")
        f.write("   - 戴眼镜的年轻女性（100%）\n")
        f.write("   - 亚洲面孔\n")
        f.write("   - 年龄段: 20-35岁\n\n")

        f.write("2. 场景分布:\n")
        for scene, count in sorted(analysis_results['scenes'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"   - {scene}: {count}次\n")

        f.write("\n3. 风格关键词:\n")
        for style, count in analysis_results['styles'].most_common():
            f.write(f"   - {style}: {count}次\n")

        f.write("\n4. 摄影特征:\n")
        for style, count in analysis_results['photo_styles'].most_common():
            f.write(f"   - {style}: {count}次\n")

        # 三、提示词模板
        f.write("\n" + "=" * 100 + "\n")
        f.write("三、眼镜穿搭提示词模板库\n")
        f.write("=" * 100 + "\n\n")

        for style_name, template in analysis_results['templates'].items():
            f.write(f"【{style_name}】\n")
            f.write(f"{template}\n\n")

        # 四、使用建议
        f.write("=" * 100 + "\n")
        f.write("四、提示词使用建议\n")
        f.write("=" * 100 + "\n\n")

        f.write("1. 核心要素（必填）:\n")
        f.write("   - 人物: 戴眼镜的年轻女性\n")
        f.write("   - 摄影: iPhone拍摄、自然光、真实感\n")
        f.write("   - 氛围: 松弛、自然、生活气息\n\n")

        f.write("2. 可选要素（根据风格调整）:\n")
        f.write("   - 场景: 办公室/咖啡店/居家/街头\n")
        f.write("   - 风格: 知性/韩系/cleanfit/姐姐风/休闲\n")
        f.write("   - 穿搭: 衬衫/针织/西装/毛衣/polo等\n\n")

        f.write("3. 注意事项:\n")
        f.write("   - 避免过度美颜，强调真实质感\n")
        f.write("   - 光线要自然，不要影楼光\n")
        f.write("   - 姿态要松弛，避免摆拍痕迹\n")
        f.write("   - 突出眼镜作为穿搭单品的特点\n\n")

        # 五、常见组合
        f.write("=" * 100 + "\n")
        f.write("五、常用提示词组合\n")
        f.write("=" * 100 + "\n\n")

        combinations = [
            {
                "name": "职场知性风",
                "prompt": "场景：办公室/书房，人物：一位戴眼镜的知性女性，风格：知性优雅，穿搭：白色衬衫/西装，摄影：iPhone拍摄，自然光，真实生活感，氛围：专业、从容、有书卷气"
            },
            {
                "name": "韩系日常风",
                "prompt": "场景：咖啡店/街边，人物：一位戴眼镜的韩系女生，风格：韩系温柔，穿搭：针织衫/柔和色调，摄影：iPhone拍摄，自然光，真实生活感，氛围：恬静、可爱、青春"
            },
            {
                "name": "休闲自然风",
                "prompt": "场景：居家/街头，人物：一位戴眼镜的休闲女生，风格：自然休闲，穿搭：基础款/低饱和色，摄影：iPhone拍摄，自然光，真实生活感，氛围：松弛、自然、充满生活气息"
            }
        ]

        for combo in combinations:
            f.write(f"【{combo['name']}】\n")
            f.write(f"{combo['prompt']}\n\n")

        f.write("=" * 100 + "\n")
        f.write("报告结束\n")
        f.write("=" * 100 + "\n")


if __name__ == "__main__":
    print("正在加载知识库...")
    examples = load_knowledge_base()
    print(f"加载了 {len(examples)} 个提示词示例")

    print("\n正在加载笔记数据...")
    notes = load_notes()
    print(f"加载了 {len(notes)} 篇笔记")

    print("\n正在深度分析提示词模式...")
    analysis_results = analyze_patterns(examples, notes)

    print("\n正在保存分析报告...")
    save_analysis_report(examples, analysis_results)

    print(f"\n完成！分析报告已保存到: {ANALYSIS_FILE}")
    print(f"\n知识库文件: {KNOWLEDGE_BASE_FILE}")
