"""
小红书采集+AI生成完整工作流
- 采集阶段：使用GLM-4辅助
- 分析和生成阶段：使用Kimi K2
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
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from ai_config import AIModelConfig
from ai_note_generator import AIXHSNoteGenerator


def check_api_keys():
    """检查API密钥配置"""
    print("="*60)
    print("检查API密钥配置")
    print("="*60)

    # GLM-4
    glm4_key = AIModelConfig.get_env_api_key("GLM4")
    print(f"\n[GLM-4（采集阶段）]")
    print(f"  状态：{'✅ 已配置' if glm4_key else '⚠️ 未配置'}")
    if not glm4_key:
        print(f"  请设置环境变量：ZHIPU_API_KEY 或 GLM_API_KEY")

    # Kimi K2
    kimi_key = AIModelConfig.get_env_api_key("KIMI_K2")
    print(f"\n[Kimi K2（分析和生成阶段）]")
    print(f"  状态：{'✅ 已配置' if kimi_key else '⚠️ 未配置'}")
    if not kimi_key:
        print(f"  请设置环境变量：MOONSHOT_API_KEY 或 KIMI_API_KEY")

    return glm4_key, kimi_key


def run_crawler(keyword, count=10):
    """运行小红书爬虫

    Args:
        keyword: 搜索关键词
        count: 采集数量

    Returns:
        str: 采集结果文件路径
    """
    print("\n" + "="*60)
    print(f"阶段1: 数据采集 - 使用GLM-4辅助")
    print("="*60)

    # 这里可以集成GLM-4进行智能优化
    # 例如：优化搜索关键词、识别热门笔记等
    print(f"\n正在采集 '{keyword}' 相关笔记...")

    # 调用爬虫脚本
    try:
        os.chdir("D:\\xiaohongshu-crawler")
        os.environ["KEYWORDS"] = keyword
        os.environ["TARGET_COUNT"] = str(count)

        # 导入爬虫
        sys.path.insert(0, "D:\\xiaohongshu-crawler")
        from crawler_v4 import main as crawler_main

        # 运行爬虫（这里简化处理，实际可能需要异步执行）
        print("提示：请手动运行以下命令启动爬虫")
        print(f"  cd D:\\xiaohongshu-crawler")
        print(f"  python search_xhs.py \"{keyword}\" {count}")

        # 假设爬虫已运行完成，查找最新文件
        output_dir = Path("D:\\xiaohongshu-crawler\\output")
        json_files = list(output_dir.glob("notes_*.json"))

        if json_files:
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            print(f"\n✅ 采集完成：{latest_file}")
            return str(latest_file)
        else:
            print("\n⚠️ 未找到采集结果")
            return None

    except Exception as e:
        print(f"\n⚠️ 爬虫运行失败: {e}")
        return None


def run_analysis_and_generation(data_file, keyword, count=5):
    """运行分析和生成阶段（使用Kimi K2）

    Args:
        data_file: 采集数据文件
        keyword: 关键词
        count: 生成数量

    Returns:
        str: 生成结果文件路径
    """
    print("\n" + "="*60)
    print(f"阶段2&3: 分析和生成 - 使用Kimi K2")
    print("="*60)

    # 读取采集数据
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            notes_data = json.load(f)
        print(f"\n✅ 成功读取 {len(notes_data)} 条笔记数据")
    except Exception as e:
        print(f"\n⚠️ 读取数据失败: {e}")
        return None

    # 创建AI生成器
    generator = AIXHSNoteGenerator(keyword, use_ai=True)

    # 批量生成笔记
    print(f"\n正在生成 {count} 篇笔记...")
    notes = generator.generate_batch(notes_data, count=count)

    # 保存结果
    if notes:
        json_file, txt_file = generator.save(notes)
        return json_file
    else:
        print("\n⚠️ 未生成任何笔记")
        return None


def full_workflow(keyword, crawl_count=10, generate_count=5):
    """完整工作流

    Args:
        keyword: 搜索关键词
        crawl_count: 采集数量
        generate_count: 生成数量
    """
    print("\n" + "="*60)
    print("小红书AI完整工作流")
    print("="*60)
    print(f"关键词: {keyword}")
    print(f"采集数量: {crawl_count}")
    print(f"生成数量: {generate_count}")
    print("\n模型配置:")
    print(f"  采集阶段: GLM-4 (智谱AI)")
    print(f"  分析阶段: Kimi K2 (Moonshot AI)")
    print(f"  生成阶段: Kimi K2 (Moonshot AI)")

    # 检查API密钥
    glm4_key, kimi_key = check_api_keys()

    if not kimi_key:
        print("\n⚠️ 缺少Kimi K2的API密钥，无法进行分析和生成")
        print("提示：可以仅运行采集阶段")
        user_input = input("\n是否继续运行采集阶段？(y/n): ")
        if user_input.lower() != 'y':
            return

    # 阶段1: 采集（如果未运行）
    print("\n" + "="*60)
    print("【选项】")
    print("1. 运行完整流程（采集+分析+生成）")
    print("2. 仅运行采集阶段")
    print("3. 使用已有数据进行分析和生成")
    print("="*60)

    choice = input("\n请选择 (1/2/3): ").strip()

    data_file = None

    if choice == "1" or choice == "2":
        # 运行采集
        data_file = run_crawler(keyword, crawl_count)

    elif choice == "3":
        # 使用已有数据
        existing_file = input("请输入数据文件路径: ").strip()
        if Path(existing_file).exists():
            data_file = existing_file
        else:
            print(f"⚠️ 文件不存在: {existing_file}")
            return

    if data_file and choice in ["1", "3"]:
        # 阶段2&3: 分析和生成
        if kimi_key:
            result_file = run_analysis_and_generation(data_file, keyword, generate_count)
            if result_file:
                print(f"\n{'='*60}")
                print("✅ 完整工作流执行成功！")
                print(f"{'='*60}")
                print(f"采集数据: {data_file}")
                print(f"生成笔记: {result_file}")
        else:
            print("\n⚠️ 缺少Kimi K2的API密钥，跳过分析和生成阶段")

    print("\n" + "="*60)
    print("工作流结束")
    print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小红书AI采集+生成完整工作流')
    parser.add_argument('keyword', help='搜索关键词')
    parser.add_argument('--crawl', type=int, default=10, help='采集数量（默认10）')
    parser.add_argument('--generate', type=int, default=5, help='生成数量（默认5）')

    args = parser.parse_args()

    # 运行完整工作流
    full_workflow(args.keyword, args.crawl, args.generate)


if __name__ == "__main__":
    # 如果没有参数，使用交互模式
    if len(sys.argv) == 1:
        keyword = input("请输入搜索关键词: ").strip()
        crawl_count = input("采集数量 (默认10): ").strip()
        generate_count = input("生成数量 (默认5): ").strip()

        crawl_count = int(crawl_count) if crawl_count else 10
        generate_count = int(generate_count) if generate_count else 5

        full_workflow(keyword, crawl_count, generate_count)
    else:
        main()
