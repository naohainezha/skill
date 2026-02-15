"""
AI绘画提示词生成器
基于小红书笔记生成AI绘画提示词
使用Kimi K2模型
"""
import sys
import json

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


def generate_image_prompts(notes):
    """使用Kimi K2生成AI绘画提示词

    Args:
        notes: 笔记列表

    Returns:
        list: 每篇笔记的AI绘画提示词列表
    """

    # 定义Kimi K2 API配置
    config = {
        "model": "kimi-k2",
        "api_key": "",  # 从环境变量读取
        "base_url": "https://api.moonshot.cn/v1",
        "temperature": 0.7,
        "max_tokens": 2000
    }

    # 尝试从环境变量获取API密钥
    import os
    api_key = os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_API_KEY")

    if not api_key:
        print("⚠️  警告：未找到Kimi K2的API密钥")
        print("   请设置环境变量：MOONSHOT_API_KEY 或 KIMI_API_KEY")
        print("\n使用默认提示词模板生成...")

        # 使用模板生成默认提示词
        return generate_default_prompts(notes)

    # 使用Kimi K2 API
    try:
        import requests

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        all_prompts = []

        for i, note in enumerate(notes, 1):
            prompt_text = f"""你是AI绘画提示词专家，擅长创作Flux和QwenImage的自然语言风格提示词。

任务：为以下小红书笔记生成3-5个AI绘画提示词（Flux/QwenImage风格）。

笔记标题：{note['title']}
笔记内容：{note['content']}

Flux/QwenImage提示词特点：
1. 使用自然语言段落式描述，不要用逗号分隔的关键词
2. 描述要详细生动，包含场景、人物动作、光线、氛围等
3. 中英文双版本
4. 符合小红书图片风格：温暖柔和的光线、自然清新的妆容、日常精致的穿搭

要求：
1. 生成3-5个AI绘画提示词
2. 每个提示词使用自然语言段落描述（不是关键词列表）
3. 包含：人物描述（亚洲年轻女性、气质）、眼镜描述（形状、颜色、材质）、穿搭描述（服装、颜色、风格）、场景描述（环境、光线、氛围）、拍摄角度、风格描述（高智感、韩系、清新、复古、治愈系）、画质要求（高清、光线柔和、细节丰富）
4. 中英文双版本
5. 适合Flux和QwenImage等AI绘画工具

请按以下格式输出：

【中文提示词1】
[详细的中文段落描述]

【英文提示词1】
[详细的英文段落描述]
"""

            data = {
                "model": config['model'],
                "messages": [
                    {"role": "system", "content": "你是一位专业的AI绘画提示词专家，擅长创作Flux和QwenImage风格的自然语言描述式提示词。"},
                    {"role": "user", "content": prompt_text}
                ],
                "temperature": config['temperature'],
                "max_tokens": config['max_tokens']
            }

            response = requests.post(
                config['base_url'] + "/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                all_prompts.append({
                    "note_index": i,
                    "note_title": note['title'],
                    "prompts": parse_prompts_flux(content),
                    "model": "Kimi K2 (Flux/QwenImage style)"
                })
                print(f"✅ 笔记{i} - {note['title'][:20]}... 提示词生成完成")
            else:
                print(f"⚠️  笔记{i} API调用失败: {response.status_code}")
                # 使用默认提示词
                all_prompts.append({
                    "note_index": i,
                    "note_title": note['title'],
                    "prompts": generate_default_prompt_for_note(note),
                    "model": "Default Template (Flux/QwenImage style)"
                })

        return all_prompts

    except ImportError:
        print("⚠️  警告：需要安装requests库")
        return generate_default_prompts(notes)
    except Exception as e:
        print(f"⚠️  警告：调用Kimi K2失败: {str(e)}")
        return generate_default_prompts(notes)


def parse_prompts_flux(content):
    """解析AI生成的提示词（Flux/QwenImage风格）

    Args:
        content: AI返回的内容

    Returns:
        list: 提示词列表（中英文双版本）
    """
    prompts = []
    lines = content.split('\n')

    current_prompt = {"zh": "", "en": ""}
    for line in lines:
        line = line.strip()
        
        if line.startswith('【中文提示词'):
            # 保存上一个提示词
            if current_prompt["zh"] or current_prompt["en"]:
                prompts.append(current_prompt.copy())
            # 开始新提示词
            current_prompt = {"zh": "", "en": ""}
        elif line.startswith('【英文提示词'):
            # 继续当前提示词的英文部分
            continue
        elif line.startswith('【'):
            # 新提示词的开始
            if current_prompt["zh"] or current_prompt["en"]:
                prompts.append(current_prompt.copy())
            current_prompt = {"zh": "", "en": ""}
        elif not line.startswith('【'):
            # 内容行
            if 'zh' in current_prompt and current_prompt["zh"] == "":
                current_prompt["zh"] = line
            elif 'en' in current_prompt and current_prompt["en"] == "":
                current_prompt["en"] = line
            elif current_prompt["zh"] and not current_prompt["en"]:
                current_prompt["zh"] += " " + line
            elif current_prompt["en"] and not current_prompt["zh"]:
                current_prompt["en"] += " " + line
    
    # 添加最后一个提示词
    if current_prompt["zh"] or current_prompt["en"]:
        prompts.append(current_prompt.copy())

    return prompts


def generate_default_prompt_for_note(note):
    """为单篇笔记生成默认提示词（Flux/QwenImage风格，段落式）

    Args:
        note: 笔记数据

    Returns:
        list: 提示词列表（包含中文和英文版本）
    """
    title = note['title']
    content = note['content']

    # 根据笔记类型生成不同提示词
    if '穿搭' in title or '公式' in title:
        return [
            {
                "zh": "一张来自小红书的穿搭照片，展示一位亚洲年轻女性戴着黑色大框眼镜，穿着一件简洁的白色衬衫，搭配深色西装裤，站在明亮的办公室环境中。她的妆容自然清新，表情自信干练，散发出一种职业又不失亲和力的氛围。拍摄角度是正面半身像，光线柔和自然，画面清晰细腻，细节丰富，具有典型的小红书生活美学风格。",
                "en": "A Xiaohongshu-style fashion photo featuring an Asian young woman wearing black wide-frame glasses and a simple white shirt paired with dark suit trousers. She stands in a bright office environment with naturally fresh makeup and a confident yet approachable expression, radiating a professional yet friendly atmosphere. The photo is a front three-quarter shot with soft natural lighting, clear and delicate details, and rich textures, embodying the typical Xiaohongshu lifestyle aesthetic."
            },
            {
                "zh": "温馨的咖啡店场景，一位亚洲年轻女性坐在木质桌前，她佩戴着一副圆形的金属丝眼镜，身上穿着米白色的针织上衣，搭配牛仔裤。她手里端着一杯拿铁咖啡，脸上带着温柔的微笑，侧脸角度完美。光线温暖柔和，营造出舒适的氛围，画面细节丰富，具有治愈系的小红书风格。",
                "en": "A cozy café scene showing an Asian young woman sitting at a wooden table wearing round gold-wire glasses, dressed in a beige knit shirt paired with jeans. She holds a latte coffee cup with a gentle smile, captured at a perfect side profile angle. The warm and soft lighting creates a comfortable atmosphere with rich details, embodying the healing Xiaohongshu style."
            },
            {
                "zh": "户外周末休闲场景，一位亚洲年轻女性穿着宽松的连帽衫，戴着一副简约的半框眼镜，站在阳光明媚的街道上。她的妆容清新自然，表情轻松惬意，展现着青春活力的状态。拍摄角度是全身或大半身，光线自然明亮，画面清新自然，具有小红书年轻感的生活美学。",
                "en": "An outdoor weekend leisure scene featuring an Asian young woman in an oversized hoodie wearing simple semi-rimless glasses, standing on a sunlit street. Her makeup is fresh and natural, with a relaxed expression showing youthful vitality. The photo is a full or three-quarter shot with bright natural lighting and a fresh, natural composition, embodying the youthful Xiaohongshu lifestyle aesthetic."
            }
        ]
    elif '脸型' in title or '本命眼镜' in title:
        return [
            {
                "zh": "一张小红书风格的人像摄影作品，展示一位圆脸的亚洲年轻女性，她戴着黑色的方框眼镜，眼镜的棱角感很好地修饰了她的脸型，让脸看起来更小更精致。她的妆容精致但不夸张，眼神明亮有神，背景是干净的摄影棚。光线柔和均匀，画面细节丰富，8K高画质，超写实风格。",
                "en": "A Xiaohongshu-style portrait photograph showcasing an Asian young woman with a round face wearing black square-frame glasses. The angular design of the glasses perfectly contours her face shape, making it appear smaller and more refined. Her makeup is sophisticated but not excessive, with bright and spirited eyes against a clean studio background. The soft and even lighting produces rich details in 8K ultra-high definition with a photorealistic style."
            },
            {
                "zh": "优雅的氛围照片，一位方脸的亚洲年轻女性佩戴圆形的金属丝眼镜，金丝框的精致感提升了整体的气质。她的妆容优雅得体，表情温和自信，背景是简约的室内空间。光线自然柔和，画面4K超写实，细节清晰，营造出一种精致优雅的美感。",
                "en": "An elegant atmospheric photograph featuring a square-faced Asian young woman wearing round metal wire glasses. The delicate gold-wire frame enhances the overall sophistication. Her makeup is elegant and appropriate, with a gentle and confident expression set against a minimalist interior space. The natural soft lighting produces 4K photorealistic images with clear details, creating a refined and elegant aesthetic."
            },
            {
                "zh": "潮流时尚的照片，一位鹅蛋脸的亚洲年轻女性戴着玳瑁色的眼镜，站在户外的自然环境中。她的造型时尚个性，妆容精致而不夸张，笑容灿烂自然。光线明亮柔和，画面高画质，细节丰富，展现出一种潮流时尚的生活态度。",
                "en": "A trendy fashion photograph showing an oval-faced Asian young woman wearing tortoise-shell glasses in an outdoor natural environment. Her styling is fashionable and individual, with exquisite yet not excessive makeup and a bright natural smile. The bright and soft lighting creates high-quality images with rich details, showcasing a trendy and fashionable lifestyle attitude."
            }
        ]
    elif '场景' in title or '氛围' in title or '咖啡店' in title:
        return [
            {
                "zh": "氛围感十足的咖啡店照片，一位亚洲年轻女性穿着米白色的针织衫，戴着圆形的金丝眼镜，在咖啡店拿着咖啡杯，侧颜的角度。温暖的光线透过窗户洒在她身上，营造出梦幻而温馨的氛围。她的表情温柔治愈，画面细节丰富，8K高画质，具有小红书氛围感。",
                "en": "An atmospheric café photograph showing an Asian young woman in a beige knit shirt wearing round gold-wire glasses at a coffee shop, holding a coffee cup at a side profile angle. Warm sunlight filters through the window illuminating her, creating a dreamy and cozy atmosphere. Her expression is gentle and healing with rich details in 8K high definition, full of atmospheric vibes."
            },
            {
                "zh": "图书馆场景的高智感照片，一位亚洲年轻女性穿着白衬衫，戴着黑色的半框眼镜，在图书馆的书架前学习。她的表情专注而沉稳，眼镜增添了知性的气质。背景是整齐的书架和学习环境，光线柔和明亮，画面4K超写实，细节清晰，展现出一种静谧专注的学习氛围。",
                "en": "An intelligent-vibe library scene photograph featuring an Asian young woman in a white shirt and black semi-rimless glasses, studying in front of bookshelves in a library. Her expression is focused and composed, with the glasses adding an intellectual touch. The background features neatly arranged bookshelves and a study environment with soft bright lighting, producing 4K photorealistic images with clear details, showcasing a quiet and focused learning atmosphere."
            },
            {
                "zh": "逛街的治愈系照片，一位亚洲年轻女性穿着碎花连衣裙，戴着玳瑁色的眼镜，走在购物街上。她的笑容灿烂自然，充满生活气息。阳光洒在身上，光线明亮柔和，街道的背景干净整洁。画面8K高画质，细节丰富，营造出一种轻松愉快的周末逛街氛围。",
                "en": "A healing weekend shopping photograph showing an Asian young woman in a floral dress wearing tortoise-shell glasses walking along a shopping street. Her bright and natural smile is full of life and energy. Sunlight illuminates her with bright and soft lighting against a clean and tidy street background. The 8K high-quality image with rich details creates a relaxed and pleasant weekend shopping atmosphere."
            }
        ]
    else:
        return [
            {
                "zh": "一张来自小红书的日常穿搭照片，一位亚洲年轻女性戴着一副时尚的眼镜，背景是简约的室内空间。她的妆容自然清新，表情亲切温和，给人舒适治愈的感觉。光线柔和自然，画面4K高画质，细节清晰，具有典型的小红书生活美学风格。",
                "en": "A daily outfit photograph from Xiaohongshu featuring an Asian young woman wearing fashionable glasses against a minimalist interior background. Her makeup is naturally fresh with a kind and gentle expression that creates a comfortable and healing feeling. The soft natural lighting produces 4K high-quality images with clear details, embodying the typical Xiaohongshu lifestyle aesthetic."
            },
            {
                "zh": "户外休闲场景照片，一位亚洲年轻女性戴着时尚的眼镜，站在户外背景中。她的造型时尚个性，妆容精致而自然，表情轻松自然。光线明亮柔和，画面高画质，8K高清，清新自然的生活美学。",
                "en": "An outdoor casual scene photograph featuring an Asian young woman with stylish glasses in an outdoor background. Her styling is fashionable and individual with exquisite yet natural makeup and a relaxed natural expression. The bright and soft lighting creates high-quality images in 8K high definition, fresh and natural lifestyle aesthetic."
            },
            {
                "zh": "高级感的室内摄影照片，一位亚洲年轻女性戴着精致的眼镜，在摄影棚的专业灯光下拍摄。她的妆容精致高级，表情优雅自信，背景是简约而高级的室内空间。光线专业均匀，画面4K超写实，细节丰富，营造出一种高级精致的美学感。",
                "en": "A premium interior studio photograph featuring an Asian young woman wearing exquisite glasses under professional studio lighting. Her makeup is sophisticated and premium with an elegant and confident expression set against a minimalist yet high-end interior space. The professional and even lighting produces 4K photorealistic images with rich details, creating a refined and elegant aesthetic."
            }
        ]


def generate_default_prompts(notes):
    """生成默认提示词模板

    Args:
        notes: 笔记列表

    Returns:
        list: 默认提示词列表
    """
    all_prompts = []

    for i, note in enumerate(notes, 1):
        prompts = generate_default_prompt_for_note(note)
        all_prompts.append({
            "note_index": i,
            "note_title": note['title'],
            "prompts": prompts,
            "model": "Default Template (Flux/QwenImage style)"
        })

    return all_prompts


def save_prompts(prompts_data, output_dir="output"):
    """保存AI绘画提示词（Flux/QwenImage风格）

    Args:
        prompts_data: 提示词数据列表
        output_dir: 输出目录
    """
    from pathlib import Path
    from datetime import datetime

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = output_path / f"image_prompts_{timestamp}.json"
    txt_file = output_path / f"image_prompts_{timestamp}.txt"

    # 保存JSON格式
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)

    # 保存文本格式（Flux/QwenImage风格）
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("AI绘画提示词 - Xiaohongshu Notes (Flux/QwenImage风格)\n")
        f.write("="*60 + "\n")
        f.write("风格：自然语言段落式描述\n")
        f.write("适用：Flux / QwenImage / Midjourney v6\n")
        f.write("="*60 + "\n\n")

        for item in prompts_data:
            f.write("笔记 " + "="*56 + "\n")
            f.write(f"标题：{item['note_title']}\n")
            f.write(f"使用模型：{item['model']}\n")
            f.write("-"*60 + "\n\n")

            for i, prompt_dict in enumerate(item['prompts'], 1):
                f.write(f"【提示词 {i}】\n\n")
                
                if isinstance(prompt_dict, dict):
                    # 中英文双版本
                    if 'zh' in prompt_dict:
                        f.write("中文版（Flux/QwenImage）:\n")
                        f.write(f"{prompt_dict['zh']}\n\n")
                    
                    if 'en' in prompt_dict:
                        f.write("英文版（适用于Midjourney等）：\n")
                        f.write(f"{prompt_dict['en']}\n\n")
                else:
                    # 单一版本
                    f.write(f"{prompt_dict}\n\n")

            f.write("="*60 + "\n\n")

    print(f"\n✅ 已保存AI绘画提示词（Flux/QwenImage风格）：")
    print(f"   JSON: {json_file}")
    print(f"   TXT:  {txt_file}")

    return json_file, txt_file


def main():
    """主函数"""
    # 读取生成的笔记
    notes_file = "D:\\xiaohongshu-crawler\\output\\kimi_generated_notes_眼镜穿搭.json"

    try:
        with open(notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)

        print("="*60)
        print("AI绘画提示词生成器 (Flux/QwenImage风格)")
        print("="*60)
        print(f"\n读取笔记文件: {notes_file}")
        print(f"笔记数量: {len(notes)}\n")

        print("正在使用Kimi K2生成AI绘画提示词...\n")

        # 生成提示词
        prompts_data = generate_image_prompts(notes)

        # 保存结果
        save_prompts(prompts_data, "D:\\xiaohongshu-crawler\\output")

        print("\n✅ AI绘画提示词生成完成！")
        print(f"   总提示词数: {sum(len(item['prompts']) for item in prompts_data)}")
        print(f"   覆盖笔记数: {len(prompts_data)}")
        print(f"\n特点：")
        print("   - 自然语言段落式描述（不是关键词列表）")
        print("   - 适合Flux和QwenImage")
        print("   - 中英文双版本")
        print("   - 符合小红书图片风格")

    except FileNotFoundError:
        print(f"⚠️  错误：找不到笔记文件 {notes_file}")
        print("   请先运行笔记生成流程")
    except Exception as e:
        print(f"⚠️  错误：{str(e)}")


if __name__ == "__main__":
    main()
