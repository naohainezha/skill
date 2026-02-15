"""
小红书完整工作流 - 采集 → 分析 → 生成
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


class XHSWorkflow:
    """小红书工作流管理器"""

    def __init__(self, keyword, count=5):
        self.keyword = keyword
        self.count = count
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def find_latest_notes(self):
        """查找最新采集的笔记"""
        pattern = f"notes_{self.keyword}_*incremental.json"
        files = list(self.output_dir.glob(pattern))

        if not files:
            print(f"❌ 未找到关键词'{self.keyword}'的采集笔记")
            print(f"   请先运行爬虫采集笔记：python crawler_v4.py")
            return None

        # 获取最新文件
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        print(f"✅ 找到最新采集笔记：{latest_file.name}")

        return latest_file

    def analyze_notes(self, notes_file):
        """分析采集的笔记"""
        print("\n" + "="*60)
        print("【第一步】分析采集笔记特点")
        print("="*60)

        with open(notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)

        analysis = {
            "note_count": len(notes),
            "title_length": [],
            "content_length": [],
            "use_emoji": 0,
            "use_tags": 0,
            "types": {"教程攻略": 0, "穿搭分享": 0, "日常记录": 0, "产品合集": 0}
        }

        for note in notes:
            title = note['title']
            content = note['content']

            analysis["title_length"].append(len(title))
            analysis["content_length"].append(len(content))

            # 检测emoji
            if any(ord(c) > 127 for c in title):
                analysis["use_emoji"] += 1

            # 检测标签
            if '#' in content:
                analysis["use_tags"] += 1

            # 分类
            text = title + content
            if any(word in text for word in ['攻略', '教程', '公式', '如何']):
                analysis["types"]["教程攻略"] += 1
            elif any(word in text for word in ['搭配', '穿搭', '韩系']):
                analysis["types"]["穿搭分享"] += 1
            elif any(word in text for word in ['日常', '记录', '阳光', '幸福']):
                analysis["types"]["日常记录"] += 1
            else:
                analysis["types"]["产品合集"] += 1

        # 显示分析结果
        print(f"\n📊 采集笔记数量：{analysis['note_count']}篇")
        print(f"📏 平均标题长度：{sum(analysis['title_length'])/len(analysis['title_length']):.1f}字符")
        print(f"📝 平均内容长度：{sum(analysis['content_length'])/len(analysis['content_length']):.0f}字符")
        print(f"😊 使用emoji比例：{analysis['use_emoji']}/{analysis['note_count']} ({analysis['use_emoji']/analysis['note_count']*100:.0f}%)")
        print(f"🏷️  使用标签比例：{analysis['use_tags']}/{analysis['note_count']} ({analysis['use_tags']/analysis['note_count']*100:.0f}%)")

        print(f"\n📚 笔记类型分布：")
        for note_type, count in analysis["types"].items():
            if count > 0:
                print(f"   - {note_type}：{count}篇")

        return analysis

    def generate_notes(self, analysis):
        """基于分析结果生成新笔记"""
        print("\n" + "="*60)
        print("【第二步】生成小红书笔记")
        print("="*60)

        # 导入生成器
        from generate_notes import XHSNoteGenerator

        generator = XHSNoteGenerator(self.keyword)
        notes = generator.generate(count=self.count)

        # 显示生成结果
        print(f"\n✨ 成功生成{len(notes)}篇笔记：\n")

        type_count = {}
        for note in notes:
            note_type = note['type']
            type_count[note_type] = type_count.get(note_type, 0) + 1

            print(f"【{note_type}】{note['title']}")
            print(f"   长度：{len(note['content'])}字符 | 标签：{note['content'].count('#')}个\n")

        print(f"📊 类型分布：{type_count}")

        # 保存文件
        json_file, txt_file = generator.save(notes)

        return notes, json_file, txt_file

    def test_quality(self, notes, analysis):
        """测试生成笔记的质量"""
        print("\n" + "="*60)
        print("【第三步】质量检测")
        print("="*60)

        passed = 0
        failed = 0

        for i, note in enumerate(notes, 1):
            issues = []

            # 检查标题长度
            title_len = len(note['title'])
            avg_title_len = sum(analysis['title_length']) / len(analysis['title_length'])
            if not (avg_title_len * 0.5 <= title_len <= avg_title_len * 1.5):
                issues.append(f"标题长度异常（{title_len}字符）")

            # 检查内容长度
            content_len = len(note['content'])
            avg_content_len = sum(analysis['content_length']) / len(analysis['content_length'])
            if not (avg_content_len * 0.3 <= content_len <= avg_content_len * 2):
                issues.append(f"内容长度异常（{content_len}字符）")

            # 检查标签
            if note['content'].count('#') < 3:
                issues.append("标签数量不足")

            # 检查emoji
            if not any(ord(c) > 127 for c in note['title']):
                issues.append("标题缺少emoji")

            if issues:
                failed += 1
                status = "❌ 未通过"
            else:
                passed += 1
                status = "✅ 通过"

            print(f"\n笔记{i}：{note['title'][:20]}...")
            print(f"  {status}")
            if issues:
                for issue in issues:
                    print(f"    - {issue}")

        # 总结
        print("\n" + "-"*60)
        print(f"质量检测完成：")
        print(f"  ✅ 通过：{passed}/{len(notes)} ({passed/len(notes)*100:.0f}%)")
        print(f"  ❌ 未通过：{failed}/{len(notes)} ({failed/len(notes)*100:.0f}%)")

        if passed == len(notes):
            print("\n🎉 所有笔记质量检测通过！")
        else:
            print("\n⚠️ 部分笔记需要优化")

    def run(self):
        """运行完整工作流"""
        print("\n" + "="*60)
        print("小红书笔记生成工作流")
        print("="*60)
        print(f"关键词：{self.keyword}")
        print(f"生成数量：{self.count}篇")
        print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 查找采集笔记
        notes_file = self.find_latest_notes()
        if not notes_file:
            return False

        # 2. 分析采集笔记
        analysis = self.analyze_notes(notes_file)

        # 3. 生成新笔记
        notes, json_file, txt_file = self.generate_notes(analysis)

        # 4. 质量检测
        self.test_quality(notes, analysis)

        # 完成
        print("\n" + "="*60)
        print("✅ 工作流完成！")
        print("="*60)
        print(f"\n生成的笔记已保存至：")
        print(f"  📄 JSON格式：{json_file}")
        print(f"  📝 文本格式：{txt_file}")

        return True


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="小红书笔记生成工作流")
    parser.add_argument("keyword", help="关键词（如：女生眼镜推荐）")
    parser.add_argument("-n", "--count", type=int, default=5, help="生成数量（默认5篇）")

    args = parser.parse_args()

    # 创建工作流
    workflow = XHSWorkflow(args.keyword, args.count)

    # 运行
    success = workflow.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
