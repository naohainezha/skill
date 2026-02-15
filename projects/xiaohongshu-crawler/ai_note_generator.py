"""
AI驱动的笔记生成器
使用GLM-4和Kimi K2模型
"""
import os
import json
import random
from pathlib import Path
from datetime import datetime
from ai_config import AIModelConfig

# 设置UTF-8编码输出
import sys
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class AIClient:
    """统一的AI模型客户端"""

    def __init__(self, usage_type):
        """初始化AI客户端

        Args:
            usage_type: 使用类型（采集阶段/数据分析/笔记生成/内容优化）
        """
        self.config = AIModelConfig.get_full_config(usage_type)
        self.usage_type = usage_type
        self.model = self.config['model']

    def chat(self, messages, **kwargs):
        """调用AI模型

        Args:
            messages: 对话消息列表
            **kwargs: 额外参数

        Returns:
            str: 模型回复
        """
        if not self.config['api_key']:
            return f"错误：未设置API密钥，无法调用{self.config['description']}"

        try:
            # 根据不同模型调用不同的API
            if "glm" in self.model.lower():
                return self._call_glm4(messages, **kwargs)
            elif "kimi" in self.model.lower():
                return self._call_kimi(messages, **kwargs)
            else:
                return f"错误：不支持的模型 {self.model}"

        except Exception as e:
            return f"错误：调用AI模型失败 - {str(e)}"

    def _call_glm4(self, messages, **kwargs):
        """调用GLM-4模型"""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.config['model'],
                "messages": messages,
                "temperature": kwargs.get('temperature', self.config['temperature']),
                "max_tokens": kwargs.get('max_tokens', self.config['max_tokens'])
            }

            response = requests.post(
                self.config['base_url'] + "chat/completions",
                headers=headers,
                json=data,
                timeout=self.config['timeout']
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"GLM-4 API错误: {response.status_code} - {response.text}"

        except ImportError:
            return "错误：需要安装requests库 (pip install requests)"
        except Exception as e:
            return f"GLM-4调用失败: {str(e)}"

    def _call_kimi(self, messages, **kwargs):
        """调用Kimi K2模型"""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.config['model'],
                "messages": messages,
                "temperature": kwargs.get('temperature', self.config['temperature']),
                "max_tokens": kwargs.get('max_tokens', self.config['max_tokens'])
            }

            response = requests.post(
                self.config['base_url'] + "/chat/completions",
                headers=headers,
                json=data,
                timeout=self.config['timeout']
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Kimi K2 API错误: {response.status_code} - {response.text}"

        except ImportError:
            return "错误：需要安装requests库 (pip install requests)"
        except Exception as e:
            return f"Kimi K2调用失败: {str(e)}"


class AIXHSNoteGenerator:
    """AI驱动的小红书笔记生成器"""

    def __init__(self, keyword, use_ai=True):
        """初始化生成器

        Args:
            keyword: 关键词
            use_ai: 是否使用AI生成（True=使用Kimi K2, False=使用模板）
        """
        self.keyword = keyword
        self.use_ai = use_ai

        if use_ai:
            # 使用Kimi K2进行数据分析和笔记生成
            self.analysis_client = AIClient("数据分析")
            self.generation_client = AIClient("笔记生成")
            print(f"✅ AI模式已启用，使用模型: {self.generation_client.model}")
        else:
            print("⚠️ 使用模板模式")

    def analyze_data(self, notes_data):
        """分析采集的笔记数据（使用Kimi K2）

        Args:
            notes_data: 采集的笔记数据列表

        Returns:
            dict: 分析结果
        """
        if not self.use_ai or not notes_data:
            return {"summary": "数据不足或AI未启用"}

        print("\n📊 正在使用Kimi K2分析笔记数据...")

        # 提取关键信息
        titles = [note.get('title', '') for note in notes_data[:5]]
        contents = [note.get('content', '')[:200] for note in notes_data[:3]]

        analysis_prompt = f"""分析以下小红书笔记数据，提取关键信息：

关键词: {self.keyword}

标题示例:
{chr(10).join([f"- {t}" for t in titles])}

内容摘要:
{chr(10).join([f"- {c}" for c in contents])}

请分析并返回JSON格式（不要有markdown标记）:
{{
  "popular_tags": ["标签1", "标签2", "标签3"],
  "common_themes": ["主题1", "主题2"],
  "tone": "语气风格（如：温柔/专业/活泼）",
  "target_audience": "目标人群",
  "key_features": ["特点1", "特点2", "特点3"],
  "pain_points": ["痛点1", "痛点2"]
}}
"""

        messages = [
            {"role": "system", "content": "你是一位小红书内容分析专家，擅长从笔记数据中提取关键信息和趋势。"},
            {"role": "user", "content": analysis_prompt}
        ]

        response = self.analysis_client.chat(messages)

        try:
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                analysis = json.loads(json_match.group())
                print("✅ 数据分析完成")
                return analysis
            else:
                print("⚠️ 分析结果格式异常，使用默认分析")
                return {"summary": response[:500]}
        except:
            print("⚠️ 解析分析结果失败，使用默认分析")
            return {"summary": response[:500]}

    def generate_note(self, analysis, note_type="经验分享"):
        """生成单篇笔记（使用Kimi K2）

        Args:
            analysis: 数据分析结果
            note_type: 笔记类型

        Returns:
            dict: 生成的笔记
        """
        print(f"\n📝 正在使用Kimi K2生成{note_type}笔记...")

        prompt = f"""基于以下分析结果，生成一篇小红书笔记：

关键词: {self.keyword}
笔记类型: {note_type}

数据分析:
{json.dumps(analysis, ensure_ascii=False, indent=2)}

要求:
1. 标题要吸引人，包含表情符号，15-25字
2. 内容要符合小红书风格，自然流畅，300-500字
3. 包含适当的表情符号和话题标签（#标签）
4. 语气要{analysis.get('tone', '温柔亲切')}
5. 针对的目标人群: {analysis.get('target_audience', '年轻女性')}
6. 解决的痛点: {', '.join(analysis.get('pain_points', ['选择困难', '不知道怎么选']))}
7. 突出特点: {', '.join(analysis.get('key_features', ['高颜值', '显脸小']))}

请返回JSON格式（不要有markdown标记）:
{{
  "title": "笔记标题",
  "content": "笔记内容",
  "tags": ["#标签1", "#标签2", "#标签3"]
}}
"""

        messages = [
            {"role": "system", "content": "你是一位小红书内容创作专家，擅长创作吸引人、有价值的笔记内容。"},
            {"role": "user", "content": prompt}
        ]

        response = self.generation_client.chat(messages)

        try:
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                note_data = json.loads(json_match.group())
                print("✅ 笔记生成完成")
                return {
                    "type": note_type,
                    "title": note_data.get('title', ''),
                    "content": note_data.get('content', ''),
                    "tags": note_data.get('tags', []),
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model": self.generation_client.model
                }
            else:
                print("⚠️ 生成结果格式异常")
                return {"error": "格式错误"}
        except Exception as e:
            print(f"⚠️ 解析生成结果失败: {e}")
            return {"error": str(e)}

    def generate_batch(self, notes_data, count=5):
        """批量生成笔记

        Args:
            notes_data: 采集的笔记数据
            count: 生成数量

        Returns:
            list: 生成的笔记列表
        """
        notes = []

        # 分析数据
        analysis = self.analyze_data(notes_data)

        # 笔记类型
        note_types = ["经验分享", "产品推荐", "使用教程", "穿搭分享", "避坑指南"]

        for i in range(count):
            note_type = note_types[i % len(note_types)]
            note = self.generate_note(analysis, note_type)
            if 'error' not in note:
                notes.append(note)

        return notes

    def save(self, notes, output_dir="output"):
        """保存生成的笔记

        Args:
            notes: 笔记列表
            output_dir: 输出目录
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = output_path / f"ai_generated_{self.keyword}_{timestamp}.json"
        txt_file = output_path / f"ai_generated_{self.keyword}_{timestamp}.txt"

        # 保存JSON格式
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

        # 保存文本格式
        with open(txt_file, 'w', encoding='utf-8') as f:
            for i, note in enumerate(notes, 1):
                f.write(f"\n{'='*60}\n")
                f.write(f"笔记 {i} - {note.get('type', '未分类')}\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"标题：{note.get('title', '')}\n\n")
                f.write(f"内容：\n{note.get('content', '')}\n\n")
                if 'tags' in note:
                    f.write(f"标签：{' '.join(note['tags'])}\n")
                f.write(f"生成时间：{note.get('generated_at', '')}\n")
                if 'model' in note:
                    f.write(f"使用模型：{note['model']}\n")

        print(f"\n✅ 已保存生成笔记：")
        print(f"   JSON: {json_file}")
        print(f"   TXT:  {txt_file}")

        return json_file, txt_file


def main():
    """主函数"""
    print("="*60)
    print("AI驱动的小红书笔记生成器")
    print("="*60)

    # 创建生成器（使用Kimi K2）
    generator = AIXHSNoteGenerator("眼镜框推荐女", use_ai=True)

    # 测试API密钥
    print("\n正在检查API配置...")
    if not generator.generation_client.config['api_key']:
        print("⚠️ 警告：未找到Kimi K2的API密钥")
        print("请设置环境变量：")
        print("  - MOONSHOT_API_KEY")
        print("  - 或 KIMI_API_KEY")
        return

    # 模拟采集数据（实际应从文件读取）
    sample_data = [
        {
            "title": "方圆脸女生必看！这3款眼镜框绝了",
            "content": "玳瑁色方圆框，韩系文艺范，显脸小",
            "likes": 5000,
            "author": "小红书达人"
        },
        {
            "title": "长中庭女生看过来！这款眼镜框让你颜值up up",
            "content": "玳瑁色镜框，清冷优雅，太阳穴凹陷消失",
            "likes": 3000,
            "author": "美妆博主"
        }
    ]

    print(f"\n使用示例数据生成笔记...")
    notes = generator.generate_batch(sample_data, count=5)

    # 显示结果
    print("\n" + "="*60)
    print("生成的笔记预览")
    print("="*60)

    for i, note in enumerate(notes, 1):
        print(f"\n【笔记{i} - {note.get('type', '未分类')}】")
        print(f"标题：{note.get('title', '')}")
        print(f"内容：{note.get('content', '')[:100]}...")
        print(f"模型：{note.get('model', 'N/A')}")

    # 保存文件
    if notes:
        generator.save(notes)
        print("\n✅ 笔记生成完成！")
    else:
        print("\n⚠️ 未生成任何笔记，请检查API配置")


if __name__ == "__main__":
    main()
